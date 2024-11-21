from pydantic import BaseModel, Field
from app.users.models import UserRole


class SUser(BaseModel):
    nickname: str = Field(..., min_length=3, max_length=40,
                          description="Nickname from 3 to 40 characters")
    password: str = Field(..., min_length=8, max_length=72,
                          description="Password from 8 to 72 characters")
class SUserWithRole(SUser):
    role: UserRole = Field(..., description="User role")