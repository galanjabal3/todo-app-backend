# Resource Entities
from app.resources.base import HealthResource
from app.resources.auth_resource import AuthLoginResource, AuthRegisterResource
from app.resources.user_resource import UserProfileResource, UsersResource, UserPasswordResource
from app.resources.group_resource import (
    GroupsResource, GroupsWithIdResource, MyGroupsResource,
    RequestJoinGroupResource, ApproveNewMemberGroupResource,
    GroupInviteResource, GroupPreviewResource
)
from app.resources.task_resource import TaskResource, TaskWithIdResource, GroupTasksResource

def register_auth_routes(add):
    add("/login", AuthLoginResource(), base="/auth")
    add("/register", AuthRegisterResource(), base="/auth")

def register_group_routes(add):
    add("/user/groups/me", MyGroupsResource())
    add("/user/groups/join", RequestJoinGroupResource())
    add("/user/groups", GroupsResource())
    add("/user/groups/{id}", GroupsWithIdResource())
    add("/user/groups/{id}/approve", ApproveNewMemberGroupResource())
    add("/user/groups/{id}/invite", GroupInviteResource())
    add("/user/groups/{id}/tasks", GroupTasksResource())
    add("/user/groups/preview/{token}", GroupPreviewResource())


def register_task_routes(add):
    add("/user/tasks", TaskResource())
    add("/user/tasks/{id}", TaskWithIdResource())

def register_routes(app, api_prefix="/api"):
    def add(path, resource, *, base=""):
        app.add_route(f"{api_prefix}{base}{path}", resource)

    app.add_route("/health", HealthResource())
    register_auth_routes(add)
    register_group_routes(add)
    register_task_routes(add)
    
    add("/admin/users", UsersResource())
    add("/user/profile", UserProfileResource())
    add("/user/profile/password", UserPasswordResource())
