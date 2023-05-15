from typing import Mapping
from hashlib import md5

from .contact import Contact
from .category import Category
from .form import Form
from .package_status import PackageStatus


class Package(Form):
    status: PackageStatus = PackageStatus.TRANSIT
    code: str = None

    def __init__(self, **data):
        super().__init__(**data)
        self.status = self.status or PackageStatus.TRANSIT
        self.code = self.code or md5(str(self).encode()).hexdigest()

    @classmethod
    def from_dict(cls, data: Mapping):
        return cls(sender_contact=Contact(**data['sender_contact']), receiver_contact=Contact(**data['receiver_contact']),
                   office=data['office'], destination=data['destination'], weight=data['weight'],
                   category=Category(data['category']), price=data['price'], status=PackageStatus(data['status']),
                   code=data['code'])

    def to_dict(self):
        form_dict = super().to_dict()
        form_dict['price'] = self.price
        form_dict['status'] = self.status
        form_dict['code'] = self.code
        return form_dict



    
