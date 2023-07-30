from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

import jwt
from jose import JWTError
import bcrypt
import secrets
import string
from datetime import datetime, timedelta
from ..config import Settings, get_settings

settings: Settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def generate_pwd():
    characters = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(characters)
                       for l in range(settings.password_length))

    return hash_password(password)


def hash_password(plaintext: str):
    salt = bcrypt.gensalt()
    hashed_pwd = bcrypt.hashpw(plaintext.encode("utf-8"), salt)

    return hashed_pwd.decode("utf-8")


def generate_access_token(account: dict):
    to_encode = account.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.token_exp)
    to_encode.update(dict(exp=expire))
    encode_jwt = jwt.encode(
        to_encode, settings.jwt_secret, algorithm=settings.jwt_alg)

    return encode_jwt


def verify_password(plain_pwd: str, hashed_pwd: str) -> bool:
    return plain_pwd == hashed_pwd


async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, settings.jwt_secret,
                             algorithm=settings.jwt_alg)
        username = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token.")

        return username

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token.")
