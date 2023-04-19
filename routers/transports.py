from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from classes.database import CollectionProvider
from classes.transport import Transport
from dependencies import get_current_active_user
from security.access_level import AccessLevel
from security.user import User

router = APIRouter()


@router.post("/transports/add")
async def add_transport(transport: Transport, current_user: Annotated[User, Depends(get_current_active_user)],
                        test: bool = False):
    if current_user.access_level != AccessLevel.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    if not test:
        CollectionProvider.transports().insert_one(transport.dict())
    return {"message": "Transport added"}


@router.post("/transports/delete")
async def delete_transport(transport: Transport, current_user: Annotated[User, Depends(get_current_active_user)], test: bool = False):
    if current_user.access_level != AccessLevel.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    if not test:
        CollectionProvider.transports().delete_one({"_id": transport.id})
    return {"message": "Transport deleted"}