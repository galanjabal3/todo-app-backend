from app.resources.base import api_spec, Response, BaseResource
from app.services.group_service import GroupService
from app.schemas.group import *
from app.utils.enums import TagsSwagger

class BaseGroupResource(BaseResource):
    def __init__(self):
        self.service = GroupService()

class MyGroupsResource(BaseGroupResource):

    @api_spec.validate(
        query=GroupFilter,
        resp=Response(HTTP_200=ListMyGroupResponseResource),
        tags=[TagsSwagger.GROUP.value]
    )
    def on_get(self, req, resp):
        self.resource_response(resp=resp, data=self.service.get_all_group_by_member(
            user_id=req.context["user"]["id"]
        ))

class GroupsResource(BaseGroupResource):

    @api_spec.validate(
        query=GroupFilter,
        resp=Response(HTTP_200=ListGroupResponseResource),
        tags=[TagsSwagger.GROUP.value]
    )
    def on_get(self, req, resp):
        filters = self.generate_filters_resource(req, params_string=["name"])
        page = req.get_param_as_int("page", default=1, required=False)
        limit = req.get_param_as_int("limit", default=100, required=False)
        
        filters.append({"field": "user_id", "value": req.context["user"]["id"]})
        data, pagination = self.service.get_all_with_filters_and_pagination(
            page=page,
            limit=limit,
            filters=filters,
        )
        self.resource_response(resp=resp, data=data, pagination=pagination)
    
    @api_spec.validate(
        json=GroupPayload,
        resp=Response(HTTP_200=GroupResponseResource),
        tags=[TagsSwagger.GROUP.value]
    )
    def on_post(self, req, resp):
        body = self.parse_body(req, GroupPayload)
        self.resource_response(resp=resp, data=self.service.create_group(
            body,
            user_id=req.context["user"]["id"]
        ))

class GroupsWithIdResource(BaseGroupResource):

    @api_spec.validate(
        resp=Response(HTTP_200=GroupResponseResource),
        tags=[TagsSwagger.GROUP.value]
    )
    def on_get(self, req, resp, id: str):
        self.resource_response(resp=resp, data=self.service.get_by_id(id=id))
    
    @api_spec.validate(
        json=GroupPayload,
        resp=Response(HTTP_200=GroupResponseResource),
        tags=[TagsSwagger.GROUP.value]
    )
    def on_put(self, req, resp, id: str):
        body = self.parse_body(req, GroupPayload)
        body["id"] = id
        self.resource_response(resp=resp, data=self.service.update(body))
    
    @api_spec.validate(
        resp=Response(HTTP_200=BaseResponse[bool]),
        tags=[TagsSwagger.GROUP.value]
    )
    def on_delete(self, req, resp, id: str):
        self.resource_response(resp=resp, data=self.service.delete_by_id(id=id))

class GroupInviteResource(BaseGroupResource):
    @api_spec.validate(
        resp=Response(HTTP_200=InviteGroupResponseResource),
        tags=[TagsSwagger.GROUP.value]
    )
    def on_get(self, req, resp, id: str):
        self.resource_response(resp=resp, data=self.service.get_group_invite_token(
            group_id=id,
            user_id=req.context["user"]["id"]
        ))

class GroupPreviewResource(BaseGroupResource):
    @api_spec.validate(
        resp=Response(HTTP_200=PreviewGroupResponseResource),
        tags=[TagsSwagger.GROUP.value]
    )
    def on_get(self, req, resp, token: str):
        self.resource_response(resp=resp, data=self.service.preview_group_by_token(
            token=token,
        ))

class RequestJoinGroupResource(BaseGroupResource):
    @api_spec.validate(
        json=JoinGroupPayload,
        resp=Response(HTTP_200=JoinGroupResponseResource),
        tags=[TagsSwagger.GROUP.value]
    )
    def on_post(self, req, resp):
        body = self.parse_body(req, JoinGroupPayload)
        self.resource_response(resp=resp, data=self.service.request_join_group_by_token(
            token=body.get("token"),
            user_id=req.context["user"]["id"]
        ))

class ApproveNewMemberGroupResource(BaseGroupResource):
    @api_spec.validate(
        json=ApproveNewMemberPayload,
        resp=Response(HTTP_200=ApproveGroupResponseResource),
        tags=[TagsSwagger.GROUP.value]
    )
    def on_post(self, req, resp, id: str):
        body = self.parse_body(req, ApproveNewMemberPayload)
        self.resource_response(resp=resp, data=self.service.approve_member(
            group_id=id,
            user_id=body.get("user_id"),
            admin_id=req.context["user"]["id"],
            approve=body.get("approve", True)
        ))