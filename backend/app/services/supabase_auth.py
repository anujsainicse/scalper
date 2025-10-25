"""
Supabase authentication service
Handles user authentication and JWT validation
"""

from typing import Optional, Dict, Any
from datetime import datetime
from supabase import create_client, Client
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class SupabaseAuthService:
    """
    Service for Supabase authentication operations
    """

    def __init__(self):
        """Initialize Supabase client"""
        self.supabase: Optional[Client] = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Supabase client with credentials from settings"""
        try:
            if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
                logger.warning("Supabase credentials not configured. Authentication disabled.")
                return

            self.supabase = create_client(
                supabase_url=settings.SUPABASE_URL,
                supabase_key=settings.SUPABASE_KEY
            )
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token from Supabase

        Args:
            token: JWT access token

        Returns:
            User data dictionary if valid, None if invalid

        Example return:
            {
                "sub": "user-uuid-from-supabase",
                "email": "user@example.com",
                "aud": "authenticated",
                "exp": 1234567890,
                ...
            }
        """
        if not self.supabase:
            logger.error("Supabase client not initialized")
            return None

        try:
            # Verify token with Supabase
            user_response = self.supabase.auth.get_user(token)

            if not user_response or not user_response.user:
                logger.warning("Invalid token: No user found")
                return None

            user = user_response.user

            # Extract user data
            user_data = {
                "sub": user.id,  # Supabase user ID
                "email": user.email,
                "email_verified": user.email_confirmed_at is not None,
                "full_name": user.user_metadata.get("full_name") if user.user_metadata else None,
                "avatar_url": user.user_metadata.get("avatar_url") if user.user_metadata else None,
                "provider": user.app_metadata.get("provider") if user.app_metadata else None,
                "created_at": user.created_at,
                "last_sign_in_at": user.last_sign_in_at,
            }

            return user_data

        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return None

    def get_user_by_id(self, supabase_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user details by Supabase user ID (requires service role key)

        Args:
            supabase_id: Supabase user ID

        Returns:
            User data dictionary if found, None otherwise
        """
        if not self.supabase:
            logger.error("Supabase client not initialized")
            return None

        try:
            # This requires service role key
            response = self.supabase.auth.admin.get_user_by_id(supabase_id)

            if not response or not response.user:
                return None

            user = response.user
            return {
                "sub": user.id,
                "email": user.email,
                "email_verified": user.email_confirmed_at is not None,
                "full_name": user.user_metadata.get("full_name") if user.user_metadata else None,
                "avatar_url": user.user_metadata.get("avatar_url") if user.user_metadata else None,
            }

        except Exception as e:
            logger.error(f"Failed to get user by ID: {str(e)}")
            return None

    def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """
        Refresh access token using refresh token

        Args:
            refresh_token: Refresh token

        Returns:
            New session data with access_token and refresh_token
        """
        if not self.supabase:
            logger.error("Supabase client not initialized")
            return None

        try:
            response = self.supabase.auth.refresh_session(refresh_token)

            if not response or not response.session:
                return None

            return {
                "access_token": response.session.access_token,
                "refresh_token": response.session.refresh_token,
                "expires_at": response.session.expires_at,
                "user": {
                    "sub": response.user.id,
                    "email": response.user.email,
                }
            }

        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            return None

    def sign_out(self, token: str) -> bool:
        """
        Sign out user (invalidate session)

        Args:
            token: Access token

        Returns:
            True if successful, False otherwise
        """
        if not self.supabase:
            logger.error("Supabase client not initialized")
            return False

        try:
            self.supabase.auth.sign_out()
            return True

        except Exception as e:
            logger.error(f"Sign out failed: {str(e)}")
            return False


# Global Supabase auth service instance
supabase_auth = SupabaseAuthService()


# Convenience function
def verify_supabase_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify Supabase JWT token

    Args:
        token: JWT access token

    Returns:
        User data if valid, None if invalid
    """
    return supabase_auth.verify_token(token)
