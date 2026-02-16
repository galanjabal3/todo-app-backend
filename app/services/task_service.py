from uuid import UUID
from typing import TYPE_CHECKING
from app.container import ServiceContainer
from app.repositories.task_repository import TaskRepository
from app.services.base import BaseService
from app.schemas.task import  *
from app.utils.logger import logger
from app.utils.http_exceptions import not_found, unauthorized, conflict
from app.utils.enums import EntityType

if TYPE_CHECKING:
    from app.services.group_service import GroupService
    from app.services.group_member_service import GroupMemberService
    from app.services.user_service import UserService

class TaskService(BaseService[TaskRepository]):
    
    def __init__(self):
        # We pass the repo and the schema variable to the parent
        super().__init__(repository=TaskRepository())
    
    @property
    def group_service(self) -> "GroupService":
        return ServiceContainer.get(EntityType.GROUP)

    @property
    def group_member_service(self) -> "GroupMemberService":
        return ServiceContainer.get(EntityType.GROUP_MEMBER)

    @property
    def user_service(self) -> "UserService":
        return ServiceContainer.get(EntityType.USER)

    def create_task(self, payload: dict = None, user_id: str = None):
        try:
            payload = payload or {}

            group_id = payload.get("group_id")
            assigned_to_id = payload.get("assigned_to_id")

            group = None
            assigned_to = None

            # CASE 1: Task with group
            if group_id:
                group = self.group_service.get_by_id(group_id, to_model=True)

                if assigned_to_id:
                    assigned_to = self.user_service.get_by_id(
                        id=assigned_to_id,
                        to_model=True,
                        raise_error=False
                    )
                    if not assigned_to:
                        not_found(msg=f"User '{assigned_to_id}' not found")

                    is_member = self.group_member_service.get_one_by_filters(
                        {
                            "group_id": group_id,
                            "user_id": assigned_to_id,
                        },
                        raise_error=False,
                    )

                    if not is_member:
                        not_found(msg=f"User '{assigned_to_id}' is not in this group")

            # CASE 2: Personal task
            else:
                assigned_to = self.user_service.get_by_id(
                    id=user_id,
                    to_model=True,
                    raise_error=False
                )

                if not assigned_to:
                    not_found(msg=f"User '{user_id}' not found")

            # Validate payload (Pydantic)
            validated_payload = TaskCreate.model_validate(payload).model_dump()

            new_task = self.repo.create(
                {
                    **validated_payload,
                    "group": group,
                    "assigned_to": assigned_to,
                },
                to_model=True,
            )

            return TaskResponse.model_validate(new_task).model_dump(mode="json")

        except Exception as e:
            logger.error(f"Create task error: {e}")
            raise
    
    def update_task(self, payload: dict = None):
        try:
            payload = payload or {}

            task = self.repo.get_by_id(id=payload.get("id"), to_model=True)
            if not task:
                not_found(msg="Task not found")

            # Validate payload (Pydantic)
            validated_payload = TaskUpdate.model_validate(payload).model_dump()

            return self.update(validated_payload)

        except Exception as e:
            logger.error(f"Update task error: {e}")
            raise

    def update_status_or_assign(self, task_id: str, payload: dict):
        try:
            # Validate request
            validated = TaskUpdateStatusOrAssign.model_validate(payload)

            task = self.repo.get_by_id(task_id, to_model=True)
            if not task:
                not_found(msg="Task not found")

            update_data = {"id": task_id}

            # =========================
            # Update STATUS
            # =========================
            if validated.status is not None:
                update_data["status"] = validated.status

            # =========================
            # Update ASSIGNED USER
            # =========================
            if validated.assigned_to_id is not None:
                new_user = self.user_service.get_by_id(
                    id=validated.assigned_to_id,
                    to_model=True,
                    raise_error=False,
                )

                if not new_user:
                    not_found(msg=f"User '{validated.assigned_to_id}' not found")

                # Optional: check group membership
                if task.group:
                    is_member = self.group_member_service.get_one_by_filters(
                        {
                            "group_id": str(task.group.id),
                            "user_id": validated.assigned_to_id,
                        },
                        raise_error=False,
                    )

                    if not is_member:
                        not_found(msg="User is not in this group")

                update_data["assigned_to"] = new_user

            return self.repo.update(update_data)

        except Exception as e:
            logger.error(f"Error update_status_or_assign: {e}")
            raise
