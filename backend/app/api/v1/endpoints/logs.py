from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from typing import List, Optional
from uuid import UUID

from app.db.session import get_db
from app.models.user import User
from app.models.bot import ActivityLog, Bot
from app.schemas.bot import ActivityLogResponse, ActivityLogCreate
from app.services.websocket_manager import ws_manager
from app.dependencies.auth import get_current_active_user

router = APIRouter()


@router.get("/", response_model=List[ActivityLogResponse])
async def get_activity_logs(
    skip: int = 0,
    limit: int = 1000,
    level: Optional[str] = None,
    bot_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get activity logs for the current user with optional filtering
    """
    # Multi-user support: filter by current user
    query = select(ActivityLog).where(ActivityLog.user_id == current_user.id)

    if level:
        query = query.where(ActivityLog.level == level)

    if bot_id:
        query = query.where(ActivityLog.bot_id == bot_id)

    query = query.offset(skip).limit(limit).order_by(ActivityLog.timestamp.asc())

    result = await db.execute(query)
    logs = result.scalars().all()

    return logs


@router.post("/", response_model=ActivityLogResponse)
async def create_activity_log(
    log_data: ActivityLogCreate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new activity log entry for the current user
    """
    # Multi-user support: verify bot ownership if bot_id provided
    if log_data.bot_id:
        bot_result = await db.execute(
            select(Bot).where(
                Bot.id == log_data.bot_id,
                Bot.user_id == current_user.id
            )
        )
        bot = bot_result.scalar_one_or_none()
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

    log = ActivityLog(
        user_id=current_user.id,  # Multi-user support
        level=log_data.level,
        message=log_data.message,
        bot_id=log_data.bot_id
    )

    db.add(log)
    await db.commit()
    await db.refresh(log)

    # Broadcast log creation via WebSocket
    await ws_manager.broadcast_log_created({
        "id": str(log.id),
        "level": log.level,
        "message": log.message,
        "botId": str(log.bot_id) if log.bot_id else None,
        "timestamp": log.timestamp.isoformat(),
    })

    return log


@router.delete("/", status_code=204)
async def clear_all_logs(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Clear all activity logs for the current user
    """
    # Multi-user support: only delete current user's logs
    await db.execute(
        delete(ActivityLog).where(ActivityLog.user_id == current_user.id)
    )
    await db.commit()

    return None


@router.get("/count")
async def get_logs_count(
    level: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get count of logs by level for the current user
    """
    # Multi-user support: filter by current user
    if level:
        result = await db.execute(
            select(func.count(ActivityLog.id)).where(
                ActivityLog.level == level,
                ActivityLog.user_id == current_user.id
            )
        )
        count = result.scalar()
        return {"level": level, "count": count}

    # Count all levels
    levels = ["INFO", "SUCCESS", "WARNING", "ERROR", "TELEGRAM"]
    counts = {}

    for log_level in levels:
        result = await db.execute(
            select(func.count(ActivityLog.id)).where(
                ActivityLog.level == log_level,
                ActivityLog.user_id == current_user.id
            )
        )
        counts[log_level] = result.scalar()

    # Total
    total_result = await db.execute(
        select(func.count(ActivityLog.id)).where(ActivityLog.user_id == current_user.id)
    )
    counts["TOTAL"] = total_result.scalar()

    return counts
