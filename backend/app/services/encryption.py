"""
Encryption service for API keys using Fernet symmetric encryption
Provides secure encryption and decryption of sensitive credentials
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64
import os
from typing import Tuple
from app.core.config import settings


class EncryptionService:
    """
    Handles encryption and decryption of API keys
    Uses Fernet (symmetric encryption) based on SECRET_KEY
    """

    def __init__(self):
        """Initialize encryption service with derived key from SECRET_KEY"""
        self._fernet = self._create_fernet_key()

    def _create_fernet_key(self) -> Fernet:
        """
        Create Fernet cipher from SECRET_KEY using PBKDF2 key derivation

        Returns:
            Fernet cipher instance
        """
        # Use a fixed salt (in production, consider per-user salts)
        salt = b'scalper_bot_encryption_salt_v1'

        # Derive a key from SECRET_KEY
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )

        key = base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))
        return Fernet(key)

    def encrypt_credentials(self, api_key: str, api_secret: str) -> Tuple[bytes, bytes]:
        """
        Encrypt API key and secret

        Args:
            api_key: Plain text API key
            api_secret: Plain text API secret

        Returns:
            Tuple of (encrypted_key, encrypted_secret) as bytes
        """
        encrypted_key = self._fernet.encrypt(api_key.encode())
        encrypted_secret = self._fernet.encrypt(api_secret.encode())

        return encrypted_key, encrypted_secret

    def decrypt_credentials(self, encrypted_key: bytes, encrypted_secret: bytes) -> Tuple[str, str]:
        """
        Decrypt API key and secret

        Args:
            encrypted_key: Encrypted API key
            encrypted_secret: Encrypted API secret

        Returns:
            Tuple of (api_key, api_secret) as plain text strings

        Raises:
            ValueError: If decryption fails (invalid key or corrupted data)
        """
        try:
            api_key = self._fernet.decrypt(encrypted_key).decode()
            api_secret = self._fernet.decrypt(encrypted_secret).decode()
            return api_key, api_secret
        except Exception as e:
            raise ValueError(f"Failed to decrypt credentials: {str(e)}")

    def encrypt_string(self, value: str) -> bytes:
        """
        Encrypt a single string value

        Args:
            value: Plain text string

        Returns:
            Encrypted value as bytes
        """
        return self._fernet.encrypt(value.encode())

    def decrypt_string(self, encrypted_value: bytes) -> str:
        """
        Decrypt a single encrypted value

        Args:
            encrypted_value: Encrypted bytes

        Returns:
            Decrypted string

        Raises:
            ValueError: If decryption fails
        """
        try:
            return self._fernet.decrypt(encrypted_value).decode()
        except Exception as e:
            raise ValueError(f"Failed to decrypt value: {str(e)}")

    def rotate_key(self, old_secret_key: str, new_secret_key: str, encrypted_data: bytes) -> bytes:
        """
        Rotate encryption key (for key rotation scenarios)

        Args:
            old_secret_key: Previous SECRET_KEY
            new_secret_key: New SECRET_KEY
            encrypted_data: Data encrypted with old key

        Returns:
            Data encrypted with new key
        """
        # Create old Fernet instance
        old_fernet = self._create_fernet_from_key(old_secret_key)

        # Decrypt with old key
        plain_text = old_fernet.decrypt(encrypted_data).decode()

        # Re-encrypt with new key (current instance)
        return self._fernet.encrypt(plain_text.encode())

    def _create_fernet_from_key(self, secret_key: str) -> Fernet:
        """
        Create Fernet instance from a specific secret key

        Args:
            secret_key: Secret key to use

        Returns:
            Fernet instance
        """
        salt = b'scalper_bot_encryption_salt_v1'
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
        return Fernet(key)


# Global encryption service instance
encryption_service = EncryptionService()


# Convenience functions
def encrypt_api_credentials(api_key: str, api_secret: str) -> Tuple[bytes, bytes]:
    """
    Encrypt API credentials

    Args:
        api_key: Plain text API key
        api_secret: Plain text API secret

    Returns:
        Tuple of (encrypted_key, encrypted_secret)
    """
    return encryption_service.encrypt_credentials(api_key, api_secret)


def decrypt_api_credentials(encrypted_key: bytes, encrypted_secret: bytes) -> Tuple[str, str]:
    """
    Decrypt API credentials

    Args:
        encrypted_key: Encrypted API key
        encrypted_secret: Encrypted API secret

    Returns:
        Tuple of (api_key, api_secret) as plain text
    """
    return encryption_service.decrypt_credentials(encrypted_key, encrypted_secret)
