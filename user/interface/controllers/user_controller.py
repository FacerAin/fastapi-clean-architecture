from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from dependency_injector.wiring import Provide, inject

from common.auth import CurrentUser, get_admin_user, get_current_user
from containers import Container
from user.application.user_service import UserService
from user.domain.exceptions import UserNotFoundException, EmailAlreadyExistsException

router = APIRouter(prefix="/users", tags=["users"])


class CreatedUserBody(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    email: EmailStr = Field(max_length=64)
    password: str = Field(min_length=8, max_length=32)


class UpdateUser(BaseModel):
    name: str | None = Field(min_length=2, max_length=32, default=None)
    password: str | None = Field(min_length=8, max_length=32, default=None)


class UpdateUserBody(BaseModel):
    name: str | None = Field(min_length=2, max_length=32, default=None)
    password: str | None = Field(min_length=8, max_length=32, default=None)


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime


class GetUsersResponse(BaseModel):
    total_count: int
    page: int
    users: list[UserResponse]


@router.post("")
@inject
async def create_user(
    user: CreatedUserBody,
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserResponse:
    try:
        created_user = user_service.create_user(user.name, user.email, user.password)
        return created_user
    except EmailAlreadyExistsException as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.put("", response_model=UserResponse)
@inject
def update_user(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    body_data: UpdateUserBody,
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    user = user_service.update_user(current_user.id, body_data.name, body_data.password)
    return user


@router.get("")
@inject
def get_users(
    page: int = 1,
    items_per_page: int = 10,
    current_user: CurrentUser = Depends(get_admin_user),
    user_service: UserService = Depends(Provide[Container.user_service]),
) -> GetUsersResponse:
    total, users = user_service.get_users(page, items_per_page)
    return {"total_count": total, "page": page, "users": users}  # type: ignore


@router.delete("", status_code=204)
@inject
async def delete_user(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    user_service.delete_user(current_user.id)


@router.post("/login")
@inject
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    user_service: UserService = Depends(Provide[Container.user_service]),
):
    access_token = user_service.login(
        email=form_data.username, password=form_data.password
    )
    return {"access_token": access_token, "token_type": "bearer"}
