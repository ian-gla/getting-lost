import services.user
from data.schemas.user import UserCreate, UserResponse, UserUpdate, User
from fastapi import HTTPException
from fastapi.routing import APIRouter
from data.exceptions import BadRequest, Missing

router = APIRouter(prefix="/user")


@router.post("/")
async def create(user: UserCreate) -> UserResponse:
    try:
        id = services.user.create_user(user)
        return {"id": id}
    except BadRequest as e:
        raise HTTPException(404, e.message)


@router.put("/{user_id}")
async def update(user_id: int, user: UserUpdate) -> User:
    if user_id < 0:
        raise HTTPException(404, "Bad ID")
    try:
        user = services.user.update_user(user_id, user)
        return user
    except Missing as e:
        raise HTTPException(404, e.message)
