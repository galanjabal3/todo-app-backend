from typing import TYPE_CHECKING
from app.container import ServiceContainer
from app.repositories.group_repository import GroupRepository
from app.services.base import BaseService
from app.schemas.group import GroupResponse
from app.utils.logger import logger
from app.utils.enums import EntityType, GroupRole
from app.utils.http_exceptions import not_found, conflict

if TYPE_CHECKING:
    from app.services.group_member_service import GroupMemberService
    from app.services.user_service import UserService

class GroupService(BaseService[GroupRepository]):
    
    def __init__(self):
        # We pass the repo and the schema variable to the parent
        super().__init__(repository=GroupRepository())
    
    @property
    def group_member_service(self) -> "GroupMemberService":
        return ServiceContainer.get(EntityType.GROUP_MEMBER)

    @property
    def user_service(self) -> "UserService":
        return ServiceContainer.get(EntityType.USER)

    def get_all_group_by_member(self, user_id: str):
        group_members = self.group_member_service.get_all_with_filters(filters={
            "user_id": user_id,
        }, to_model=True)
        
        if not group_members:
            return []
        
        group_ids = {x.group.id: x for x in group_members}

        return self.get_all_with_filters({"ids": list(group_ids.keys())})
    
    def create_group(self, payload: dict = None, user_id: str = None):
        try:
            # Check User
            user = self.user_service.get_by_id(id=user_id, to_model=True)
            if not user:
                not_found(msg=f"User id '{user_id}' is not found.")
            
            # Make a new group
            new_group = self.repo.create(payload, to_model=True)
            
            # Assign account to admin group member
            self.group_member_service.create({
                "group": new_group,
                "user": user,
                "role": GroupRole.ADMIN.value
            })
            
            return GroupResponse.model_validate(new_group).model_dump(mode="json")
            
        except Exception as e:
            logger.error(f"Err in create_group: {e}", exc_info=e)
            raise
