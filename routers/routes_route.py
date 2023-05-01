from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from classes.database import CollectionProvider
from classes.route import Route, RawRoute
from dependencies import get_current_active_user
from security.access_level import AccessLevel
from security.user import User

router = APIRouter()


@router.post("/routes/add")
async def add_route(route: RawRoute, current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.access_level != AccessLevel.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    transport = CollectionProvider.transports().find_one({"_id": route.transport})
    if not transport:
        raise HTTPException(status_code=400, detail="Transport not found")
    return CollectionProvider.routes().insert_one(Route.from_raw_route(route).to_dict()).inserted_id


@router.post("/routes/delete/{id}")
async def delete_route(id_: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.access_level != AccessLevel.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    if CollectionProvider.routes().delete_one({"_id": ObjectId(id_)}).deleted_count == 0:
        raise HTTPException(status_code=404, detail="Route not found")
    return {"message": "Route deleted"}
