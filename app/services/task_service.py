from uuid import UUID
from typing import TYPE_CHECKING
from app.container import ServiceContainer
from app.repositories.task_repository import TaskRepository
from app.services.base import BaseService
from app.schemas.task import  *
from app.utils.logger import logger
from app.utils.http_exceptions import not_found
from app.utils.enums import EntityType

if TYPE_CHECKING:
    from app.services.group_service import GroupService
    from app.services.group_member_service import GroupMemberService
    from app.services.user_service import UserService
    from app.services.storage_service import StorageService

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

    @property
    def storage_service(self) -> "StorageService":
        return ServiceContainer.get(EntityType.STORAGE)

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

            assigned_to_id = payload.get("assigned_to_id")
            if "assigned_to_id" in payload:
                new_user = None
                if assigned_to_id:  # hanya fetch user jika tidak None
                    new_user = self.user_service.get_by_id(
                        id=assigned_to_id,
                        to_model=True,
                        raise_error=False,
                    )

                    if not new_user:
                        not_found(msg=f"User '{assigned_to_id}' not found")

                    if task.group:
                        is_member = self.group_member_service.get_one_by_filters(
                            {"group_id": str(task.group.id), "user_id": assigned_to_id},
                            raise_error=True,
                        )
                        if not is_member:
                            not_found(msg="User is not in this group")

                validated_payload["assigned_to"] = new_user  # None = unassign

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

    def unassign_tasks_by_user_in_group(self, group_id: str, user_id: str):
        return self.update_all_with_filters(filters={
            "group_id": group_id,
            "user_id": user_id,
        }, data={"assigned_to": None})
    
    # Attachments
    def upload_attachment(self, task_id: str, file_bytes: bytes, file_name: str, content_type: str, user_id: str) -> dict:
        """
        Upload a file attachment to a task.
        Stores file in Supabase Storage and appends metadata to task.attachment JSON field.
        """
        try:
            task = self.repo.get_by_id(id=task_id, to_model=True)
            if not task:
                not_found(msg="Task not found")

            # Upload to Supabase Storage
            uploaded = self.storage_service.upload_file(
                file_bytes=file_bytes,
                file_name=file_name,
                content_type=content_type,
                task_id=task_id,
            )

            # Append to existing attachments
            current_attachments = task.attachment or []
            current_attachments.append({
                **uploaded,
                "uploaded_by": user_id,
                "uploaded_at": datetime.now(timezone.utc).isoformat(),
            })

            task.attachment = current_attachments

            return TaskResponse.model_validate(task).model_dump(mode="json")

        except Exception as e:
            logger.error(f"Upload attachment error: {e}")
            raise

    def delete_attachment(self, task_id: str, attachment_id: str) -> dict:
        """
        Delete a specific attachment from a task by attachment_id.
        Removes file from Supabase Storage and updates task.attachment JSON field.
        """
        try:
            task = self.repo.get_by_id(id=task_id, to_model=True)
            if not task:
                not_found(msg="Task not found")

            current_attachments = task.attachment or []

            # Find the attachment
            target = next((a for a in current_attachments if a.get("id") == attachment_id), None)
            if not target:
                not_found(msg="Attachment not found")

            # Extract unique file name from URL to delete from storage
            # URL format: .../task-attachments/<task_id>/<uuid>_<filename>
            file_url = target.get("file_url", "")
            unique_file_name = file_url.split(f"{task_id}/")[-1]

            # Delete from Supabase Storage
            self.storage_service.delete_file(
                task_id=task_id,
                unique_file_name=unique_file_name,
            )

            # Remove from attachment list
            task.attachment = [a for a in current_attachments if a.get("id") != attachment_id]

            return TaskResponse.model_validate(task).model_dump(mode="json")

        except Exception as e:
            logger.error(f"Delete attachment error: {e}")
            raise
    
    def delete_task_with_attachments(self, task_id: str) -> bool:
        """
        Delete a task and all its attachments from Supabase Storage.
        """
        try:
            task = self.repo.get_by_id(id=task_id, to_model=True)
            if not task:
                not_found(msg="Task not found")

            # Remove all attachment from storage
            attachments = task.attachment or []
            for att in attachments:
                unique_file_name = att.get("unique_file_name")
                if unique_file_name:
                    try:
                        self.storage_service.delete_file(
                            task_id=task_id,
                            unique_file_name=unique_file_name,
                        )
                    except Exception as e:
                        logger.warning(f"Failed to delete attachment {unique_file_name}: {e}")
                
            if attachments:
                self.storage_service.delete_folder(task_id=task_id)

            return self.delete_by_id(id=task_id, soft_delete=False)

        except Exception as e:
            logger.error(f"Delete task with attachments error: {e}")
            raise