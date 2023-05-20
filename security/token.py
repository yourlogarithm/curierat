from datetime import timedelta, datetime
from jose import jwt
from pydantic import BaseModel
from constants import ALGORITHM, JWT_TOKEN


class Token(BaseModel):
    access_token: str
    token_type: str

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({'exp': expire})
        encoded_jwt = jwt.encode(to_encode, JWT_TOKEN, algorithm=ALGORITHM)
        return encoded_jwt
