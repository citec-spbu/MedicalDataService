from pydantic import BaseModel, Field, field_validator
from app.users.models import UserRole
from fastapi import HTTPException, status


class SUser(BaseModel):
    nickname: str = Field(..., description="Nickname from 3 to 40 characters")
    password: str = Field(..., description="Password from 8 to 72 characters")

    @field_validator('nickname')
    def validate_nickname(cls, value):
        if len(value) < 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nickname must be at least 3 characters long"
            )
        if len(value) > 40:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Nickname must not exceed 40 characters"
            )
        return value

    @field_validator('password')
    def validate_password(cls, value):
        if len(value) < 8:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must be at least 8 characters long"
            )
        if len(value) > 72:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must not exceed 72 characters"
            )
        return value

class SUserWithRole(SUser):
    role: UserRole = Field(..., description="User role")