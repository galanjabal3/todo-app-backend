import uuid
from datetime import datetime, timezone
from pony.orm import Required, Optional, PrimaryKey, Set, Json
from app.db.database import dbcon
from app.utils.enums import StatusTask, GroupRole

db = dbcon()

class UserDB(db.Entity):
    _table_ = "users"
    
    id = PrimaryKey(uuid.UUID, default=uuid.uuid4)
    email = Required(str, unique=True)
    username = Optional(str, unique=True, nullable=True)
    password = Required(str)
    full_name = Required(str)
    
    created_at = Required(datetime, default=lambda: datetime.now(timezone.utc))
    updated_at = Optional(datetime, default=lambda: datetime.now(timezone.utc))
    is_deleted = Required(bool, default=False)
    
    # relasi
    group_memberships = Set("GroupMemberDB")
    tasks = Set("TaskDB")


class GroupDB(db.Entity):
    _table_ = "groups"
    
    id = PrimaryKey(uuid.UUID, default=uuid.uuid4)
    name = Required(str)
    
    created_at = Required(datetime, default=lambda: datetime.now(timezone.utc))
    
    # relasi
    members = Set("GroupMemberDB")
    tasks = Set("TaskDB")


class GroupMemberDB(db.Entity):
    _table_ = "group_members"
    
    group = Required(GroupDB, column="group_id")
    user = Required(UserDB, column="user_id")
    
    role = Required(str, default=GroupRole.MEMBER.value)
    joined_at = Required(datetime, default=lambda: datetime.now(timezone.utc))
    
    PrimaryKey(group, user)

    @property
    def id(self):
        return self.user.id

    @property
    def full_name(self):
        return self.user.full_name

    @property
    def email(self):
        return self.user.email

    @property
    def username(self):
        return self.user.username


class TaskDB(db.Entity):
    _table_ = "tasks"
    
    id = PrimaryKey(uuid.UUID, default=uuid.uuid4)
    title = Required(str)
    description = Optional(str, default="")
    due_date = Optional(datetime)
    status = Optional(str, default=StatusTask.TODO.value)
    attachment = Optional(Json)
    
    created_at = Required(datetime, default=lambda: datetime.now(timezone.utc))
    updated_at = Optional(datetime, default=lambda: datetime.now(timezone.utc))
    is_deleted = Required(bool, default=False)
    
    # relasi
    assigned_to = Optional(UserDB, column="assigned_to_id", reverse="tasks")
    group = Optional(GroupDB, column="group_id", reverse="tasks")
