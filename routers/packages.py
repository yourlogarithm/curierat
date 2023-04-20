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

_BASE_ACCESS_LEVELS = AccessLevel.OFFICE,
_PRIVILEGED_ACCESS_LEVELS = AccessLevel.OFFICE, AccessLevel.ADMIN


@router.post("/packages/calculate_price")
async def calculate_price(form_: Form, current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.access_level not in _BASE_ACCESS_LEVELS + _PRIVILEGED_ACCESS_LEVELS:
        raise HTTPException(status_code=403, detail="Forbidden")
    return Ticket.get_price(form_)


@router.post("/packages/tickets/add")
async def ticket(ticket_: Ticket, current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.access_level not in _BASE_ACCESS_LEVELS + _PRIVILEGED_ACCESS_LEVELS:
        raise HTTPException(status_code=403, detail="Forbidden")
    destination = ticket_.destination
    current_timestamp = datetime.now()
    # TODO: Search for best route in terms of delivery time and category of transport
    routes = list(CollectionProvider.routes().aggregate([
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
    ]))
    return CollectionProvider.tickets().insert_one(ticket_.dict()).inserted_id


@router.get("/packages/tickets/{ticket_id}")
async def ticket(ticket_id: str, current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.access_level not in _PRIVILEGED_ACCESS_LEVELS:
        raise HTTPException(status_code=403, detail="Forbidden")
    return CollectionProvider.tickets().find_one({"_id": ticket_id})


@router.post("/packages/tickets/update_status/{ticket_id}")
async def ticket(ticket_id: str, closed: bool, current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.access_level not in _PRIVILEGED_ACCESS_LEVELS:
        raise HTTPException(status_code=403, detail="Forbidden")
    CollectionProvider.tickets().update_one({"_id": ticket_id}, {"$set": {"closed": closed}})
    return {"message": "Ticket status updated"}
