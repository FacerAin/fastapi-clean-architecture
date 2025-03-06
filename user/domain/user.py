from dataclasses import dataclass
from datetime import datetime


@dataclass
class Profile:
    # 데이터만 가지고 있는 도메인 객체를 Value Object(VO)라고 한다.
    name: str
    email: str

@dataclass
class User:
    id: str
    profile: Profile
    password: str
    created_at: datetime
    updated_at: datetime