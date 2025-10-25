"""
Authentication dependencies for FastAPI endpoints
Provides user authentication and authorization
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.user import User
from app.services.supabase_auth import verify_supabase_token
import logging

logger = logging.getLogger(__name__)

# HTTP Bearer token authentication
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get current authenticated user from JWT token

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        User object

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    # Check if credentials are provided
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please provide a valid access token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    # Verify token with Supabase
    user_data = verify_supabase_token(token)

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    supabase_id = user_data.get("sub")
    email = user_data.get("email")

    if not supabase_id or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get or create user in local database
    result = await db.execute(
        select(User).where(User.supabase_id == supabase_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        # Create new user if doesn't exist
        user = User(
            supabase_id=supabase_id,
            email=email,
            full_name=user_data.get("full_name"),
            avatar_url=user_data.get("avatar_url"),
            is_verified=user_data.get("email_verified", False),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        logger.info(f"Created new user: {email} (supabase_id: {supabase_id})")
    else:
        # Update last login time
        from sqlalchemy import update
        from datetime import datetime

        await db.execute(
            update(User)
            .where(User.id == user.id)
            .values(last_login_at=datetime.utcnow())
        )
        await db.commit()
        await db.refresh(user)

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current active user (ensures user is not deactivated)

    Args:
        current_user: Current user from get_current_user

    Returns:
        Active user object

    Raises:
        HTTPException: 403 if user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account"
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise None
    Useful for optional authentication endpoints

    Args:
        credentials: HTTP Bearer token credentials
        db: Database session

    Returns:
        User object if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


def require_subscription_tier(*allowed_tiers: str):
    """
    Dependency factory to require specific subscription tier(s)

    Args:
        *allowed_tiers: Allowed subscription tier names (e.g., "pro", "enterprise")

    Returns:
        Dependency function

    Example:
        @router.get("/premium-feature", dependencies=[Depends(require_subscription_tier("pro", "enterprise"))])
    """
    async def check_subscription_tier(
        current_user: User = Depends(get_current_active_user)
    ):
        if current_user.subscription_tier.value not in allowed_tiers:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"This feature requires {' or '.join(allowed_tiers)} subscription"
            )
        return current_user

    return check_subscription_tier


async def require_verified_email(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Require user to have verified email

    Args:
        current_user: Current active user

    Returns:
        User with verified email

    Raises:
        HTTPException: 403 if email is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email address to access this feature"
        )
    return current_user
