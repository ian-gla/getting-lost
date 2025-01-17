import services.event
from data.schemas.event import EventCreate, EventResponse, EventUpdate, Event
from fastapi import HTTPException
from fastapi.routing import APIRouter
from data.exceptions import BadRequest, Missing

router = APIRouter(prefix="/event")


@router.post("/")
async def create(event: EventCreate) -> EventResponse:
    try:
        id = services.event.create_event(event)
        return {"id": id}
    except BadRequest as e:
        raise HTTPException(404, e.message)


@router.put("/{event_id}")
async def update(event_id: int, event: EventUpdate) -> Event:
    if event_id < 0:
        raise HTTPException(404, "Bad ID")
    try:
        event = services.event.update_event(event_id, event)
        return event
    except Missing as e:
        raise HTTPException(404, e.message)
