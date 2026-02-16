from typing import TYPE_CHECKING
from app.container import ServiceContainer
from app.repositories.group_member_repository import GroupMemberRepository
from app.services.base import BaseService
from app.utils.logger import logger
from app.utils.enums import EntityType
from app.utils.http_exceptions import not_found

if TYPE_CHECKING:
    from app.services.group_service import GroupService

class GroupMemberService(BaseService[GroupMemberRepository]):
    
    def __init__(self):
        # We pass the repo and the schema variable to the parent
        super().__init__(repository=GroupMemberRepository())
    
    # access to GroupService
    @property
    def group_service(self) -> "GroupService":
        return ServiceContainer.get(EntityType.GROUP)
    