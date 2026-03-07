from app.resources.base import api_spec, Response, BaseResource
from app.services.task_service import TaskService
from app.schemas.task import *
from app.utils.enums import TagsSwagger
from app.utils.http_exceptions import bad_request

class BaseGroupResource(BaseResource):
    def __init__(self):
        self.service = TaskService()
        
class TaskResource(BaseGroupResource):

    @api_spec.validate(
        query=TaskFilter,
        resp=Response(HTTP_200=ListTaskResponseResource),
        tags=[TagsSwagger.TASK.value]
    )
    def on_get(self, req, resp):
        filters = self.generate_filters_resource(req, params_string=["title", "status"])
        page = req.get_param_as_int("page", default=1, required=False)
        limit = req.get_param_as_int("limit", default=100, required=False)
        
        filters.append({"field": "user_id", "value": req.context["user"]["id"]})
        filters.append({"field": "group_id", "value": None})
        data, pagination = self.service.get_all_with_filters_and_pagination(
            page=page,
            limit=limit,
            filters=filters,
        )
        self.resource_response(resp=resp, data=data, pagination=pagination)
    
    @api_spec.validate(
        json=TaskPayload,
        resp=Response(HTTP_200=TaskResponseResource),
        tags=[TagsSwagger.TASK.value]
    )
    def on_post(self, req, resp):
        body = self.parse_body(req, TaskPayload)
        self.resource_response(resp=resp, data=self.service.create_task(
            payload=body,
            user_id=req.context["user"]["id"],
        ))


class TaskWithIdResource(BaseGroupResource):

    @api_spec.validate(
        resp=Response(HTTP_200=TaskResponseResource),
        tags=[TagsSwagger.TASK.value]
    )
    def on_get(self, req, resp, id: str):
        self.resource_response(resp=resp, data=self.service.get_by_id(id=id))
    
    @api_spec.validate(
        json=TaskPayload,
        resp=Response(HTTP_200=TaskResponseResource),
        tags=[TagsSwagger.TASK.value]
    )
    def on_put(self, req, resp, id: str):
        body = self.parse_body(req, TaskPayload)
        body["id"] = id
        self.resource_response(resp=resp, data=self.service.update_task(body))
    
    @api_spec.validate(
        json=TaskUpdateStatusOrAssign,
        resp=Response(HTTP_200=TaskResponseResource),
        tags=[TagsSwagger.TASK.value]
    )
    def on_patch(self, req, resp, id: str):
        body = self.parse_body(req, TaskUpdateStatusOrAssign)
        self.resource_response(resp=resp, data=self.service.update_status_or_assign(task_id=id, payload=body))
    
    @api_spec.validate(
        resp=Response(HTTP_200=BaseResponse[bool]),
        tags=[TagsSwagger.TASK.value]
    )
    def on_delete(self, req, resp, id: str):
        self.resource_response(resp=resp, data=self.service.delete_task_with_attachments(task_id=id))

class GroupTasksResource(BaseGroupResource):

    @api_spec.validate(
        query=TaskFilter,
        resp=Response(HTTP_200=ListTaskResponseResource),
        tags=[TagsSwagger.GROUP.value]
    )
    def on_get(self, req, resp, id: int):
        filters = self.generate_filters_resource(req, params_string=["title", "status", "user_id"])
        page = req.get_param_as_int("page", default=1, required=False)
        limit = req.get_param_as_int("limit", default=100, required=False)
        
        filters.append({"field": "group_id", "value": id})
        data, pagination = self.service.get_all_with_filters_and_pagination(
            page=page,
            limit=limit,
            filters=filters,
        )
        self.resource_response(resp=resp, data=data, pagination=pagination)

class TaskAttachmentResource(BaseGroupResource):

    @api_spec.validate(
        resp=Response(HTTP_200=TaskResponseResource),
        tags=[TagsSwagger.TASK.value]
    )
    def on_post(self, req, resp, id: str):
        """Upload a file attachment to a task."""
        
        file = req.get_param("file")

        if file is None:
            bad_request("No file provided")

        file_bytes = file.file.read()

        if len(file_bytes) > 10 * 1024 * 1024:
            bad_request("File size exceeds 10MB limit")

        result = self.service.upload_attachment(
            task_id=id,
            file_bytes=file_bytes,
            file_name=file.filename or "unknown",
            content_type=file.type or "application/octet-stream",
            user_id=req.context["user"]["id"],
        )

        self.resource_response(resp=resp, data=result)


class TaskAttachmentWithIdResource(BaseGroupResource):

    @api_spec.validate(
        resp=Response(HTTP_200=TaskResponseResource),
        tags=[TagsSwagger.TASK.value]
    )
    def on_delete(self, req, resp, id: str, attachment_id: str):
        """Delete a specific attachment from a task."""
        result = self.service.delete_attachment(
            task_id=id,
            attachment_id=attachment_id,
        )

        self.resource_response(resp=resp, data=result)