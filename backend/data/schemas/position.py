from typing import Optional
from typing_extensions import Annotated

from pydantic import ConfigDict, BaseModel
from geoalchemy2.types import WKBElement

from .utils import to_camel


class PositionResponse(BaseModel):
    id: int


class PositionBase(BaseModel):
    start: Annotated[str, WKBElement]
    lost: Annotated[str, WKBElement]
    end: Annotated[str, WKBElement]
    start_radius: Optional[int] = None  # type: ignore
    lost_radius: Optional[int] = None
    end_radius: Optional[int] = None


class PositionUpdate(PositionBase):
    pass


class PositionCreate(PositionBase):
    start: str
    lost: str
    end: str
    start_radius: int
    lost_radius: int
    end_radius: int


class Position(PositionCreate):
    store_id: int
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, populate_by_name=True)
