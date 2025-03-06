from fastapi import APIRouter
from pydantic import BaseModel

from user.application.user_service import UserService

router = APIRouter(prefix="/users")

class CreatedUserBody(BaseModel):
    name: str
    email: str
    password: str

@router.post("", status_code=201)
def create_user(user: CreatedUserBody):
    user_service = UserService()
    created_user = user_service.create_user(user.name, user.email, user.password)
    return created_user
