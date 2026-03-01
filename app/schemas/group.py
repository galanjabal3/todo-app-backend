from uuid import UUID
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator
from app.schemas.base import *
from app.schemas.common import GroupMemberSimple

class GroupFilter(BasePaginationFilter):
    name: Optional[str] = None

class GroupPayload(BaseModel):
    name: str

class GroupResponse(BaseModel):
    id: UUID
    name: str
    created_at: Optional[datetime] = None
    members: List[GroupMemberSimple] = Field(default_factory=list)
    
    model_config = ConfigDict(from_attributes=True)
    
class GroupResponseResource(BaseResponse):
    data: GroupResponse

class ListGroupResponseResource(ListResponseWithPagination):
    data: List[GroupResponse]

class ListMyGroupResponseResource(ListResponse):
    data: List[GroupResponse]

class JoinGroupPayload(BaseModel):
    token: str

class InviteResponse(BaseModel):
    link: str = Field(..., example="https://todo-app-frontend-phi.vercel.app/join/eyJncm91cF9pZCI6ICIxMjMifQ.abc123xyz")
    expires_days: int = Field(..., example=7)

class InviteGroupResponseResource(BaseResponse):
    data: InviteResponse = Field(..., example={
        "link": "https://todo-app-frontend-phi.vercel.app/join/eyJncm91cF9pZCI6ICIxMjMifQ.abc123xyz",
        "expires_days": 7
    })

class MessageJoinGroupResponse(BaseModel):
    message: str

class JoinGroupResponseResource(BaseResponse):
    data: MessageJoinGroupResponse

# Preview Group by token
class PreviewGroupResponse(BaseModel):
    id: Union[str, UUID]
    name: str
    member_count: Optional[int] = 0

    model_config = ConfigDict(from_attributes=True)

class PreviewGroupResponseResource(BaseResponse):
    data: PreviewGroupResponse

# Approve / Reject Member requested
class ApproveNewMemberPayload(BaseModel):
    user_id: str
    approve: Optional[bool] = True

class ApproveJoinGroupResponse(BaseModel):
    approve: Optional[bool] = True
    message: Optional[str] = ""

class ApproveGroupResponseResource(BaseResponse):
    data: ApproveJoinGroupResponse

class GroupSimple(BaseModel):
    id: Union[str, UUID]
    name: str

    model_config = ConfigDict(from_attributes=True)
