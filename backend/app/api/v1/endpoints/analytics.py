"""
Analytics API endpoints for performance metrics and insights
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from app.db.session import get_db
from app.services.analytics_service import analytics_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/portfolio")
async def get_portfolio_metrics(
    range: str = Query('1W', description="Date range: 1D, 1W, 1M, 3M, ALL"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get overall portfolio metrics

    Returns:
        - totalPnL: Combined PnL across all bots
        - totalTrades: Total number of trades
        - activeBots: Number of active bots
        - totalVolume: Total trading volume
        - winRate: Overall win rate percentage
        - avgTradeValue: Average value per trade
    """
    metrics = await analytics_service.get_portfolio_metrics(db, range)
    return metrics


@router.get("/performance")
async def get_performance_metrics(
    range: str = Query('1W', description="Date range: 1D, 1W, 1M, 3M, ALL"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed performance metrics

    Returns:
        - winRate: Percentage of profitable trades
        - profitFactor: Gross profit / Gross loss
        - sharpeRatio: Risk-adjusted returns
        - maxDrawdown: Largest peak-to-trough decline
        - avgTradePnL: Average profit per trade
        - bestTrade: Highest profit trade
        - worstTrade: Largest loss trade
        - totalProfitableTrades: Count of winning trades
        - totalLosingTrades: Count of losing trades
    """
    metrics = await analytics_service.get_performance_metrics(db, range)
    return metrics


@router.get("/pnl-history")
async def get_pnl_history(
    range: str = Query('1W', description="Date range: 1D, 1W, 1M, 3M, ALL"),
    bot_ids: Optional[List[str]] = Query(None, description="Filter by bot IDs"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get PnL history time series

    Returns:
        List of {timestamp, pnl, botId, botTicker}
    """
    history = await analytics_service.get_pnl_history(db, range, bot_ids)
    return history


@router.get("/trade-history")
async def get_trade_history(
    range: str = Query('1W', description="Date range: 1D, 1W, 1M, 3M, ALL"),
    bot_ids: Optional[List[str]] = Query(None, description="Filter by bot IDs"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    Get paginated trade history

    Returns:
        List of trade records with pagination
    """
    # TODO: Implement trade history with pagination
    # For now, return empty list
    return []


@router.get("/bot-comparison")
async def get_bot_comparison(
    range: str = Query('1W', description="Date range: 1D, 1W, 1M, 3M, ALL"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get bot performance comparison

    Returns:
        List of {botId, ticker, exchange, totalTrades, pnl, winRate, status, rank}
    """
    comparison = await analytics_service.get_bot_comparison(db, range)
    return comparison


@router.get("/hourly-performance")
async def get_hourly_performance(
    range: str = Query('1W', description="Date range: 1D, 1W, 1M, 3M, ALL"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get performance metrics by hour of day

    Returns:
        Heatmap data for performance by hour
    """
    # TODO: Implement hourly performance analysis
    # For now, return empty list
    return []
