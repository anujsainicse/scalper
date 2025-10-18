"""
Telegram API Endpoints

Handles Telegram bot connection and notification management
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
from typing import List

from app.db.session import get_db
from app.models.bot import TelegramConnection
from app.schemas.bot import (
    TelegramConnectionCodeResponse,
    TelegramStatus,
    TelegramConnectionResponse,
    TelegramNotification
)
from app.services.telegram import telegram_service

router = APIRouter()


@router.post("/generate-code", response_model=TelegramConnectionCodeResponse)
async def generate_connection_code(db: AsyncSession = Depends(get_db)):
    """
    Generate a new connection code for Telegram

    Creates a 6-digit code that users can send to the Telegram bot to connect their account.
    The code expires after 10 minutes.
    """
    try:
        # Delete old pending connections (expired or incomplete)
        result = await db.execute(
            select(TelegramConnection).where(
                TelegramConnection.chat_id == "pending"
            )
        )
        old_pending = result.scalars().all()
        for conn in old_pending:
            await db.delete(conn)
        await db.commit()

        # Generate unique code
        code, expires_at = await telegram_service.generate_connection_code(db)

        # Create pending connection record
        connection = TelegramConnection(
            chat_id="pending",  # Will be updated when user sends code
            connection_code=code,
            code_expires_at=expires_at,
            is_active=False
        )

        db.add(connection)
        await db.commit()
        await db.refresh(connection)

        return TelegramConnectionCodeResponse(
            connection_code=code,
            expires_at=expires_at,
            message=f"Send this code to the Telegram bot: {code}"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate connection code: {str(e)}")


@router.get("/status", response_model=TelegramStatus)
async def get_telegram_status(db: AsyncSession = Depends(get_db)):
    """
    Check Telegram connection status

    Returns the current connection status including whether a Telegram account is connected.
    """
    try:
        # Find active connection
        result = await db.execute(
            select(TelegramConnection).where(TelegramConnection.is_active == True)
        )
        connection = result.scalar_one_or_none()

        if connection:
            return TelegramStatus(
                connected=True,
                chat_id=connection.chat_id,
                username=connection.username,
                connected_at=connection.connected_at
            )
        else:
            return TelegramStatus(
                connected=False,
                chat_id=None,
                username=None,
                connected_at=None
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check status: {str(e)}")


@router.post("/disconnect")
async def disconnect_telegram(db: AsyncSession = Depends(get_db)):
    """
    Disconnect Telegram

    Deactivates the current Telegram connection.
    """
    try:
        # Find active connection
        result = await db.execute(
            select(TelegramConnection).where(TelegramConnection.is_active == True)
        )
        connection = result.scalar_one_or_none()

        if not connection:
            raise HTTPException(status_code=404, detail="No active Telegram connection found")

        # Deactivate connection
        connection.is_active = False
        await db.commit()

        return {"message": "Telegram disconnected successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to disconnect: {str(e)}")


@router.post("/send-notification")
async def send_test_notification(
    notification: TelegramNotification,
    db: AsyncSession = Depends(get_db)
):
    """
    Send a test notification to Telegram

    Sends a test message to all active Telegram connections.
    """
    try:
        await telegram_service.send_notification(
            db=db,
            message=notification.message,
            level=notification.level.value if notification.level else "INFO"
        )

        return {"message": "Notification sent successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {str(e)}")


@router.get("/connections", response_model=List[TelegramConnectionResponse])
async def get_all_connections(db: AsyncSession = Depends(get_db)):
    """
    Get all Telegram connections

    Returns a list of all Telegram connections (active and inactive).
    """
    try:
        result = await db.execute(
            select(TelegramConnection).order_by(TelegramConnection.connected_at.desc())
        )
        connections = result.scalars().all()

        return connections

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve connections: {str(e)}")


@router.delete("/connections/{connection_id}")
async def delete_connection(connection_id: str, db: AsyncSession = Depends(get_db)):
    """
    Delete a Telegram connection

    Permanently removes a Telegram connection from the database.
    """
    try:
        from uuid import UUID

        # Convert string to UUID
        try:
            connection_uuid = UUID(connection_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid connection ID format")

        # Find connection
        result = await db.execute(
            select(TelegramConnection).where(TelegramConnection.id == connection_uuid)
        )
        connection = result.scalar_one_or_none()

        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found")

        # Delete connection
        await db.delete(connection)
        await db.commit()

        return {"message": "Connection deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete connection: {str(e)}")


@router.get("/stats")
async def get_telegram_stats(db: AsyncSession = Depends(get_db)):
    """
    Get Telegram connection statistics

    Returns statistics about Telegram connections and notifications.
    """
    try:
        # Count total connections
        total_result = await db.execute(select(func.count(TelegramConnection.id)))
        total_connections = total_result.scalar()

        # Count active connections
        active_result = await db.execute(
            select(func.count(TelegramConnection.id)).where(TelegramConnection.is_active == True)
        )
        active_connections = active_result.scalar()

        # Count connections with recent notifications (last 24 hours)
        recent_time = datetime.utcnow() - timedelta(hours=24)
        recent_result = await db.execute(
            select(func.count(TelegramConnection.id)).where(
                TelegramConnection.last_notification_at >= recent_time
            )
        )
        recent_notifications = recent_result.scalar()

        return {
            "total_connections": total_connections,
            "active_connections": active_connections,
            "inactive_connections": total_connections - active_connections,
            "recent_notifications_24h": recent_notifications
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve stats: {str(e)}")


from datetime import timedelta
