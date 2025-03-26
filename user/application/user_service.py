from datetime import datetime

from fastapi import BackgroundTasks, HTTPException
from fastapi import status

from common.auth import Role, create_access_token
from user.application.email_service import EmailService
from user.application.send_welcome_email_task import SendWelcomeEmailTask
from user.domain.exceptions import UserNotFoundException, EmailAlreadyExistsException
from ulid import ULID  # type: ignore
from user.domain.repository.user_repo import IUserRepository
from user.domain.user import User
from utils.crypto import Crypto
from dependency_injector.wiring import inject


class UserService:
    @inject
    def __init__(self, user_repo: IUserRepository, email_service: EmailService, ulid: ULID, crypto: Crypto, send_welcome_email_task: SendWelcomeEmailTask):
        self.user_repo = user_repo
        self.ulid = ulid
        self.crypto = crypto
        self.send_welcome_email_task = send_welcome_email_task

    def create_user(self, name: str, email: str, password: str, memo: str|None = None):
        _user = None

        try:
            _user = self.user_repo.find_by_email(email)
        except Exception as e:
            if getattr(e, "status_code", None) != 422:
                raise e

        if _user:
            raise EmailAlreadyExistsException("Email already exists")

        now = datetime.now()
        user: User = User(
            id=self.ulid.generate(),
            name=name,
            email=email,
            password=self.crypto.encrypt(password),
            created_at=now,
            updated_at=now,
            memo=memo,
        )
        self.user_repo.save(user)

        self.send_welcome_email_task.delay(user.email)
        return user

    def update_user(
        self, user_id: str, name: str | None = None, password: str | None = None
    ):
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundException("User not found")

        if name:
            user.name = name
        if password:
            user.password = self.crypto.encrypt(password)

        user.updated_at = datetime.now()
        self.user_repo.update(user)
        return user

    def get_users(self, page: int, items_per_page: int) -> tuple[int, list[User]]:
        return self.user_repo.get_users(page, items_per_page)

    def delete_user(self, user_id: str):
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise UserNotFoundException("User not found")

        self.user_repo.delete(user_id)
        return user

    def login(self, email: str, password: str):
        user = self.user_repo.find_by_email(email)

        if not self.crypto.verify(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
            )
        access_token = create_access_token({"user_id": user.id}, role=Role.USER)
        return access_token
