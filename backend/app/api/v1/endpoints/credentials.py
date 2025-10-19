"""
Exchange Credentials API Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID
from datetime import datetime

from app.db.session import get_db
from app.models.credentials import ExchangeCredentials
from app.schemas.credentials import (
    CredentialsCreate,
    CredentialsUpdate,
    CredentialsResponse,
    CredentialsValidate
)
from app.utils.encryption import encrypt_api_key, decrypt_api_key
from app.exchanges import create_exchange_adapter

router = APIRouter()


@router.get("/", response_model=List[CredentialsResponse])
async def get_credentials(
    exchange: str = None,
    is_active: bool = None,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all exchange credentials with optional filtering.

    Note: Encrypted API keys are not returned in the response for security.
    """
    query = select(ExchangeCredentials)

    if exchange:
        query = query.where(ExchangeCredentials.exchange == exchange.lower())

    if is_active is not None:
        query = query.where(ExchangeCredentials.is_active == is_active)

    query = query.order_by(ExchangeCredentials.created_at.desc())

    result = await db.execute(query)
    credentials = result.scalars().all()

    return credentials


@router.post("/", response_model=CredentialsResponse, status_code=status.HTTP_201_CREATED)
async def create_credentials(
    credentials_data: CredentialsCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create new exchange credentials.

    API keys will be encrypted before storage.
    """
    # Check if credentials for this exchange already exist
    result = await db.execute(
        select(ExchangeCredentials)
        .where(ExchangeCredentials.exchange == credentials_data.exchange.lower())
        .where(ExchangeCredentials.is_testnet == credentials_data.is_testnet)
    )
    existing = result.scalar_one_or_none()

    if existing and existing.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Active credentials already exist for {credentials_data.exchange} ({'testnet' if credentials_data.is_testnet else 'mainnet'})"
        )

    # Encrypt API keys
    encrypted_api_key = encrypt_api_key(credentials_data.api_key)
    encrypted_secret_key = encrypt_api_key(credentials_data.secret_key)
    encrypted_passphrase = encrypt_api_key(credentials_data.passphrase) if credentials_data.passphrase else None

    # Create credentials
    credentials = ExchangeCredentials(
        exchange=credentials_data.exchange.lower(),
        exchange_display_name=credentials_data.exchange_display_name,
        api_key_encrypted=encrypted_api_key,
        secret_key_encrypted=encrypted_secret_key,
        passphrase_encrypted=encrypted_passphrase,
        is_testnet=credentials_data.is_testnet,
        is_active=credentials_data.is_active,
        label=credentials_data.label,
        description=credentials_data.description,
        is_validated=False
    )

    db.add(credentials)
    await db.commit()
    await db.refresh(credentials)

    return credentials


@router.get("/{credentials_id}", response_model=CredentialsResponse)
async def get_credential(
    credentials_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Get specific credentials by ID.
    """
    result = await db.execute(
        select(ExchangeCredentials).where(ExchangeCredentials.id == credentials_id)
    )
    credentials = result.scalar_one_or_none()

    if not credentials:
        raise HTTPException(status_code=404, detail="Credentials not found")

    return credentials


@router.put("/{credentials_id}", response_model=CredentialsResponse)
async def update_credentials(
    credentials_id: UUID,
    credentials_data: CredentialsUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update exchange credentials.

    If API keys are updated, they will be re-encrypted and validation status will be reset.
    """
    result = await db.execute(
        select(ExchangeCredentials).where(ExchangeCredentials.id == credentials_id)
    )
    credentials = result.scalar_one_or_none()

    if not credentials:
        raise HTTPException(status_code=404, detail="Credentials not found")

    # Update fields
    update_data = credentials_data.dict(exclude_unset=True, exclude_none=True)

    # If API keys are being updated, encrypt them and reset validation
    if 'api_key' in update_data:
        credentials.api_key_encrypted = encrypt_api_key(update_data.pop('api_key'))
        credentials.is_validated = False
        credentials.validation_error = None

    if 'secret_key' in update_data:
        credentials.secret_key_encrypted = encrypt_api_key(update_data.pop('secret_key'))
        credentials.is_validated = False
        credentials.validation_error = None

    if 'passphrase' in update_data:
        passphrase = update_data.pop('passphrase')
        credentials.passphrase_encrypted = encrypt_api_key(passphrase) if passphrase else None
        credentials.is_validated = False
        credentials.validation_error = None

    # Update other fields
    for field, value in update_data.items():
        setattr(credentials, field, value)

    await db.commit()
    await db.refresh(credentials)

    return credentials


@router.delete("/{credentials_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credentials(
    credentials_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete exchange credentials.

    This will permanently remove the credentials from the database.
    """
    result = await db.execute(
        select(ExchangeCredentials).where(ExchangeCredentials.id == credentials_id)
    )
    credentials = result.scalar_one_or_none()

    if not credentials:
        raise HTTPException(status_code=404, detail="Credentials not found")

    await db.delete(credentials)
    await db.commit()

    return None


@router.post("/{credentials_id}/validate", response_model=CredentialsValidate)
async def validate_credentials(
    credentials_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Validate exchange credentials by attempting to connect to the exchange.

    This will:
    1. Decrypt the API keys
    2. Create an exchange adapter
    3. Attempt to validate credentials with the exchange
    4. Update validation status in database
    """
    result = await db.execute(
        select(ExchangeCredentials).where(ExchangeCredentials.id == credentials_id)
    )
    credentials = result.scalar_one_or_none()

    if not credentials:
        raise HTTPException(status_code=404, detail="Credentials not found")

    try:
        # Decrypt API keys
        api_key = decrypt_api_key(credentials.api_key_encrypted)
        secret_key = decrypt_api_key(credentials.secret_key_encrypted)

        # Create exchange adapter
        adapter = create_exchange_adapter(
            exchange_name=credentials.exchange,
            api_key=api_key,
            secret_key=secret_key,
            testnet=credentials.is_testnet
        )

        # Validate credentials
        is_valid = await adapter.validate_credentials()

        if is_valid:
            # Update credentials as validated
            credentials.is_validated = True
            credentials.last_validated_at = datetime.now()
            credentials.validation_error = None

            await db.commit()

            return CredentialsValidate(
                success=True,
                message="Credentials validated successfully",
                validated_at=credentials.last_validated_at
            )
        else:
            # Update with validation failure
            credentials.is_validated = False
            credentials.validation_error = "Validation failed - check your API keys"

            await db.commit()

            return CredentialsValidate(
                success=False,
                message="Credentials validation failed - please check your API keys"
            )

    except Exception as e:
        # Update with error
        credentials.is_validated = False
        credentials.validation_error = str(e)

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to validate credentials: {str(e)}"
        )


@router.post("/{credentials_id}/toggle", response_model=CredentialsResponse)
async def toggle_credentials(
    credentials_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Toggle credentials active status.
    """
    result = await db.execute(
        select(ExchangeCredentials).where(ExchangeCredentials.id == credentials_id)
    )
    credentials = result.scalar_one_or_none()

    if not credentials:
        raise HTTPException(status_code=404, detail="Credentials not found")

    credentials.is_active = not credentials.is_active

    await db.commit()
    await db.refresh(credentials)

    return credentials
