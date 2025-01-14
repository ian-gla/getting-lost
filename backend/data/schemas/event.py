from pydantic import ConfigDict, BaseModel

from .utils import to_camel


class EventResponse(BaseModel):
    id: int


class EventBase(BaseModel):
    position: int
    user: int
    when: str
    time_of_day: str
    day_of_week: str
    guidance: str
    group: str
    factors: str
    familiarity: str
    context: str
    explain: str


class EventUpdate(EventBase):
    pass


class EventCreate(EventBase):
    position: int
    user: int
    when: str
    time_of_day: str
    day_of_week: str
    guidance: str
    group: str
    factors: str
    familiarity: str
    context: str
    explain: str


class Event(EventCreate):
    id: int
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)
