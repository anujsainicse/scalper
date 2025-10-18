from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.models.bot import Bot, ActivityLog, BotStatus
from app.schemas.bot import (
    BotCreate,
    BotUpdate,
    BotResponse,
    BotStatusUpdate,
    BotStatistics,
    ActivityLogResponse,
    ActivityLogCreate
)
from app.services.telegram import telegram_service

router = APIRouter()


@router.get("/", response_model=List[BotResponse])
async def get_bots(
    skip: int = 0,
    limit: int = 100,
    status: str = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all bots with optional filtering
    """
    query = select(Bot)

    if status:
        query = query.where(Bot.status == status)

    query = query.offset(skip).limit(limit).order_by(Bot.created_at.desc())

    result = await db.execute(query)
    bots = result.scalars().all()

    return bots


@router.post("/", response_model=BotResponse, status_code=status.HTTP_201_CREATED)
async def create_bot(
    bot_data: BotCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new bot
    """
    # Create bot
    bot = Bot(
        ticker=bot_data.ticker,
        exchange=bot_data.exchange,
        first_order=bot_data.first_order,
        quantity=bot_data.quantity,
        buy_price=bot_data.buy_price,
        sell_price=bot_data.sell_price,
        trailing_percent=bot_data.trailing_percent,
        infinite_loop=bot_data.infinite_loop,
        status=BotStatus.ACTIVE,  # Start as ACTIVE by default
    )

    db.add(bot)
    await db.flush()

    # Create activity log
    log = ActivityLog(
        bot_id=bot.id,
        level="SUCCESS",
        message=f"Bot started for {bot.ticker} on {bot.exchange.value}"
    )
    db.add(log)

    await db.commit()
    await db.refresh(bot)

    # Send Telegram notification
    await telegram_service.send_notification(
        db=db,
        message=f"*Bot Created*\n\n"
                f"Ticker: {bot.ticker}\n"
                f"Exchange: {bot.exchange.value}\n"
                f"Quantity: {bot.quantity}\n"
                f"Buy Price: ${bot.buy_price}\n"
                f"Sell Price: ${bot.sell_price}",
        level="SUCCESS"
    )

    return bot


@router.get("/{bot_id}", response_model=BotResponse)
async def get_bot(
    bot_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get a specific bot by ID
    """
    result = await db.execute(select(Bot).where(Bot.id == bot_id))
    bot = result.scalar_one_or_none()

    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    return bot


@router.put("/{bot_id}", response_model=BotResponse)
async def update_bot(
    bot_id: UUID,
    bot_data: BotUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a bot's configuration
    """
    result = await db.execute(select(Bot).where(Bot.id == bot_id))
    bot = result.scalar_one_or_none()

    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Update bot fields
    update_data = bot_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bot, field, value)

    # Create activity log
    log = ActivityLog(
        bot_id=bot.id,
        level="INFO",
        message=f"Bot updated for {bot.ticker} on {bot.exchange.value}"
    )
    db.add(log)

    await db.commit()
    await db.refresh(bot)

    return bot


@router.delete("/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bot(
    bot_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a bot
    """
    result = await db.execute(select(Bot).where(Bot.id == bot_id))
    bot = result.scalar_one_or_none()

    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Store bot info before deleting
    ticker = bot.ticker
    exchange = bot.exchange.value

    # Create activity log before deleting
    log = ActivityLog(
        bot_id=bot.id,
        level="WARNING",
        message=f"Bot deleted for {bot.ticker}"
    )
    db.add(log)

    await db.delete(bot)
    await db.commit()

    # Send Telegram notification
    await telegram_service.send_notification(
        db=db,
        message=f"*Bot Deleted*\n\n"
                f"Ticker: {ticker}\n"
                f"Exchange: {exchange}",
        level="WARNING"
    )

    return None


@router.post("/{bot_id}/start", response_model=BotResponse)
async def start_bot(
    bot_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Start a bot (set status to ACTIVE)
    """
    result = await db.execute(select(Bot).where(Bot.id == bot_id))
    bot = result.scalar_one_or_none()

    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    bot.status = BotStatus.ACTIVE

    log = ActivityLog(
        bot_id=bot.id,
        level="SUCCESS",
        message=f"Bot started for {bot.ticker}"
    )
    db.add(log)

    await db.commit()
    await db.refresh(bot)

    # Send Telegram notification
    await telegram_service.send_notification(
        db=db,
        message=f"*Bot Started*\n\n"
                f"Ticker: {bot.ticker}\n"
                f"Exchange: {bot.exchange.value}\n"
                f"Status: ACTIVE",
        level="SUCCESS"
    )

    return bot


@router.post("/{bot_id}/stop", response_model=BotResponse)
async def stop_bot(
    bot_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Stop a bot (set status to STOPPED)
    """
    result = await db.execute(select(Bot).where(Bot.id == bot_id))
    bot = result.scalar_one_or_none()

    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    bot.status = BotStatus.STOPPED

    log = ActivityLog(
        bot_id=bot.id,
        level="WARNING",
        message=f"Bot stopped for {bot.ticker}"
    )
    db.add(log)

    await db.commit()
    await db.refresh(bot)

    # Send Telegram notification
    await telegram_service.send_notification(
        db=db,
        message=f"*Bot Stopped*\n\n"
                f"Ticker: {bot.ticker}\n"
                f"Exchange: {bot.exchange.value}\n"
                f"Status: STOPPED",
        level="WARNING"
    )

    return bot


@router.post("/{bot_id}/toggle", response_model=BotResponse)
async def toggle_bot(
    bot_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Toggle bot status (ACTIVE <-> STOPPED)
    """
    result = await db.execute(select(Bot).where(Bot.id == bot_id))
    bot = result.scalar_one_or_none()

    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    # Toggle status
    new_status = BotStatus.STOPPED if bot.status == BotStatus.ACTIVE else BotStatus.ACTIVE
    bot.status = new_status

    log_level = "SUCCESS" if new_status == BotStatus.ACTIVE else "WARNING"
    log = ActivityLog(
        bot_id=bot.id,
        level=log_level,
        message=f"Bot {new_status.value.lower()} for {bot.ticker}"
    )
    db.add(log)

    await db.commit()
    await db.refresh(bot)

    return bot


@router.post("/stop-all", status_code=status.HTTP_200_OK)
async def stop_all_bots(
    db: AsyncSession = Depends(get_db)
):
    """
    Stop all active bots
    """
    result = await db.execute(select(Bot).where(Bot.status == BotStatus.ACTIVE))
    bots = result.scalars().all()

    for bot in bots:
        bot.status = BotStatus.STOPPED

    # Create activity log
    log = ActivityLog(
        level="ERROR",
        message="Emergency stop - All bots stopped"
    )
    db.add(log)

    await db.commit()

    # Send Telegram notification
    await telegram_service.send_notification(
        db=db,
        message=f"*Emergency Stop*\n\n"
                f"All bots have been stopped!\n"
                f"Total bots stopped: {len(bots)}",
        level="ERROR"
    )

    return {"message": f"Stopped {len(bots)} bots", "count": len(bots)}


@router.get("/statistics/summary", response_model=BotStatistics)
async def get_statistics(
    db: AsyncSession = Depends(get_db)
):
    """
    Get bot statistics
    """
    # Total bots
    total_result = await db.execute(select(func.count(Bot.id)))
    total_bots = total_result.scalar()

    # Active bots
    active_result = await db.execute(
        select(func.count(Bot.id)).where(Bot.status == BotStatus.ACTIVE)
    )
    active_bots = active_result.scalar()

    # Stopped bots
    stopped_bots = total_bots - active_bots

    # Total PnL
    pnl_result = await db.execute(select(func.sum(Bot.pnl)))
    total_pnl = pnl_result.scalar() or 0.0

    # Total trades
    trades_result = await db.execute(select(func.sum(Bot.total_trades)))
    total_trades = trades_result.scalar() or 0

    return {
        "total_bots": total_bots,
        "active_bots": active_bots,
        "stopped_bots": stopped_bots,
        "total_pnl": total_pnl,
        "total_trades": total_trades
    }
