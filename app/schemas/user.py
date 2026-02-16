from uuid import UUID
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator, Field, model_validator
from app.schemas.base import *

class UserFilter(BasePaginationFilter):
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)  # Industry standard is usually 8+
    username: Optional[str] = Field(None, min_length=6, max_length=20)
    full_name: str = Field(..., min_length=1)
    
class UserUpdate(BaseModel):
    username: Optional[str] = Field("", min_length=6, max_length=20)
    full_name: Optional[str] = Field("", min_length=1)

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    username: Optional[str] = None
    password: str
    full_name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: bool = False

    model_config = ConfigDict(from_attributes=True)

class UserPublicResponse(BaseModel):
    id: UUID
    email: EmailStr
    username: Optional[str] = None
    full_name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UserPublicResponseResource(BaseResponse):
    data: UserPublicResponse

class ListUserPublicResponseResource(ListResponseWithPagination):
    data: List[UserPublicResponse]

class UserRegisterSchema(BaseModel):
    # Use Field for constraints and clear descriptions
    email: EmailStr
    password: str = Field(..., min_length=8)  # Industry standard is usually 8+
    password_confirm: str = Field(..., min_length=8)
    
    # Corrected the syntax error: removed the extra '=""'
    username: Optional[str] = Field(..., min_length=6, max_length=15)
    full_name: str = Field(..., min_length=1)
    
    @model_validator(mode="after")
    def check_passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("passwords do not match")
        return self

class UserLoginSchema(BaseModel):
    identity: str = Field(..., min_length=3, description="username / email")
    password: str = Field(..., min_length=8)

    @field_validator("identity")
    @classmethod
    def validate_identity(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Identity cannot be empty")

        return value

class UserLoginResponse(UserPublicResponse):
    token: Optional[str] = ""

class UserLoginResponseResource(BaseResponse):
    data: UserLoginResponse

class UserSimple(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    username: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
