from enum import Enum

class StatusTask(Enum):
    TODO = "todo"
    IN_PROGRESS = "in progress"
    DONE = "done"


class GroupRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


class EntityType(Enum):
    USER = "user"
    GROUP = "group"
    GROUP_MEMBER = "group_member"
    TASK = "task"


class RoleType(str, Enum):
    ADMIN = 'admin'
    USER = 'user'


class TagsSwagger(str, Enum):
    CORE = "Core"
    AUTH = "Auth"
    USER = "User"
    GROUP = "Group"
    TASK = "Task"