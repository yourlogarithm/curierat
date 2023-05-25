from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from classes.database_provider import DatabaseProvider
from classes.route import Route
from classes.raw_route import RawRoute
from dependencies import get_current_active_user
from security.access_level import AccessLevel
from security.user import User


class RoutesRouter:
    router = APIRouter()

    @staticmethod
    @router.get('/routes')
    async def get_routes(current_user: Annotated[User, Depends(get_current_active_user)]):
        routes = list(DatabaseProvider.routes().find())
        for route in routes:
            route['_id'] = str(route['_id'])
        return routes

    @staticmethod
    @router.post('/routes/add')
    async def add_route(route: RawRoute, current_user: Annotated[User, Depends(get_current_active_user)]):
        if current_user.access_level < AccessLevel.Admin:
            raise HTTPException(status_code=403, detail='Forbidden')
        if len(route.cities) <= 1 or route.cities[0] == route.cities[-1]:
            raise HTTPException(status_code=400, detail='Invalid route')
        transport = DatabaseProvider.transports().find_one({'_id': route.transport})
        if not transport:
            raise HTTPException(status_code=400, detail='Transport not found')
        return str(DatabaseProvider.routes().insert_one(Route.from_raw_route(route).to_dict()).inserted_id)

    @staticmethod
    @router.delete('/routes/delete/{id}')
    async def delete_route(id_: str, current_user: Annotated[User, Depends(get_current_active_user)]):
        if current_user.access_level < AccessLevel.Moderator:
            raise HTTPException(status_code=403, detail='Forbidden')
        if DatabaseProvider.routes().delete_one({'_id': ObjectId(id_)}).deleted_count == 0:
            raise HTTPException(status_code=404, detail='Route not found')
        return {'message': 'Route deleted'}

    @staticmethod
    @router.get('/routes/package/{package_code}')
    async def get_route_of_package_code(package_code: str, current_user: Annotated[User, Depends(get_current_active_user)]):
        route = DatabaseProvider.routes().find_one({'packages.code': package_code})
        if route is None:
            raise HTTPException(status_code=404, detail='Package not found')
        route['_id'] = str(route['_id'])
        return route

    @staticmethod
    @router.post('/routes/increment_position')
    async def increment_position(route_id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
        if current_user.access_level < AccessLevel.Moderator and current_user.access_level != AccessLevel.Courier:
            raise HTTPException(status_code=403, detail='Forbidden')
        route = DatabaseProvider.routes().find_one({'_id': ObjectId(route_id)})
        if route is None:
            raise HTTPException(status_code=404, detail='Route not found')
        route = Route.from_dict(route)
        route.increment_position()
        return {'message': 'Position incremented'}
