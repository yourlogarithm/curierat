from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

from classes.database import CollectionProvider
from classes.form import Form
from classes.ticket import Ticket
from dependencies import get_current_active_user
from security.access_level import AccessLevel
from security.user import User

router = APIRouter()


@router.post("/packages/submit_form")
async def form(form_: Form, current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.access_level not in (AccessLevel.OFFICE | AccessLevel.ADMIN):
        raise HTTPException(status_code=403, detail="Forbidden")
    return Ticket.get_price(form_)


@router.post("/packages/submit_ticket")
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
