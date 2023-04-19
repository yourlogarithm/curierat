import re
from pydantic import BaseModel
from classes.category import Category


class Transport(BaseModel):
    id: str
    cargo_category: Category

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = self.id.upper().replace(" ", "")
        if re.match(r"[^A-Z0-9]", self.id):
            raise ValueError("Transport ID must only contain letters and numbers")

    def dict(self, *args, **kwargs):
        return {
            "_id": self.id,
            "cargo_category": self.cargo_category.value
        }
