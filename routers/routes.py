from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from classes.database import CollectionProvider
from classes.route import Route
from dependencies import get_current_active_user
from security.access_level import AccessLevel
from security.user import User

router = APIRouter()


@router.post("/routes/add")
async def add_route(route: Route, current_user: Annotated[User, Depends(get_current_active_user)], test: bool = False):
    if current_user.access_level != AccessLevel.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    transport = CollectionProvider.transports().find_one({"_id": route.transport})
    if not transport:
        raise HTTPException(status_code=400, detail="Transport not found")
    if not test:
        CollectionProvider.routes().insert_one(route.dict())
    return {"message": "Route added"}


@router.post("/routes/delete")
async def delete_route(route: Route, current_user: Annotated[User, Depends(get_current_active_user)], test: bool = False):
    if current_user.access_level != AccessLevel.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    if not test:
        CollectionProvider.routes().delete_one({"_id": route._id})
    return {"message": "Route deleted"}