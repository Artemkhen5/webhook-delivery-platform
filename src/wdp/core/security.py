from secrets import token_urlsafe

from cryptography.fernet import Fernet

from wdp.core.config import get_settings


def generate_secret() -> str:
    return token_urlsafe(32)


def _get_fernet() -> Fernet:
    key = get_settings().encryption_key.get_secret_value()
    return Fernet(key.encode("ascii"))


def encrypt_secret(secret: str) -> str:
    encrypted = _get_fernet().encrypt(secret.encode("utf-8"))
    return encrypted.decode("ascii")


def decrypt_secret(encrypted_secret: str) -> str:
    encrypted = _get_fernet().decrypt(encrypted_secret.encode("ascii"))
    return encrypted.decode("utf-8")
