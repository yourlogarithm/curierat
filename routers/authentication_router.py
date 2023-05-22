from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from constants import ACCESS_TOKEN_EXPIRE_MINUTES
from security.token import Token
from security.validation import Validation


class AuthenticationRouter:
    router = APIRouter()

    @staticmethod
    @router.post('/token')
    async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
        user = Validation.authenticate_user(form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Incorrect username or password',
                headers={'WWW-Authenticate': 'Bearer'},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = Token.create_access_token(data={'sub': user.username}, expires_delta=access_token_expires)
        return {'access_token': access_token, 'token_type': 'bearer'}
