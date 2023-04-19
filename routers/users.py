from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from classes.database import CollectionProvider
from dependencies import get_current_active_user
from security.access_level import AccessLevel
from security.register_form import RegisterForm
from security.user import User, RegisteredUser

router = APIRouter()


@router.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@router.post("/users/register_client")
async def register_client(register_form: RegisterForm, test: bool = False):
    if register_form.access_level != AccessLevel.CLIENT:
        raise HTTPException(status_code=403, detail="Forbidden")
    user = RegisteredUser.get(CollectionProvider.users(), register_form.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = register_form.to_user()
    if not test:
        CollectionProvider.users().insert_one(user.dict())
    return {"message": "Client registered"}


@router.post("/users/register_employee")
async def register_employee(register_form: RegisterForm,
                            current_user: Annotated[User, Depends(get_current_active_user)], test: bool = False):
    if register_form.access_level == AccessLevel.CLIENT or current_user.access_level != AccessLevel.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    user = RegisteredUser.get(CollectionProvider.users(), register_form.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = register_form.to_user()
    if not test:
        CollectionProvider.users().insert_one(user.dict())
    return {"message": "Employee registered"}