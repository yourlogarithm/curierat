from .form import Form
from .category import Category
from .open_route_service import OpenRouteService


class Ticket(Form):
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

    def to_dict(self):
        form_dict = super().to_dict()
        form_dict['price'] = self.price
        form_dict['closed'] = self.closed
        return form_dict



    
