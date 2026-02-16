# Resource Entities
from app.resources.base import HealthResource
from app.resources.auth_resource import AuthLoginResource, AuthRegisterResource
from app.resources.user_resource import UserProfileResource, UsersResource
from app.resources.group_resource import GroupsResource, GroupsWithIdResource, MyGroupsResource
from app.resources.task_resource import TaskResource, TaskWithIdResource, GroupTasksResource

def register_auth_routes(add):
    add("/login", AuthLoginResource(), base="/auth")
    add("/register", AuthRegisterResource(), base="/auth")

def register_routes(app, api_prefix="/api"):
    def add(path, resource, *, base=""):
        app.add_route(f"{api_prefix}{base}{path}", resource)

    app.add_route("/health", HealthResource())

    register_auth_routes(add)

    add("/admin/users", UsersResource())
    add("/user/profile", UserProfileResource())
    
    # Group
    add("/user/my_groups", MyGroupsResource())
    add("/user/groups", GroupsResource())
    add("/user/groups/{id}", GroupsWithIdResource())

    # Task
    add("/user/tasks", TaskResource())
    add("/user/tasks/{id}", TaskWithIdResource())
    add("/user/group/{id}/tasks", GroupTasksResource())
