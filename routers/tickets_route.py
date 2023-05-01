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


@router.post("/tickets/calculate_price")
async def calculate_price(form_: Form, current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.access_level not in _BASE_ACCESS_LEVELS + _PRIVILEGED_ACCESS_LEVELS:
        raise HTTPException(status_code=403, detail="Forbidden")
    return Ticket.get_price(form_)


@router.post("/tickets/add")
async def ticket(ticket_: Ticket, current_user: Annotated[User, Depends(get_current_active_user)]):
    if current_user.access_level not in _BASE_ACCESS_LEVELS + _PRIVILEGED_ACCESS_LEVELS:
        raise HTTPException(status_code=403, detail="Forbidden")
    current_timestamp = datetime.now()
    routes = list(CollectionProvider.routes().aggregate([
        {
            "$match": {
                "cities": {"$all": [ticket_.office, ticket_.destination]},
                "schedule": {"$gt": current_timestamp}
            },
        },
        {
            "$project": {
                "office_index": {"$indexOfArray": ["$cities", ticket_.office]},
                "destination_index": {"$indexOfArray": ["$cities", ticket_.destination]},
                "transport": 1,
                "coordinates": 1,
                "schedule": 1,
                "current_position": 1
            }
        },
        {"$match": {"$expr": {"$lt": ["$office_index", "$destination_index"]}}},
        {"$match": {"$expr": {"$lte": ["$office_index", "$current_position"]}}},
        {"$sort": {"schedule": 1}}
    ]))
    if len(routes) == 0:
        raise HTTPException(status_code=404, detail="No route found")

    return str(CollectionProvider.tickets().insert_one(ticket_.to_dict()).inserted_id)


@router.get("/tickets/{ticket_id}")
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
