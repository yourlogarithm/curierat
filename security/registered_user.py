from classes.database_provider import DatabaseProvider
from security.user import User


class RegisteredUser(User):
    hashed_password: str

    @classmethod
    def get(cls, username: str) -> 'RegisteredUser | None':
        user = DatabaseProvider.users().find_one({'username': username})
        if user:
            return cls(**user)

    def dict(self, *args, **kwargs):
        dict_val = super().dict()
        dict_val['hashed_password'] = self.hashed_password
        return dict_val
