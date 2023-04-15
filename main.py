from typing import Annotated
from datetime import timedelta
from fastapi import Depends, HTTPException, FastAPI, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from pymongo import MongoClient
from classes.form import Form
from classes.ticket import Ticket
from security.user import User, RegisteredUser
from security.register_form import RegisterForm
from constants import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, JWT_TOKEN
from security.authorization import Validation
from security.token import Token, TokenData

app = FastAPI()
db = MongoClient("mongodb://localhost:27017/")["curierat"]
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/form")
async def form(form_: Form):
    price = Ticket.get_price(form_)
    return {"price": price}


@app.post("/ticket")
async def ticket(ticket_: Ticket):
    db.tickets.insert_one(ticket_.dict())
    return {"message": "Ticket added"}


@app.post("/token")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user = Validation.authenticate_user(db["users"], form_data.username, form_data.password)
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
    user = RegisteredUser.get(db["users"], token_data.username)
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
async def register_client(register_form: RegisterForm):
    user = RegisteredUser.get(db["users"], register_form.username)
    if user:
        raise HTTPException(status_code=400, detail="Username already registered")
    user = register_form.to_user()
    db["users"].insert_one(user.dict())
    return {"message": "User registered"}
