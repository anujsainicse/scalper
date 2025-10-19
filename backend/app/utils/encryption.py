"""
Encryption Utilities

Provides functions for encrypting and decrypting sensitive data like API keys.
Uses Fernet symmetric encryption from the cryptography library.
"""

from cryptography.fernet import Fernet
from app.core.config import settings
import base64
import hashlib


def _get_encryption_key() -> bytes:
    """
    Generate an encryption key from the SECRET_KEY.

    Uses the application's SECRET_KEY to derive a Fernet-compatible key.
    This ensures the same key is used consistently across application restarts.

    Returns:
        bytes: Fernet encryption key
    """
    # Use SECRET_KEY from settings to derive a Fernet key
    # Fernet keys must be 32 url-safe base64-encoded bytes
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return base64.urlsafe_b64encode(key)


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key for secure storage.

    Args:
        api_key: Plain text API key

    Returns:
        str: Encrypted API key (base64 encoded)

    Example:
        >>> encrypted = encrypt_api_key("my-secret-api-key")
        >>> print(encrypted)
        'gAAAAA...'
    """
    if not api_key:
        return ""

    try:
        fernet = Fernet(_get_encryption_key())
        encrypted_bytes = fernet.encrypt(api_key.encode())
        return encrypted_bytes.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Failed to encrypt API key: {str(e)}")


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Decrypt an encrypted API key.

    Args:
        encrypted_key: Encrypted API key (base64 encoded)

    Returns:
        str: Decrypted API key in plain text

    Raises:
        ValueError: If decryption fails

    Example:
        >>> decrypted = decrypt_api_key(encrypted)
        >>> print(decrypted)
        'my-secret-api-key'
    """
    if not encrypted_key:
        return ""

    try:
        fernet = Fernet(_get_encryption_key())
        decrypted_bytes = fernet.decrypt(encrypted_key.encode())
        return decrypted_bytes.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Failed to decrypt API key: {str(e)}")


def is_encrypted(value: str) -> bool:
    """
    Check if a string appears to be encrypted.

    Args:
        value: String to check

    Returns:
        bool: True if value appears encrypted (starts with Fernet token prefix)
    """
    if not value:
        return False

    # Fernet tokens start with 'gAAAAA' in base64
    return value.startswith('gAAAAA')
