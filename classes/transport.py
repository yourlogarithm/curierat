import re
from typing import Mapping

from fastapi import HTTPException
from pydantic import BaseModel
from classes.category import Category


class Transport(BaseModel):
    id: str
    cargo_category: Category
    max_weight: float

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.id = self.id.upper().replace(' ', '')
        if re.match(r'[^A-Z0-9]', self.id):
            raise HTTPException(status_code=406, detail='Transport ID must only contain letters and numbers')

    @classmethod
    def from_dict(cls, data: Mapping):
        return cls(
            id=data['_id'],
            cargo_category=Category(data['cargo_category']),
            max_weight=data['max_weight']
        )

    def to_dict(self):
        return {
            '_id': self.id,
            'cargo_category': self.cargo_category.value,
            'max_weight': self.max_weight
        }
