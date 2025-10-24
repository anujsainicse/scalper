"""
Analytics Service for calculating trading performance metrics
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from app.models.bot import Bot, BotStatus
from app.models.order import Order, OrderStatus
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for calculating analytics and performance metrics"""

    @staticmethod
    def get_date_filter(date_range: str) -> Optional[datetime]:
        """
        Get datetime filter based on date range string

        Args:
            date_range: '1D', '1W', '1M', '3M', or 'ALL'

        Returns:
            datetime cutoff or None for ALL
        """
        now = datetime.utcnow()
        range_map = {
            '1D': timedelta(days=1),
            '1W': timedelta(weeks=1),
            '1M': timedelta(days=30),
            '3M': timedelta(days=90),
            'ALL': None,
        }

        delta = range_map.get(date_range)
        return (now - delta) if delta else None

    @staticmethod
    async def get_portfolio_metrics(
        db: AsyncSession,
        date_range: str = 'ALL'
    ) -> Dict[str, Any]:
        """
        Calculate overall portfolio metrics

        Returns:
            Dict with totalPnL, totalTrades, activeBots, etc.
        """
        try:
            # Get all bots
            bots_result = await db.execute(select(Bot))
            bots = bots_result.scalars().all()

            # Calculate metrics
            total_pnl = sum(bot.pnl or 0 for bot in bots)
            total_trades = sum(bot.total_trades or 0 for bot in bots)
            active_bots = sum(1 for bot in bots if bot.status == BotStatus.ACTIVE)

            # Get date filter
            date_filter = AnalyticsService.get_date_filter(date_range)

            # Calculate total volume for date range
            volume_query = select(func.sum(Order.quantity * Order.price))
            if date_filter:
                volume_query = volume_query.where(Order.created_at >= date_filter)
            volume_result = await db.execute(volume_query)
            total_volume = volume_result.scalar() or 0

            # Calculate win rate
            if date_filter:
                filled_orders = await db.execute(
                    select(Order).where(
                        and_(
                            Order.status == OrderStatus.FILLED,
                            Order.created_at >= date_filter
                        )
                    )
                )
            else:
                filled_orders = await db.execute(
                    select(Order).where(Order.status == OrderStatus.FILLED)
                )

            orders = filled_orders.scalars().all()

            # Simple win rate calculation (trades with positive PnL)
            profitable_trades = sum(1 for order in orders if (order.filled_price or 0) > 0)
            win_rate = (profitable_trades / len(orders) * 100) if len(orders) > 0 else 0

            avg_trade_value = total_volume / total_trades if total_trades > 0 else 0

            return {
                "totalPnL": float(total_pnl),
                "totalTrades": total_trades,
                "activeBots": active_bots,
                "totalVolume": float(total_volume),
                "winRate": round(win_rate, 2),
                "avgTradeValue": round(float(avg_trade_value), 2),
            }

        except Exception as e:
            logger.error(f"Error calculating portfolio metrics: {e}")
            return {
                "totalPnL": 0.0,
                "totalTrades": 0,
                "activeBots": 0,
                "totalVolume": 0.0,
                "winRate": 0.0,
                "avgTradeValue": 0.0,
            }

    @staticmethod
    async def get_performance_metrics(
        db: AsyncSession,
        date_range: str = 'ALL'
    ) -> Dict[str, Any]:
        """
        Calculate detailed performance metrics

        Returns:
            Dict with winRate, profitFactor, sharpeRatio, maxDrawdown, etc.
        """
        try:
            # Get date filter
            date_filter = AnalyticsService.get_date_filter(date_range)

            # Get all filled orders for date range
            if date_filter:
                orders_result = await db.execute(
                    select(Order).where(
                        and_(
                            Order.status == OrderStatus.FILLED,
                            Order.created_at >= date_filter
                        )
                    ).order_by(Order.created_at.asc())
                )
            else:
                orders_result = await db.execute(
                    select(Order).where(Order.status == OrderStatus.FILLED)
                    .order_by(Order.created_at.asc())
                )

            orders = orders_result.scalars().all()

            if not orders:
                return {
                    "winRate": 0.0,
                    "profitFactor": 0.0,
                    "sharpeRatio": 0.0,
                    "maxDrawdown": 0.0,
                    "avgTradePnL": 0.0,
                    "bestTrade": 0.0,
                    "worstTrade": 0.0,
                    "totalProfitableTrades": 0,
                    "totalLosingTrades": 0,
                }

            # Calculate PnL for each trade (simplified - actual PnL calculated differently)
            profitable_trades = []
            losing_trades = []
            all_pnls = []

            for order in orders:
                # Simplified PnL calculation
                pnl = float(order.filled_price or 0) - float(order.price)
                all_pnls.append(pnl)

                if pnl > 0:
                    profitable_trades.append(pnl)
                elif pnl < 0:
                    losing_trades.append(abs(pnl))

            # Win rate
            win_rate = (len(profitable_trades) / len(orders) * 100) if orders else 0

            # Profit factor (gross profit / gross loss)
            gross_profit = sum(profitable_trades) if profitable_trades else 0
            gross_loss = sum(losing_trades) if losing_trades else 1  # Avoid division by zero
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

            # Average trade PnL
            avg_trade_pnl = sum(all_pnls) / len(all_pnls) if all_pnls else 0

            # Best and worst trades
            best_trade = max(all_pnls) if all_pnls else 0
            worst_trade = min(all_pnls) if all_pnls else 0

            # Max drawdown (simplified)
            cumulative_pnl = []
            running_total = 0
            for pnl in all_pnls:
                running_total += pnl
                cumulative_pnl.append(running_total)

            max_drawdown = 0
            if cumulative_pnl:
                peak = cumulative_pnl[0]
                for value in cumulative_pnl:
                    if value > peak:
                        peak = value
                    drawdown = peak - value
                    if drawdown > max_drawdown:
                        max_drawdown = drawdown

            # Sharpe ratio (simplified - would need risk-free rate in production)
            if all_pnls:
                import statistics
                mean_return = statistics.mean(all_pnls)
                std_dev = statistics.stdev(all_pnls) if len(all_pnls) > 1 else 1
                sharpe_ratio = (mean_return / std_dev) if std_dev > 0 else 0
            else:
                sharpe_ratio = 0

            return {
                "winRate": round(win_rate, 2),
                "profitFactor": round(profit_factor, 2),
                "sharpeRatio": round(sharpe_ratio, 2),
                "maxDrawdown": round(float(max_drawdown), 2),
                "avgTradePnL": round(float(avg_trade_pnl), 2),
                "bestTrade": round(float(best_trade), 2),
                "worstTrade": round(float(worst_trade), 2),
                "totalProfitableTrades": len(profitable_trades),
                "totalLosingTrades": len(losing_trades),
            }

        except Exception as e:
            logger.error(f"Error calculating performance metrics: {e}")
            return {
                "winRate": 0.0,
                "profitFactor": 0.0,
                "sharpeRatio": 0.0,
                "maxDrawdown": 0.0,
                "avgTradePnL": 0.0,
                "bestTrade": 0.0,
                "worstTrade": 0.0,
                "totalProfitableTrades": 0,
                "totalLosingTrades": 0,
            }

    @staticmethod
    async def get_pnl_history(
        db: AsyncSession,
        date_range: str = 'ALL',
        bot_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get PnL history time series

        Returns:
            List of {timestamp, pnl, botId, botTicker}
        """
        try:
            date_filter = AnalyticsService.get_date_filter(date_range)

            # Build query
            query = select(Order).where(Order.status == OrderStatus.FILLED)

            if date_filter:
                query = query.where(Order.created_at >= date_filter)

            if bot_ids:
                from uuid import UUID
                bot_uuids = [UUID(bid) for bid in bot_ids]
                query = query.where(Order.bot_id.in_(bot_uuids))

            query = query.order_by(Order.created_at.asc())

            result = await db.execute(query)
            orders = result.scalars().all()

            # Build time series
            pnl_data = []
            cumulative_pnl = 0

            for order in orders:
                # Simplified PnL
                trade_pnl = float(order.filled_price or 0) - float(order.price)
                cumulative_pnl += trade_pnl

                # Get bot info
                bot_result = await db.execute(select(Bot).where(Bot.id == order.bot_id))
                bot = bot_result.scalar_one_or_none()

                pnl_data.append({
                    "timestamp": order.created_at.isoformat() if order.created_at else "",
                    "pnl": round(cumulative_pnl, 2),
                    "botId": str(order.bot_id) if order.bot_id else None,
                    "botTicker": bot.ticker if bot else None,
                })

            return pnl_data

        except Exception as e:
            logger.error(f"Error fetching PnL history: {e}")
            return []

    @staticmethod
    async def get_bot_comparison(
        db: AsyncSession,
        date_range: str = 'ALL'
    ) -> List[Dict[str, Any]]:
        """
        Get bot performance comparison

        Returns:
            List of {botId, ticker, exchange, totalTrades, pnl, winRate, status, rank}
        """
        try:
            # Get all bots
            bots_result = await db.execute(select(Bot))
            bots = bots_result.scalars().all()

            bot_performance = []

            for bot in bots:
                # Simple metrics from bot table
                bot_performance.append({
                    "botId": str(bot.id),
                    "ticker": bot.ticker,
                    "exchange": bot.exchange.value,
                    "totalTrades": bot.total_trades or 0,
                    "pnl": float(bot.pnl or 0),
                    "winRate": 0.0,  # Would need to calculate from orders
                    "status": bot.status.value,
                    "rank": 0,  # Will be calculated after sorting
                })

            # Sort by PnL and assign ranks
            bot_performance.sort(key=lambda x: x['pnl'], reverse=True)
            for i, bot in enumerate(bot_performance):
                bot['rank'] = i + 1

            return bot_performance

        except Exception as e:
            logger.error(f"Error fetching bot comparison: {e}")
            return []


# Export singleton instance
analytics_service = AnalyticsService()
