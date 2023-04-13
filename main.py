from fastapi import FastAPI
from classes.form import Form
from pymongo import MongoClient

from classes.ticket import Ticket

app = FastAPI()
db = MongoClient("mongodb://localhost:27017/")


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/form")
async def form(form_: Form):
    price = Ticket.get_price(form_)
    return {"price": price}
