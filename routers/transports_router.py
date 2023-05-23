from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from classes.database_provider import DatabaseProvider
from classes.transport import Transport
from dependencies import get_current_active_user
from security.access_level import AccessLevel
from security.user import User


class TransportsRouter:
    router = APIRouter()

    @staticmethod
    @router.post('/transports/add')
    async def add_transport(transport: Transport, current_user: Annotated[User, Depends(get_current_active_user)]):
        if current_user.access_level < AccessLevel.Moderator:
            raise HTTPException(status_code=403, detail='Forbidden')
        DatabaseProvider.transports().insert_one(transport.to_dict())
        return {'message': 'Transport added'}

    @staticmethod
    @router.get('/transports')
    async def get_transports(current_user: Annotated[User, Depends(get_current_active_user)]):
        if current_user.access_level < AccessLevel.Moderator:
            raise HTTPException(status_code=403, detail='Forbidden')
        return list(DatabaseProvider.transports().find())

    @staticmethod
    @router.delete('/transports/delete/{transport_id}')
    async def delete_transport(transport_id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
        if current_user.access_level < AccessLevel.Moderator:
            raise HTTPException(status_code=403, detail='Forbidden')
        if DatabaseProvider.transports().delete_one({'_id': transport_id}).deleted_count == 0:
            raise HTTPException(status_code=404, detail='Transport not found')
        return {'message': 'Transport deleted'}
