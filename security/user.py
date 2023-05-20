from pydantic import BaseModel
from security.access_level import AccessLevel


class User(BaseModel):
    username: str
    email: str
    fullname: str
    disabled: bool = False
    access_level: AccessLevel

    def dict(self, *args, **kwargs):
        return {
            'username': self.username,
            'email': self.email,
            'fullname': self.fullname,
            'disabled': self.disabled,
            'access_level': self.access_level.value,
        }
