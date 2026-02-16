"""
Service Registry - Register semua services
"""
from app.container import ServiceContainer
from app.utils.enums import EntityType

from app.services.user_service import UserService
from app.services.group_service import GroupService
from app.services.group_member_service import GroupMemberService
from app.services.task_service import TaskService


def register_services():
    """Register semua services"""
    ServiceContainer.register(EntityType.USER, lambda: UserService())
    ServiceContainer.register(EntityType.GROUP, lambda: GroupService())
    ServiceContainer.register(EntityType.GROUP_MEMBER, lambda: GroupMemberService())
    ServiceContainer.register(EntityType.TASK, lambda: TaskService())
    
    ServiceContainer.boot()