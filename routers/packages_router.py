from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from classes.database_provider import DatabaseProvider
from classes.form import Form
from classes.package_status import PackageStatus
from classes.route import Route
from classes.package import Package
from dependencies import get_current_active_user
from security.access_level import AccessLevel
from security.user import User

router = APIRouter()


@router.post('/packages/calculate_price')
async def calculate_price(form_: Form, current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.access_level not in (AccessLevel.Admin, AccessLevel.Moderator, AccessLevel.Office):
        raise HTTPException(status_code=403, detail='Forbidden')
    return form_.price


@router.post('/packages/add')
async def add_package(package_: Package, current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.access_level not in (AccessLevel.Admin, AccessLevel.Moderator, AccessLevel.Office):
        raise HTTPException(status_code=403, detail='Forbidden')
    current_timestamp = datetime.now()
    routes = Route.get_best_routes(package_.office, package_.destination, current_timestamp)
    if len(routes) == 0:
        raise HTTPException(status_code=404, detail='No route found')
    best = next(route for route in routes if route.current_weight + package_.weight <= route.transport.max_weight)
    if best is None:
        raise HTTPException(status_code=400, detail='No transport available')
    best.add_package(package_)
    return {'package_code': package_.code, 'route_id': str(best.id)}


@router.get('/packages/{username}')
async def get_package(username: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.access_level < AccessLevel.Moderator:
        raise HTTPException(status_code=403, detail='Forbidden')
    packages = list(DatabaseProvider.routes().aggregate([
        {'$match': {'packages.username': username}},
        {'$unwind': '$packages'},
        {'$match': {'packages.username': username}},
    ]))
    return packages


@router.post('/packages/change_status/{package_code}')
async def change_package_status(package_code: str, status: PackageStatus, current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.access_level < AccessLevel.Moderator and current_user.access_level != AccessLevel.Courier:
        raise HTTPException(status_code=403, detail='Forbidden')
    update_result = DatabaseProvider.routes().update_one({'packages.code': package_code}, {'$set': {'packages.$.status': status}})
    if update_result.matched_count == 0:
        raise HTTPException(status_code=404, detail='Package not found')
    return update_result.raw_result
