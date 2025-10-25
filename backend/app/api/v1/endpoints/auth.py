"""
Authentication endpoints
Handles user authentication, profile management, and logout
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.session import get_db
from app.models.user import User
from app.models.bot import Bot, Trade
from app.schemas.user import (
    UserResponse,
    UserProfile,
    UserUpdate,
    TokenResponse,
    SupabaseCallbackData,
)
from app.dependencies.auth import get_current_user, get_current_active_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/user", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's profile

    Returns:
        User profile data
    """
    return current_user


@router.get("/profile", response_model=UserProfile)
async def get_user_profile_with_stats(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's extended profile with statistics

    Returns:
        Extended user profile with bot and trading statistics
    """
    # Get bot count
    bot_count_query = select(func.count(Bot.id)).where(Bot.user_id == current_user.id)
    bot_count_result = await db.execute(bot_count_query)
    total_bots = bot_count_result.scalar() or 0

    # Get trade count and total PnL
    trade_stats_query = select(
        func.count(Trade.id),
        func.coalesce(func.sum(Trade.pnl), 0.0)
    ).where(Trade.user_id == current_user.id)

    trade_stats_result = await db.execute(trade_stats_query)
    trade_stats = trade_stats_result.one()
    total_trades = trade_stats[0] or 0
    total_pnl = float(trade_stats[1]) if trade_stats[1] is not None else 0.0

    # Create profile response
    profile_data = {
        **current_user.to_dict(),
        "total_bots": total_bots,
        "total_trades": total_trades,
        "total_pnl": total_pnl,
    }

    return UserProfile(**profile_data)


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's profile

    Args:
        profile_update: Updated profile data

    Returns:
        Updated user profile
    """
    # Update user fields
    update_data = profile_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        setattr(current_user, field, value)

    await db.commit()
    await db.refresh(current_user)

    logger.info(f"User profile updated: {current_user.email}")

    return current_user


@router.post("/callback", response_model=TokenResponse)
async def supabase_auth_callback(
    callback_data: SupabaseCallbackData,
    db: AsyncSession = Depends(get_db)
):
    """
    Handle Supabase authentication callback

    This endpoint receives data from Supabase after successful authentication
    and creates or updates the user in the local database.

    Args:
        callback_data: Authentication data from Supabase

    Returns:
        Token response with user data
    """
    try:
        # Extract user data from callback
        supabase_user = callback_data.user
        supabase_id = supabase_user.get("id")
        email = supabase_user.get("email")

        if not supabase_id or not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid callback data: missing user ID or email"
            )

        # Check if user exists
        result = await db.execute(
            select(User).where(User.supabase_id == supabase_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            # Create new user
            user = User(
                supabase_id=supabase_id,
                email=email,
                full_name=supabase_user.get("user_metadata", {}).get("full_name"),
                avatar_url=supabase_user.get("user_metadata", {}).get("avatar_url"),
                is_verified=supabase_user.get("email_confirmed_at") is not None,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.info(f"New user created via callback: {email}")
        else:
            # Update existing user
            from datetime import datetime
            user.last_login_at = datetime.utcnow()
            await db.commit()
            await db.refresh(user)

        # Return token response
        return TokenResponse(
            access_token=callback_data.access_token,
            refresh_token=callback_data.refresh_token,
            token_type=callback_data.token_type,
            expires_at=callback_data.expires_in,
            user=UserResponse.from_orm(user)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Auth callback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication callback failed"
        )


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout current user

    Note: Token invalidation is handled by Supabase on the client side.
    This endpoint is mainly for logging and potential server-side cleanup.

    Returns:
        Success message
    """
    logger.info(f"User logged out: {current_user.email}")

    return {
        "message": "Successfully logged out",
        "user_id": str(current_user.id)
    }


@router.delete("/account")
async def delete_account(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete current user's account

    This will delete the user and all associated data (bots, trades, logs, etc.)
    due to CASCADE delete constraints.

    Returns:
        Success message
    """
    user_email = current_user.email

    # Delete user (CASCADE will handle related records)
    await db.delete(current_user)
    await db.commit()

    logger.warning(f"User account deleted: {user_email}")

    return {
        "message": "Account successfully deleted",
        "email": user_email
    }
