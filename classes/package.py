from typing import Mapping

from .form import Form
from .category import Category
from .open_route_service import OpenRouteService


class Package(Form):
    price: float
    closed: bool = False

    @staticmethod
    def get_price(form: Form):
        match form.category:
            case Category.Fragile:
                category_multiplier = 1.3
            case Category.Precious:
                category_multiplier = 1.1
            case Category.Dangerous:
                category_multiplier = 1.5
            case _:
                raise ValueError("Invalid category")
        data = OpenRouteService.get_route_data([form.office, form.destination])
        return (form.weight * 5 + data['total_distance'] * .25) * category_multiplier

    @classmethod
    def from_dict(cls, data: Mapping):
        return cls(
            sender_contact=data["sender_contact"],
            receiver_contact=data["receiver_contact"],
            office=data["office"],
            destination=data["destination"],
            weight=data["weight"],
            category=Category(data["category"]),
            price=data["price"],
            closed=data["closed"]
        )

    def to_dict(self):
        form_dict = super().to_dict()
        form_dict['price'] = self.price
        form_dict['closed'] = self.closed
        return form_dict



    
