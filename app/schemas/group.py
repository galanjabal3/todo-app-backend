from uuid import UUID
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_validator
from app.schemas.base import *
from app.schemas.group_member import GroupMemberSimple

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

class GroupSimple(BaseModel):
    id: Union[str, UUID]
    name: str

    model_config = ConfigDict(from_attributes=True)
