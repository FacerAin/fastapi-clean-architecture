from datetime import datetime
from user.domain.user import User

def test_user_creation():
    user = User(
        id="ID_TEST",
        name="Test User",
        email="example@example.com",
        password="123456",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        memo=None)
    
    assert user.id == "ID_TEST"
    assert user.name == "Test User"
    assert user.email == "example@example.com"
    assert user.password == "123456"
    assert user.memo == None