from datetime import UTC, datetime, timedelta

import bcrypt
import jwt

from core.config import settings


def encode_jwt(
    payload: dict,
    private_key: str = settings.auth_jwt.private_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
    expire_days: int = settings.auth_jwt.access_token_expire_days,
) -> str:
    """
    Кодирует jwt-токен
    :param payload: полезная нагрузка в токене
    :param private_key: закрытый ключ
    :param algorithm: алгоритм шифрования
    :param expire_days: действие токена в днях
    :return: токен доступа
    """
    to_encode = payload.copy()
    now = datetime.now(UTC)
    expire = now + timedelta(days=expire_days)
    to_encode.update(
        exp=expire,
        iat=now,
    )
    encoded = jwt.encode(
        to_encode,
        private_key,
        algorithm=algorithm,
    )
    return encoded


def decode_jwt(
    token: str | bytes,
    public_key: str = settings.auth_jwt.public_key_path.read_text(),
    algorithm: str = settings.auth_jwt.algorithm,
) -> dict:
    """
    Декодирует jwt-токен
    :param token: токен доступа
    :param public_key: публичный ключ
    :param algorithm: алгоритм шифрования
    :return: данные токена
    """
    decoded = jwt.decode(
        token,
        public_key,
        algorithms=[algorithm],
    )
    return decoded


def hash_password(
    password: str,
) -> bytes:
    """
    Хэширует пароль
    :param password: пароль
    :return: хэшированный пароль
    """
    salt = bcrypt.gensalt()
    pwd_bytes: bytes = password.encode()
    return bcrypt.hashpw(pwd_bytes, salt)


def validate_password(
    password: str,
    hashed_password: bytes,
) -> bool:
    """
    Сравнивает пароли
    :param password: пароль
    :param hashed_password: хэшированный пароль
    :return: результат сравнения
    """
    return bcrypt.checkpw(
        password=password.encode(),
        hashed_password=hashed_password,
    )


def get_access_token(
    user_id: int, username: str, is_admin: bool
) -> str:

    payload = {
        "sub": str(user_id),
        "username": username,
        "is_admin": is_admin,
    }
    token = encode_jwt(payload=payload)
    return token
