"""
Pydantic schemas for Exchange Credentials
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class CredentialsBase(BaseModel):
    """Base credentials schema"""
    exchange: str = Field(..., description="Exchange name (e.g., 'coindcx', 'bybit')")
    exchange_display_name: str = Field(..., description="Display name for the exchange")
    label: Optional[str] = Field(None, description="Optional label for these credentials")
    description: Optional[str] = Field(None, description="Optional description")
    is_testnet: bool = Field(default=True, description="Whether to use testnet or mainnet")
    is_active: bool = Field(default=True, description="Whether credentials are active")


class CredentialsCreate(CredentialsBase):
    """Schema for creating new credentials"""
    api_key: str = Field(..., description="Exchange API key (will be encrypted)")
    secret_key: str = Field(..., description="Exchange secret key (will be encrypted)")
    passphrase: Optional[str] = Field(None, description="Exchange passphrase if required (will be encrypted)")


class CredentialsUpdate(BaseModel):
    """Schema for updating credentials (all fields optional)"""
    exchange_display_name: Optional[str] = None
    api_key: Optional[str] = Field(None, description="New API key (will be encrypted)")
    secret_key: Optional[str] = Field(None, description="New secret key (will be encrypted)")
    passphrase: Optional[str] = Field(None, description="New passphrase (will be encrypted)")
    label: Optional[str] = None
    description: Optional[str] = None
    is_testnet: Optional[bool] = None
    is_active: Optional[bool] = None


class CredentialsResponse(CredentialsBase):
    """Schema for returning credentials (encrypted keys not exposed)"""
    id: UUID
    is_validated: bool
    last_validated_at: Optional[datetime] = None
    validation_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    # Note: We never return encrypted keys in responses for security
    # Frontend doesn't need to see them

    class Config:
        from_attributes = True


class CredentialsValidate(BaseModel):
    """Schema for credential validation response"""
    success: bool
    message: str
    validated_at: Optional[datetime] = None
