from security.authorization import Validation
from security.user import User, RegisteredUser


class RegisterForm(User):
    password: str
    test: bool = False

    def to_user(self) -> RegisteredUser:
        return RegisteredUser(**self.dict(), hashed_password=Validation.get_password_hash(self.password))
