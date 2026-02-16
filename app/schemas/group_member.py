from datetime import datetime
from pydantic import ConfigDict, BaseModel
from app.schemas.user import UserSimple

class GroupMemberCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    group_id: str
    user_id: str
    role: str = "member"

class GroupMemberResponse(BaseModel):
    group: str
    user: str
    role: str
    joined_at: datetime

class GroupMemberSimple(UserSimple):
    role: str
