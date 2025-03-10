from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from dependency_injector.wiring import Provide, inject

from containers import Container
from user.application.user_service import UserService
from user.domain.exceptions import UserNotFoundException, EmailAlreadyExistsException

router = APIRouter(prefix="/users", tags=["users"])

class CreatedUserBody(BaseModel):
    name: str
    email: str
    password: str

class UpdateUser(BaseModel):
    name: str | None
    password: str | None

@router.post("")
@inject
async def create_user(user: CreatedUserBody, user_service: UserService = Depends(Provide[Container.user_service])):
    try:
        created_user = user_service.create_user(user.name, user.email, user.password)
        return created_user
    except EmailAlreadyExistsException as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.put("/{user_id}")
@inject
async def update_user(user_id: str, user: UpdateUser, user_service: UserService = Depends(Provide[Container.user_service])):
    try:
        updated_user = user_service.update_user(user_id, user.name, user.password)
        return updated_user
    except UserNotFoundException as e:
        raise HTTPException(status_code=422, detail=str(e))

@router.get("")
@inject
def get_users(
    page: int = 1,
    items_per_page: int = 10,
    user_service: UserService = Depends(Provide[Container.user_service])):
    total, users = user_service.get_users(page, items_per_page)
    return {"total_count": total, "page":page, "users": users}

@router.delete("/{user_id}")
@inject
async def delete_user(user_id: str, user_service: UserService = Depends(Provide[Container.user_service])):
    try:
        deleted_user = user_service.delete_user(user_id)
        return deleted_user
    except UserNotFoundException as e:
        raise HTTPException(status_code=422, detail=str(e))