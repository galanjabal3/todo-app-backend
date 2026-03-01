from uuid import UUID
from typing import List, Optional, Union
from pydantic import BaseModel, ConfigDict, EmailStr


class UserSimple(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    username: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class GroupSimple(BaseModel):
    id: Union[str, UUID]
    name: str

    model_config = ConfigDict(from_attributes=True)

class GroupMemberSimple(UserSimple):
    role: str