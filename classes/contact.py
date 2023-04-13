from pydantic import BaseModel


class Contact(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
