from fastapi import APIRouter
from app.users.dao import UserDAO


router = APIRouter(prefix="/user", tags=["Authorization and registration"])


@router.post("/register/")
async def register_user(nickname: str, password: str) -> dict:
    # TODO add validation on user existence
    await UserDAO.add_student(nickname=nickname, password=password)
    return {"message": "You have registered successfully!"}
