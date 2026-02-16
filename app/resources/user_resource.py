from app.resources.base import api_spec, Response, BaseResource
from app.services.user_service import UserService
from app.schemas.user import UserFilter, UserPublicResponseResource, UserPublicResponse, UserUpdate, ListUserPublicResponseResource
from app.utils.enums import TagsSwagger
from app.utils.http_exceptions import forbidden

PASS_ADMIN = "214675a1-4520-4aef-aff2-28b4e4fa3a51"

class BaseUserResource(BaseResource):
    def __init__(self):
        self.service = UserService()
        
class UsersResource(BaseUserResource):

    @api_spec.validate(
        query=UserFilter,
        resp=Response(HTTP_200=ListUserPublicResponseResource),
        tags=[TagsSwagger.USER.value]
    )
    def on_get(self, req, resp):
        filters = self.generate_filters_resource(req, params_string=["email", "username"])
        page = req.get_param_as_int("page", default=1, required=False)
        limit = req.get_param_as_int("limit", default=100, required=False)
        pass_admin = req.get_param("pass_admin")
        if not pass_admin or pass_admin != PASS_ADMIN:
            forbidden(msg="You do not have permission to access this resource")
        
        data, pagination = self.service.get_all_with_filters_and_pagination(
            page=page,
            limit=limit,
            filters=filters,
            schema_response=UserPublicResponse
        )
        self.resource_response(resp=resp, data=data, pagination=pagination)

class UserProfileResource(BaseUserResource):

    @api_spec.validate(
        resp=Response(HTTP_200=UserPublicResponseResource),
        tags=[TagsSwagger.USER.value]
    )
    def on_get(self, req, resp):
        self.resource_response(resp=resp, data=self.service.get_one_by_filters(filters={
            "id": req.context["user"]["id"]
        }, schema_response=UserPublicResponse))
    
    @api_spec.validate(
        json=UserUpdate,
        resp=Response(HTTP_200=UserPublicResponseResource),
        tags=[TagsSwagger.USER.value]
    )
    def on_put(self, req, resp):
        usr_id = req.context["user"]["id"]
        
        payload = req.media
        payload["id"] = usr_id
        self.resource_response(resp=resp, data=self.service.update_one_with_filters(filters={"id": usr_id}, data=payload))
