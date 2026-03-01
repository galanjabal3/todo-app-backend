from uuid import UUID
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, model_validator
from app.utils.enums import StatusTask
from app.schemas.base import *
from app.schemas.common import GroupSimple, UserSimple

class TaskFilter(BasePaginationFilter):
    title: Optional[str] = None
    status: Optional[StatusTask] = None

class TaskPayload(BaseModel):
    title: str
    description: Optional[str] = ""
    status: Optional[StatusTask] = StatusTask.TODO
    due_date: Optional[datetime] = None
    attachment: list = Field(default_factory=list)
    group_id: Optional[str] = ""
    assigned_to_id: Optional[str] = ""

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    status: Optional[StatusTask] = StatusTask.TODO
    due_date: Optional[datetime] = None
    attachment: list = Field(default_factory=list)

    model_config = ConfigDict(use_enum_values=True)

class TaskUpdateStatusOrAssign(BaseModel):
    status: Optional[StatusTask] = None
    assigned_to_id: Optional[str] = None

    model_config = ConfigDict(use_enum_values=True)

    @model_validator(mode="after")
    def validate_only_one_field(self):
        filled_fields = [
            field for field in [self.status, self.assigned_to_id]
            if field is not None
        ]

        if len(filled_fields) == 0:
            raise ValueError("Either 'status' or 'assigned_to_id' must be provided")

        if len(filled_fields) > 1:
            raise ValueError("Only one field can be updated at a time")

        return self

class TaskUpdate(BaseModel):
    id: UUID
    title: str
    description: Optional[str] = ""
    status: Optional[StatusTask] = ""
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    attachment: list = Field(default_factory=list)

    model_config = ConfigDict(use_enum_values=True)

class TaskResponse(BaseModel):
    id: UUID
    title: str
    description: str
    status: str
    due_date: Optional[datetime] = None
    attachment: list = Field(default_factory=list)
    assigned_to: Optional[UserSimple] | None
    group: Optional[GroupSimple] | None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TaskResponseResource(BaseResponse):
    data: TaskResponse

class ListTaskResponseResource(ListResponseWithPagination):
    data: List[TaskResponse]