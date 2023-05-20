from security.validation import Validation
from security.user import User
from security.registered_user import RegisteredUser


class RegisterForm(User):
    password: str

    def to_user(self) -> RegisteredUser:
        return RegisteredUser(**self.dict(), hashed_password=Validation.get_password_hash(self.password))
