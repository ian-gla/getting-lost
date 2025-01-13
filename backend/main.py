from fastapi import FastAPI
import data.models as models
from data.session import create_session
from data.schemas.position import PositionCreate, PositionResponse
from data.schemas.user import UserCreate, UserResponse


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

    return app


app = create_app()
