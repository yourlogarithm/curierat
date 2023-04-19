from typing import Annotated
from datetime import timedelta, datetime
from fastapi import Depends, HTTPException, FastAPI, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

from classes.form import Form
from classes.route import Route
from classes.ticket import Ticket
from classes.transport import Transport
from security.access_level import AccessLevel
from security.user import User, RegisteredUser
from security.register_form import RegisterForm
from constants import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, JWT_TOKEN
from security.authorization import Validation
from security.token import Token, TokenData
from classes.database import CollectionProvider

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = Validation.authenticate_user(CollectionProvider.users(), form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = Token.create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_TOKEN, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = RegisteredUser.get(CollectionProvider.users(), token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: Annotated[User, Depends(get_current_user)]):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.get("/users/me")
async def read_users_me(current_user: Annotated[User, Depends(get_current_active_user)]):
    return current_user


@app.post("/users/register_client")
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


@app.post("/users/register_employee")
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


@app.post("/package/submit_form")
async def form(form_: Form, current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.access_level not in (AccessLevel.OFFICE | AccessLevel.ADMIN):
        raise HTTPException(status_code=403, detail="Forbidden")
    return Ticket.get_price(form_)


@app.post("/package/submit_ticket")
async def ticket(ticket_: Ticket, current_user: Annotated[User, Depends(get_current_active_user)], test: bool = False):
    if current_user.access_level not in (AccessLevel.OFFICE | AccessLevel.ADMIN):
        raise HTTPException(status_code=403, detail="Forbidden")
    destination = ticket_.destination
    current_timestamp = datetime.now()
    routes = CollectionProvider.routes().aggregate([
        {"$match": {
            "cities": {"$in": [destination]},
            "schedule": {"$gt": current_timestamp}
        }},
        {"$lookup": {
            "from": "transports",
            "localField": "transport",
            "foreignField": "_id", "as": "transport"
        }},
        {"$project": {
             "cities": 1,
             "transport": {"$arrayElemAt": ["$transport", 0]},
             "current_position": 1,
             "schedule": 1,
             "coordinates": 1
         }}
    ])
    if not test:
        CollectionProvider.tickets().insert_one(ticket_.dict())
    return {"message": "Ticket added"}


@app.post("/route/add")
async def add_route(route: Route, current_user: Annotated[User, Depends(get_current_active_user)], test: bool = False):
    if current_user.access_level != AccessLevel.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    transport = CollectionProvider.transports().find_one({"_id": route.transport})
    if not transport:
        raise HTTPException(status_code=400, detail="Transport not found")
    if not test:
        CollectionProvider.routes().insert_one(route.dict())
    return {"message": "Route added"}


@app.post("/route/delete")
async def delete_route(route: Route, current_user: Annotated[User, Depends(get_current_active_user)], test: bool = False):
    if current_user.access_level != AccessLevel.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    if not test:
        CollectionProvider.routes().delete_one({"_id": route._id})
    return {"message": "Route deleted"}


@app.post("/transport/add")
async def add_transport(transport: Transport, current_user: Annotated[User, Depends(get_current_active_user)],
                        test: bool = False):
    if current_user.access_level != AccessLevel.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    if not test:
        CollectionProvider.transports().insert_one(transport.dict())
    return {"message": "Transport added"}


@app.post("/transport/delete")
async def delete_transport(transport: Transport, current_user: Annotated[User, Depends(get_current_active_user)], test: bool = False):
    if current_user.access_level != AccessLevel.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    if not test:
        CollectionProvider.transports().delete_one({"_id": transport.id})
    return {"message": "Transport deleted"}
