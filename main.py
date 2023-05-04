from typing import Annotated
from datetime import timedelta
from fastapi import Depends, HTTPException, FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from constants import ACCESS_TOKEN_EXPIRE_MINUTES
from security.authorization import Validation
from security.token import Token
from classes.database import DatabaseProvider
from routers import packages_router, routes_router, transports_router, users_router

app = FastAPI()

app.include_router(packages_router.router)
app.include_router(routes_router.router)
app.include_router(transports_router.router)
app.include_router(users_router.router)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = Validation.authenticate_user(DatabaseProvider.users(), form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = Token.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
