from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from classes.database import DatabaseProvider
from classes.transport import Transport
from dependencies import get_current_active_user
from security.access_level import AccessLevel
from security.user import User

router = APIRouter()


@router.post("/transports/add")
async def add_transport(transport: Transport, current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.access_level != AccessLevel.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    return DatabaseProvider.transports().insert_one(transport.dict()).inserted_id


@router.post("/transports/delete/{transport_id}")
async def delete_transport(transport_id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.access_level != AccessLevel.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    if DatabaseProvider.transports().delete_one({"_id": transport_id}).deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transport not found")
    return {"message": "Transport deleted"}
