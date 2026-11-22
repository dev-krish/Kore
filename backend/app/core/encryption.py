import base64
import hashlib
import logging
from typing import Optional
from cryptography.fernet import Fernet
from app.core.config import settings

logger = logging.getLogger(__name__)

def _get_fernet_key() -> bytes:
    """Derives a deterministic 32-byte Fernet key from SECRET_KEY."""
    digest = hashlib.sha256(settings.SECRET_KEY.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)

def encrypt_token(plain_token: Optional[str]) -> Optional[str]:
    """
    Encrypts a sensitive OAuth token for storage at rest.
    Prefixes with 'enc:v1:' to clearly identify encrypted values.
    """
    if not plain_token:
        return plain_token
    if plain_token.startswith("enc:v1:"):
        return plain_token  # Already encrypted

    try:
        f = Fernet(_get_fernet_key())
        encrypted_bytes = f.encrypt(plain_token.encode("utf-8"))
        return f"enc:v1:{encrypted_bytes.decode('utf-8')}"
    except Exception as e:
        logger.error(f"Failed to encrypt sensitive token at rest: {e}")
        return plain_token

def decrypt_token(cipher_token: Optional[str]) -> Optional[str]:
    """
    Decrypts an encrypted OAuth token from storage.
    If the value is not prefixed with 'enc:v1:', returns as is (backwards compatible).
    """
    if not cipher_token:
        return cipher_token
    if not cipher_token.startswith("enc:v1:"):
        return cipher_token  # Unencrypted legacy token

    try:
        raw_token = cipher_token[len("enc:v1:"):]
        f = Fernet(_get_fernet_key())
        decrypted_bytes = f.decrypt(raw_token.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to decrypt sensitive token: {e}")
        return None
