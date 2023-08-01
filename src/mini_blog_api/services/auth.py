import secrets
import string
from datetime import datetime, timedelta

import bcrypt
import jwt

from ..config import Settings, get_settings

settings: Settings = get_settings()


def generate_pwd():
    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(
        secrets.choice(characters) for _ in range(settings.password_length)
    )

    return hash_password(password)


def hash_password(plaintext: str):
    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(plaintext.encode("utf-8"), salt)

    return hashed_pwd.decode("utf-8")


def generate_access_token(account: dict):
    to_encode = account.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.token_exp)
    to_encode.update(dict(exp=expire))
    encode_jwt = jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_alg)

    return encode_jwt


def verify_password(plain_pwd: str, hashed_pwd: str) -> bool:
    return plain_pwd == hashed_pwd
