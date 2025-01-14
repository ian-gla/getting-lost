from fastapi import FastAPI, HTTPException
import data.models as models
from data.session import create_session
from data.schemas.position import PositionCreate, PositionResponse, PositionUpdate, Position
from data.schemas.user import UserCreate, UserResponse, UserUpdate, User
from data.schemas.event import EventCreate, EventResponse, EventUpdate, Event
from geoalchemy2.shape import to_shape


def create_app() -> FastAPI:
    app = FastAPI(
        title="getting-lost",
        description="Simple API to handle getting-lost app responses",
        version="1.0",
    )

    @app.post("/position/")
    async def create_position(position: PositionCreate) -> PositionResponse:
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
        db.close()
        return {"id": id}

    @app.put("/position/{position_id}")
    async def update_postion(position_id: int, position: PositionUpdate) -> Position:
        db = create_session()
        pos = db.query(models.Positions).filter(models.Positions.id == position_id).first()
        if not pos:
            db.close()
            raise HTTPException(404, "Position not found")
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
        db.close()
        return pos

    # Create an user
    @app.post("/user/")
    async def create_user(user: UserCreate) -> UserResponse:
        db = create_session()
        new_user = models.Users(
            age=user.age, gender=user.gender, nav_skill=user.nav_skill, position=user.position
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        id = new_user.id
        db.close()
        return {"id": id}

    @app.put("/user/{user_id}")
    async def update_user(user_id: int, user: UserUpdate) -> User:
        db = create_session()
        u = db.query(models.Users).filter(models.Users.id == user_id).first()
        if not u:
            db.rollback()
            db.close()
            raise HTTPException(404, "User not found")
        u.age = user.age
        u.gender = user.gender
        u.nav_skill = user.nav_skill
        db.commit()
        db.refresh(u)
        db.close()
        return u

    # Create an event
    @app.post("/event/")
    async def create_event(event: EventCreate) -> EventResponse:
        db = create_session()
        new_event = models.Events(
            user=event.user,
            position=event.position,
            when=event.when,
            time_of_day=event.time_of_day,
            day_of_week=event.day_of_week,
            guidance=event.guidance,
            group=event.group,
            factors=event.factors,
            familiarity=event.familiarity,
            context=event.context,
            explain=event.explain,
        )
        db.add(new_event)
        db.commit()
        db.refresh(new_event)
        id = new_event.id
        db.close()
        return {"id": id}

    @app.put(
        "/event/{event_id}",
        responses={404: {"description": "Event not found"}},
    )
    async def update_event(event_id: int, event: EventUpdate) -> Event:
        db = create_session()
        e = db.query(models.Events).filter(models.Events.id == event_id).first()
        if not e:
            db.close()
            raise HTTPException(status_code=404, detail="Event not found")
        e.user = event.user
        e.position = event.position
        e.when = event.when
        e.time_of_day = event.time_of_day
        e.day_of_week = event.day_of_week
        e.guidance = event.guidance
        e.group = event.group
        e.factors = event.factors
        e.familiarity = str(event.familiarity)
        e.context = event.context
        e.explain = event.explain
        db.commit()
        db.refresh(e)
        e.familiarity = str(e.familiarity)
        db.close()
        return e

    return app
