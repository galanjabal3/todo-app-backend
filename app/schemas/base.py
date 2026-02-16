from typing import Generic, List, TypeVar, Optional, Dict, Any, Union
from pydantic import BaseModel, Field

T = TypeVar("T")


class BaseResponse(BaseModel, Generic[T]):
    code: int = 200
    status: str = "200 OK"
    message: str = "Success"
    data: Optional[T] = None
    
class DeleteResponse(BaseResponse[bool]):
    data: Union[bool, None] = True

class PaginationResponse(BaseModel):
    page: int
    limit: int
    total: int
    total_pages: int

class ListResponse(BaseResponse[List[T]], Generic[T]):
    data: List[T]

class ListResponseWithPagination(BaseResponse[List[T]], Generic[T]):
    data: List[T]
    pagination: PaginationResponse
    metadata: Dict[str, Any] = Field({})
    
class BasePaginationFilter(BaseModel):
    page: Optional[int] = Field(default=1)
    limit: Optional[int] = Field(default=100)

class BaseFilter(BaseModel):
    id: Optional[str] = Field(default=None)
