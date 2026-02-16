from app.resources.base import api_spec, Response, BaseResource
from app.services.user_service import UserService
from app.schemas.user import UserLoginSchema, UserLoginResponseResource, UserRegisterSchema, UserPublicResponseResource
from app.utils.enums import TagsSwagger

class BaseAuthResource(BaseResource):
    def __init__(self):
        self.user_service = UserService()

class AuthLoginResource(BaseAuthResource):
    skip_auth = True
    
    @api_spec.validate(
        json=UserLoginSchema,
        resp=Response(
            HTTP_200=UserLoginResponseResource,
        ),
        security=[],
        tags=[TagsSwagger.AUTH.value]
    )
    def on_post(self, req, resp):
        body = self.parse_body(req, UserLoginSchema)
        self.resource_response(resp=resp, data=self.user_service.auth_login(body))


class AuthRegisterResource(BaseAuthResource):
    skip_auth = True
    
    @api_spec.validate(
        json=UserRegisterSchema,
        resp=Response(
            HTTP_200=UserPublicResponseResource,
        ),
        security=[],
        tags=[TagsSwagger.AUTH.value]
    )
    def on_post(self, req, resp):
        body = self.parse_body(req, UserRegisterSchema)
        self.resource_response(resp=resp, data=self.user_service.auth_register(body))