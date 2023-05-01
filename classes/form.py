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

    def to_dict(self):
        return {
            "sender_contact": self.sender_contact.dict(),
            "receiver_contact": self.receiver_contact.dict(),
            "office": self.office,
            "destination": self.destination,
            "weight": self.weight,
            "category": self.category.value
        }
