from pydantic import BaseModel
from .contact import Contact
from .category import Category
from .open_route_service import OpenRouteService


class Form(BaseModel):
    sender_contact: Contact
    receiver_contact: Contact
    office: str
    destination: str
    weight: float
    category: Category
    price: float = None

    def __init__(self, **data):
        super().__init__(**data)
        self.price = self.price or self._get_price()

    def to_dict(self):
        return {
            'sender_contact': self.sender_contact.dict(),
            'receiver_contact': self.receiver_contact.dict(),
            'office': self.office,
            'destination': self.destination,
            'weight': self.weight,
            'category': self.category.value
        }

    def _get_price(self) -> float:
        match self.category:
            case Category.Fragile:
                category_multiplier = 1.3
            case Category.Precious:
                category_multiplier = 1.1
            case Category.Dangerous:
                category_multiplier = 1.5
            case Category.Regular:
                category_multiplier = 1
            case _:
                raise ValueError('Invalid category')
        data = OpenRouteService.get_route_data([self.office, self.destination])
        return (self.weight * 5 + data['total_distance'] * .25) * category_multiplier
