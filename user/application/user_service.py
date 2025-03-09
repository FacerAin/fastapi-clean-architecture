from datetime import datetime

from fastapi import HTTPException
from ulid import ULID  # type: ignore
from user.domain.repository.user_repo import IUserRepository
from user.domain.user import User
from utils.crypto import Crypto
from dependency_injector.wiring import inject


class UserService:
    @inject
    def __init__(self, user_repo: IUserRepository):
        self.user_repo = user_repo
        self.ulid = ULID() # 정렬 가능한 범용 고유 식별자 ( Universally Unique Lexicographically Sortable Identifier ) -> 정렬이 가능하므로, 검색 속도 향상 가능
        self.crypto = Crypto()

    def create_user(self, name: str, email: str, password: str):
        _user = None

        try:
            _user = self.user_repo.find_by_email(email)
        except Exception as e:
            if getattr(e, "status_code", None) != 422:
                raise e
        
        if _user:
            raise HTTPException(status_code=422, detail="Email already exists")
        
        now = datetime.now()
        user: User = User(
            id=self.ulid.generate(),
            name=name,
            email=email,
            password=self.crypto.encrypt(password),
            created_at=now,
            updated_at=now,
            memo=user.memo,
        )
        self.user_repo.save(user)
        return user
    
    def update_user(self, user_id: str, name: str | None = None, password: str | None = None):
        user = self.user_repo.find_by_id(user_id)
        if not user:
            raise HTTPException(status_code=422, detail="User not found")
        
        if name:
            user.name = name
        if password:
            user.password = self.crypto.encrypt(password)
        
        user.updated_at = datetime.now()
        self.user_repo.update(user)
        return user
    
    def get_users(self, page: int, items_per_page: int) -> tuple[int, list[User]]:
        return self.user_repo.get_users(page, items_per_page)