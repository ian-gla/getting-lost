import services.position as position
from data.schemas.position import PositionCreate, PositionResponse, PositionUpdate, Position
from fastapi import HTTPException
from fastapi.routing import APIRouter
from data.exceptions import BadRequest, Missing
import logging

router = APIRouter(prefix="/position")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/")
async def create(posit: PositionCreate) -> PositionResponse:
    logger.info("Post called")
    try:
        id = position.create_position(posit)
        return {"id": id}
    except BadRequest as e:
        raise HTTPException(404, e.message)


@router.put("/{position_id}")
async def update(position_id: int, posit: PositionUpdate) -> Position:
    if position_id < 0:
        raise HTTPException(404, "Bad ID")
    try:
        pos = position.update_position(position_id, posit)
        return pos
    except Missing as e:
        raise HTTPException(404, e.message)
