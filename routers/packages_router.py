from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from classes.contact import Contact
from classes.database_provider import DatabaseProvider
from classes.form import Form
from classes.package_status import PackageStatus
from classes.route import Route
from classes.package import Package
from classes.transport import Transport
from dependencies import get_current_active_user
from security.access_level import AccessLevel
from security.user import User


class PackagesRouter:
    router = APIRouter()

    @staticmethod
    def _get_by_code(code: str):
        packages = list(DatabaseProvider.routes().aggregate([
            {'$match': {'packages.code': code}},
            {'$unwind': '$packages'},
            {'$match': {'packages.code': code}},
        ]))
        if len(packages) == 0:
            raise HTTPException(status_code=404, detail='No packages found')
        return packages[0]['packages']

    @staticmethod
    def _get_best_route_from_form(form_: Form):
        current_timestamp = datetime.now()
        routes = Route.get_best_routes(form_.office, form_.destination, current_timestamp)
        if len(routes) == 0:
            raise HTTPException(status_code=400, detail='No route found')
        best = None
        for route in routes:
            transport = Transport.from_dict(DatabaseProvider.transports().find_one({'_id': route.transport}))
            if route.current_weight + form_.weight <= transport.max_weight and transport.cargo_category == form_.category:
                best = route
                break
        if best is None:
            raise HTTPException(status_code=400, detail='No route available')
        return best

    @staticmethod
    @router.post('/packages/calculate_price')
    async def calculate_price(form_: Form, current_user: Annotated[User, Depends(get_current_active_user)]):
        if current_user.access_level not in (AccessLevel.Admin, AccessLevel.Moderator, AccessLevel.Office):
            raise HTTPException(status_code=403, detail='Forbidden')
        return form_.price

    @staticmethod
    @router.post('/packages/get_best_route')
    async def get_best_route(form_: Form, current_user: Annotated[User, Depends(get_current_active_user)]):
        if current_user.access_level not in (AccessLevel.Admin, AccessLevel.Moderator, AccessLevel.Office):
            raise HTTPException(status_code=403, detail='Forbidden')
        return PackagesRouter._get_best_route_from_form(form_).to_dict()

    @staticmethod
    @router.post('/packages/add')
    async def add_package(package_: Package, current_user: Annotated[User, Depends(get_current_active_user)]):
        if current_user.access_level not in (AccessLevel.Admin, AccessLevel.Moderator, AccessLevel.Office):
            raise HTTPException(status_code=403, detail='Forbidden')
        best = PackagesRouter._get_best_route_from_form(package_)
        best.add_package(package_)
        return {'package_code': package_.code, 'route_id': str(best.id)}

    @staticmethod
    @router.post('/packages/get_by_contact')
    async def get_package_by_contact(contact: Contact, current_user: Annotated[User, Depends(get_current_active_user)]):
        if current_user.access_level < AccessLevel.Moderator:
            raise HTTPException(status_code=403, detail='Forbidden')
        packages = list(DatabaseProvider.routes().aggregate([
            {'$match': {'packages.sender_contact': contact.dict()}},
            {'$unwind': '$packages'},
            {'$match': {'packages.sender_contact': contact.dict()}},
            {'$project': {'_id': 1, 'packages': 1}}
        ]))
        if len(packages) == 0:
            raise HTTPException(status_code=404, detail='No packages found')
        result = []
        for package in packages:
            entry = {'_id': str(package['_id'])}
            entry.update(package['packages'])
            result.append(entry)
        return result

    @staticmethod
    @router.post('/packages/get_by_code')
    async def get_package_by_code(code: str, current_user: Annotated[User, Depends(get_current_active_user)]):
        if current_user.access_level < AccessLevel.Moderator:
            raise HTTPException(status_code=403, detail='Forbidden')
        return PackagesRouter._get_by_code(code)

    @staticmethod
    @router.post('/packages/change_status/{package_code}')
    async def change_package_status(package_code: str, status: PackageStatus, current_user: Annotated[User, Depends(get_current_active_user)]):
        if current_user.access_level < AccessLevel.Moderator and current_user.access_level != AccessLevel.Courier:
            raise HTTPException(status_code=403, detail='Forbidden')
        update_result = DatabaseProvider.routes().update_one({'packages.code': package_code}, {'$set': {'packages.$.status': status}})
        if update_result.matched_count == 0:
            raise HTTPException(status_code=404, detail='Package not found')
        package = Package.from_dict(PackagesRouter._get_by_code(package_code))
        if package.status == PackageStatus.WaitingReceiver:
            package.receiver_contact.notify()
        elif package.status == PackageStatus.WaitingSender:
            package.sender_contact.notify()
        return {'status': 'ok'}
