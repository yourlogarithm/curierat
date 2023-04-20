from .form import Form
from .category import Category
from .route import Route


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
        coords = Route.get_coordinates_of_cities([form.office, form.destination])
        distances, _ = Route.get_distance_and_duration_between_coords(coords)
        return (form.weight * 5 + sum(distances) * .25) * category_multiplier  # TODO: find optimal route


    
