"""
CoinDCX Futures Utility Functions
Common helper functions for trading operations
"""

from app.exchanges.coindcx.client import CoinDCXFutures, OrderSide, OrderType, TimeInForce
import time


def get_current_price(client, pair):
    """
    Get current market price from recent trades or orderbook

    Args:
        client: CoinDCXFutures client instance
        pair: Trading pair (e.g., 'B-ETH_USDT')

    Returns:
        float: Current market price
    """
    # Try orderbook first
    try:
        orderbook = client.get_orderbook(pair, depth=5)
        if orderbook and orderbook.get('bids') and orderbook.get('asks'):
            bids = orderbook['bids']
            asks = orderbook['asks']
            if bids and asks:
                best_bid = float(list(bids.keys())[0])
                best_ask = float(list(asks.keys())[0])
                return (best_bid + best_ask) / 2
    except Exception:
        pass

    # Fallback to recent trades
    trades = client.get_trades(pair)
    if trades and len(trades) > 0:
        return float(trades[0]['price'])

    raise ValueError(f"Cannot fetch price for {pair}")


def find_position_leverage(client, pair):
    """
    Find the required leverage for a trading pair
    Tests common leverage values to find which one works

    Args:
        client: CoinDCXFutures client instance
        pair: Trading pair (e.g., 'B-ETH_USDT')

    Returns:
        int: Correct leverage value, or None if no position exists
    """
    leverage_values = [1, 2, 3, 5, 10, 20]

    for lev in leverage_values:
        try:
            # Try to place a small test order
            order = client.place_order(
                pair=pair,
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT_ORDER,
                quantity=0.001,  # Minimum quantity
                price=1000,      # Very low price (won't fill)
                leverage=lev,
                margin_currency="INR",
                position_margin_type="isolated"
            )

            # If successful, this is the correct leverage
            order_id = order[0]['id']

            # Cancel the test order
            try:
                client.cancel_order(order_id)
            except:
                pass

            return lev

        except Exception as e:
            error_msg = str(e)
            if "leverage" in error_msg.lower():
                continue  # Try next leverage
            else:
                # Different error, might be balance or other issue
                return None

    return None


def calculate_margin_required(quantity, price, leverage):
    """
    Calculate margin required for a position

    Args:
        quantity: Order quantity
        price: Order price
        leverage: Leverage multiplier

    Returns:
        float: Margin required in INR
    """
    position_value = quantity * price
    margin = position_value / leverage
    return margin


def validate_order_params(client, pair, quantity, price=None, leverage=1):
    """
    Validate order parameters against instrument limits

    Args:
        client: CoinDCXFutures client instance
        pair: Trading pair
        quantity: Order quantity
        price: Order price (optional)
        leverage: Leverage multiplier

    Returns:
        dict: Validation result with 'valid' boolean and 'errors' list
    """
    errors = []

    try:
        # Get instrument details
        details = client.get_instrument_details(pair)
        inst = details['instrument']

        # Check quantity
        if quantity < inst['min_trade_size']:
            errors.append(f"Quantity below minimum: {inst['min_trade_size']}")

        if quantity > inst['max_quantity']:
            errors.append(f"Quantity above maximum: {inst['max_quantity']}")

        # Check leverage
        if leverage > inst['max_leverage_long']:
            errors.append(f"Leverage above maximum: {inst['max_leverage_long']}")

        # Check price
        if price:
            if price < inst['min_price']:
                errors.append(f"Price below minimum: {inst['min_price']}")

            if price > inst['max_price']:
                errors.append(f"Price above maximum: {inst['max_price']}")

        # Check notional value
        order_price = price or get_current_price(client, pair)
        notional = quantity * order_price

        if notional < inst['min_notional']:
            errors.append(f"Order value below minimum: {inst['min_notional']}")

        if notional > inst['max_notional']:
            errors.append(f"Order value above maximum: {inst['max_notional']}")

    except Exception as e:
        errors.append(f"Validation error: {str(e)}")

    return {
        'valid': len(errors) == 0,
        'errors': errors
    }


def place_order_with_retry(client, max_retries=3, retry_delay=2, **order_params):
    """
    Place order with automatic retry on transient errors

    Args:
        client: CoinDCXFutures client instance
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        **order_params: Order parameters to pass to place_order()

    Returns:
        dict: Order response
    """
    last_error = None

    for attempt in range(max_retries):
        try:
            order = client.place_order(**order_params)
            return order

        except Exception as e:
            last_error = e
            error_msg = str(e)

            # Don't retry on these errors
            if any(x in error_msg.lower() for x in ['leverage', 'balance', 'insufficient']):
                raise

            # Retry on server errors
            if '500' in error_msg or '503' in error_msg:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue

            # Don't retry on other errors
            raise

    raise last_error


def get_position_pnl(client, pair):
    """
    Get current PnL for a position

    Args:
        client: CoinDCXFutures client instance
        pair: Trading pair

    Returns:
        dict: Position details with PnL, or None if no position
    """
    positions = client.get_positions()

    for pos in positions:
        if pos.pair == pair and pos.active_pos != 0:
            current_price = get_current_price(client, pair)

            # Calculate unrealized PnL
            if pos.active_pos > 0:  # Long position
                pnl = (current_price - pos.avg_price) * abs(pos.active_pos)
            else:  # Short position
                pnl = (pos.avg_price - current_price) * abs(pos.active_pos)

            pnl_percent = (pnl / pos.locked_margin) * 100

            return {
                'pair': pos.pair,
                'size': pos.active_pos,
                'entry_price': pos.avg_price,
                'current_price': current_price,
                'unrealized_pnl': pnl,
                'pnl_percent': pnl_percent,
                'margin': pos.locked_margin,
                'liquidation_price': pos.liquidation_price
            }

    return None


def set_stop_loss_percent(client, pair, stop_loss_percent=5):
    """
    Set stop loss at percentage below entry price

    Args:
        client: CoinDCXFutures client instance
        pair: Trading pair
        stop_loss_percent: Stop loss percentage below entry (default 5%)

    Returns:
        bool: True if stop loss was set
    """
    positions = client.get_positions()

    for pos in positions:
        if pos.pair == pair and pos.active_pos != 0:
            # Calculate stop loss price
            if pos.active_pos > 0:  # Long position
                stop_loss_price = pos.avg_price * (1 - stop_loss_percent / 100)
            else:  # Short position
                stop_loss_price = pos.avg_price * (1 + stop_loss_percent / 100)

            # Set stop loss
            client.set_position_tpsl(
                position_id=pos.id,
                stop_loss_price=stop_loss_price
            )

            print(f"✓ Stop loss set at ₹{stop_loss_price:,.2f} ({stop_loss_percent}% from entry)")
            return True

    print(f"No active position found for {pair}")
    return False


def check_liquidation_risk(client):
    """
    Check all positions for liquidation risk

    Args:
        client: CoinDCXFutures client instance

    Returns:
        list: List of positions at risk (< 20% from liquidation)
    """
    positions = client.get_positions()
    at_risk = []

    for pos in positions:
        if pos.active_pos != 0:
            try:
                current_price = get_current_price(client, pos.pair)

                # Calculate distance to liquidation
                if pos.active_pos > 0:  # Long position
                    distance = (current_price - pos.liquidation_price) / current_price
                else:  # Short position
                    distance = (pos.liquidation_price - current_price) / current_price

                risk_percent = distance * 100

                if risk_percent < 20:  # Less than 20% away
                    at_risk.append({
                        'pair': pos.pair,
                        'current_price': current_price,
                        'liquidation_price': pos.liquidation_price,
                        'risk_percent': risk_percent,
                        'position': pos
                    })
            except Exception as e:
                print(f"Error checking {pos.pair}: {e}")

    return at_risk


def get_account_summary(client):
    """
    Get summary of account status

    Args:
        client: CoinDCXFutures client instance

    Returns:
        dict: Account summary
    """
    # Get positions
    positions = client.get_positions()
    active_positions = [p for p in positions if p.active_pos != 0]

    # Get open orders
    open_orders = client.get_orders(status="open")

    # Calculate total exposure
    total_margin = sum(pos.locked_margin for pos in active_positions)

    # Get recent trades
    try:
        recent_trades = client.get_trade_history(size=5)
    except:
        recent_trades = []

    return {
        'total_positions': len(active_positions),
        'open_orders': len(open_orders),
        'total_margin_used': total_margin,
        'positions': active_positions,
        'orders': open_orders,
        'recent_trades': recent_trades
    }


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = CoinDCXFutures()

    # Get current ETH price
    pair = "B-ETH_USDT"
    price = get_current_price(client, pair)
    print(f"Current {pair}: ₹{price:,.2f}")

    # Calculate margin for 0.1 ETH with 3x leverage
    margin = calculate_margin_required(0.1, price, 3)
    print(f"Margin required for 0.1 ETH (3x): ₹{margin:,.2f}")

    # Validate order parameters
    validation = validate_order_params(client, pair, 0.1, price, 3)
    if validation['valid']:
        print("✓ Order parameters valid")
    else:
        print("✗ Validation errors:")
        for error in validation['errors']:
            print(f"  - {error}")

    # Get account summary
    summary = get_account_summary(client)
    print(f"\nAccount Summary:")
    print(f"  Active positions: {summary['total_positions']}")
    print(f"  Open orders: {summary['open_orders']}")
    print(f"  Total margin: ₹{summary['total_margin_used']:,.2f}")
