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

class UpdateUser(BaseModel):
    name: str | None
    password: str | None

@router.post("", status_code=201)
@inject
def create_user(user: CreatedUserBody, user_service: UserService = Depends(Provide[Container.user_service])):
    created_user = user_service.create_user(user.name, user.email, user.password)
    return created_user

@router.put("/{user_id}")
@inject
def update_user(user_id: str, user: UpdateUser, user_service: UserService = Depends(Provide[Container.user_service])):
    updated_user = user_service.update_user(user_id, user.name, user.password)
    return updated_user

@router.get("")
@inject
def get_users(
    page: int = 1,
    items_per_page: int = 10,
    user_service: UserService = Depends(Provide[Container.user_service])):
    total, users = user_service.get_users(page, items_per_page)
    return {"total_count": total, "page":page, "users": users}