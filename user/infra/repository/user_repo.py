from fastapi import HTTPException
from user.domain.repository.user_repo import IUserRepository
from database import SessionLocal
from user.domain.user import User as UserVO
from user.infra.db_models.user import User
from utils.db_utils import row_to_dict


class UserRepository(IUserRepository):
    def save(self, user: UserVO):
        new_user = User(
            id=user.id,
            name=user.name,
            email=user.email,
            password=user.password,
            created_at=user.created_at,
            updated_at=user.updated_at,
            memo=user.memo
        )

        with SessionLocal() as session:
            session.add(new_user)
            session.commit()
        
    def find_by_email(self, email: str) -> UserVO:
        with SessionLocal() as session:
            user = session.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=422, detail="User not found")
        return UserVO(**row_to_dict(user))
    
    def find_by_id(self, id: str) -> UserVO:
        with SessionLocal() as session:
            user = session.query(User).filter(User.id == id).first()
        if not user:
            raise HTTPException(status_code=422, detail="User not found")
        
        return UserVO(**row_to_dict(user))
    
    def update(self, user: UserVO):
        with SessionLocal() as session:
            session.query(User).filter(User.id == user.id).update({
                "name": user.name,
                "password": user.password,
                "updated_at": user.updated_at,
                "memo": user.memo
            })
            session.commit()
        
        return user
    
    def get_users(self,
                  page: int = 1,
                  items_per_page: int = 10) -> tuple[int, list[UserVO]]:
        with SessionLocal() as session:
            query = session.query(User)
            total = query.count()
            offset = (page - 1) * items_per_page
            users = query.offset(offset).limit(items_per_page).all()
        return total, [UserVO(**row_to_dict(user)) for user in users]
    
    def delete(self, id: str):
        with SessionLocal() as session:
            session.query(User).filter(User.id == id).delete()
            session.commit()
            
