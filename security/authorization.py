from passlib.context import CryptContext
from typing import ClassVar
from pymongo.collection import Collection
from security.user import RegisteredUser


class Validation:
    pwd_context: ClassVar[CryptContext] = CryptContext(schemes=["argon2"], deprecated="auto")

    @staticmethod
    def authenticate_user(collection: Collection, username: str, password: str):
        user = RegisteredUser.get(collection, username)
        if user and Validation.verify_password(password, user.hashed_password):
            return user

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return Validation.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return Validation.pwd_context.hash(password)
