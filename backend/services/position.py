import data.models as models
from data.session import create_session
from data.schemas.position import Position
from geoalchemy2.shape import to_shape
from sqlalchemy.exc import IntegrityError
from data.exceptions import BadRequest, Missing


def create_position(position: Position) -> int | None:
    try:
        db = create_session()
        new_pos = models.Positions(
            start=position.start,
            lost=position.lost,
            end=position.end,
            start_radius=position.start_radius,
            lost_radius=position.lost_radius,
            end_radius=position.end_radius,
        )
        db.add(new_pos)
        db.commit()
        db.refresh(new_pos)
        id = new_pos.id
        return id
    except IntegrityError as e:
        db.rollback()
        raise BadRequest(e.value.message)
    finally:
        db.close()


def update_position(position_id: int, position: Position) -> Position:
    try:
        db = create_session()
        pos = db.query(models.Positions).filter(models.Positions.id == position_id).first()
        if not pos:
            raise Missing(f"Position {position_id} not found")
        pos.start = position.start
        pos.lost = position.lost
        pos.end = position.end
        pos.start_radius = position.start_radius
        pos.lost_radius = position.lost_radius
        pos.end_radius = position.end_radius
        db.commit()
        db.refresh(pos)
        pos.start = to_shape(pos.start).wkt
        pos.end = to_shape(pos.end).wkt
        pos.lost = to_shape(pos.lost).wkt
        return pos
    except IntegrityError:
        db.rollback()
        raise BadRequest("bad request body")
    finally:
        db.close()
