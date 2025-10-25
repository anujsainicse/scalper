"""
Pydantic schemas for User model
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID
from enum import Enum


class SubscriptionTier(str, Enum):
    """User subscription tiers"""
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


# User Schemas
class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for creating a new user (from Supabase)"""
    supabase_id: str
    avatar_url: Optional[str] = None
    is_verified: bool = False


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserResponse(UserBase):
    """Schema for user response (public data)"""
    id: UUID
    supabase_id: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    is_active: bool
    is_verified: bool
    subscription_tier: SubscriptionTier
    created_at: datetime
    last_login_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserProfile(UserResponse):
    """Extended user profile with additional information"""
    total_bots: Optional[int] = 0
    total_trades: Optional[int] = 0
    total_pnl: Optional[float] = 0.0

    class Config:
        from_attributes = True


# Authentication Schemas
class TokenResponse(BaseModel):
    """Response schema for token endpoints"""
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    expires_at: Optional[int] = None
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh"""
    refresh_token: str


# Supabase Callback Schema
class SupabaseCallbackData(BaseModel):
    """Data received from Supabase auth callback"""
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str
    user: dict
