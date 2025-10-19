"""
Exchange Credentials Model

Stores encrypted API credentials for different exchanges.
"""

from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.db.session import Base
import uuid


class ExchangeCredentials(Base):
    """
    Store exchange API credentials securely.

    Credentials are encrypted before storage using Fernet encryption.
    Each credential set is linked to a specific exchange.
    """
    __tablename__ = "exchange_credentials"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)

    # Exchange information
    exchange = Column(String(50), nullable=False, index=True)  # e.g., 'coindcx', 'bybit'
    exchange_display_name = Column(String(100), nullable=False)  # e.g., 'CoinDCX F', 'Bybit'

    # Encrypted credentials
    api_key_encrypted = Column(String(500), nullable=False)
    secret_key_encrypted = Column(String(500), nullable=False)

    # Optional: Additional credentials (e.g., passphrase for some exchanges)
    passphrase_encrypted = Column(String(500), nullable=True)

    # Configuration
    is_testnet = Column(Boolean, default=True, index=True)
    is_active = Column(Boolean, default=True, index=True)

    # Metadata
    label = Column(String(100), nullable=True)  # User-friendly label
    description = Column(String(500), nullable=True)

    # Validation status
    is_validated = Column(Boolean, default=False)  # Whether credentials have been tested
    last_validated_at = Column(DateTime(timezone=True), nullable=True)
    validation_error = Column(String(500), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Additional settings (exchange-specific configurations)
    extra_config = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<ExchangeCredentials(id={self.id}, exchange={self.exchange}, testnet={self.is_testnet})>"
