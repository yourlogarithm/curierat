from pydantic import BaseModel
from .form import Form
from .category import Category


class Ticket(Form, BaseModel):
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
        return (form.weight * 5 + form.distance * .25) * category_multiplier  # TODO: find optimal route, based on distance calculate price

    price: float
    
