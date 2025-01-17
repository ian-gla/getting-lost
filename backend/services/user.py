import data.models as models
from data.session import create_session
from data.schemas.user import User
from sqlalchemy.exc import IntegrityError
from data.exceptions import BadRequest, Missing


def create_user(user: User) -> int:
    try:
        db = create_session()
        new_user = models.Users(
            age=user.age, gender=user.gender, nav_skill=user.nav_skill, position=user.position
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        id = new_user.id
        return id
    except IntegrityError:
        db.rollback()
        raise BadRequest("bad request body")
    finally:
        db.close()


def update_user(user_id: int, user: User) -> User:
    if user_id < 0:
        raise BadRequest("Bad ID")
    try:
        db = create_session()
        print(f"{db.bind.engine.url.database=}")
        print(f"{user_id=}")
        u = db.query(models.Users).filter(models.Users.id == user_id).first()
        if not u:
            db.rollback()
            db.close()
            raise Missing(f"User id {user_id} not found")
        u.age = user.age
        u.gender = user.gender
        u.nav_skill = user.nav_skill
        db.commit()
        db.refresh(u)
        return u
    except IntegrityError:
        db.rollback()
        raise BadRequest("bad request body")
    finally:
        db.close()
