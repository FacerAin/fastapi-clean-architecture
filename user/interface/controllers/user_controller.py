from fastapi import APIRouter, Depends
from pydantic import BaseModel
from dependency_injector.wiring import Provide, inject

from containers import Container
from user.application.user_service import UserService

router = APIRouter(prefix="/users")

class CreatedUserBody(BaseModel):
    name: str
    email: str
    password: str

@router.post("", status_code=201)
@inject
def create_user(user: CreatedUserBody, user_service: UserService = Depends(Provide[Container.user_service])):
    created_user = user_service.create_user(user.name, user.email, user.password)
    return created_user
