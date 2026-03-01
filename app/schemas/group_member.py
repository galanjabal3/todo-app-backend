from datetime import datetime
from typing import Optional
from pydantic import ConfigDict, BaseModel
from app.schemas.common import GroupSimple, UserSimple

class GroupMemberCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    group_id: str
    user_id: str
    role: str = "member"

class GroupMemberResponse(BaseModel):
    group: Optional[GroupSimple]
    user: Optional[UserSimple]
    role: str = None
    joined_at: datetime

    model_config = ConfigDict(from_attributes=True)

class GroupMemberSimple(UserSimple):
    role: str
