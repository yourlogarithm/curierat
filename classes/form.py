from pydantic import BaseModel
from .contact import Contact
from .category import Category


class Form(BaseModel):
    sender_contact: Contact
    receiver_contact: Contact
    office: str
    destination: str
    weight: float
    category: Category
