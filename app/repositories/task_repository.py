import uuid
from app.schemas.task import *
from app.repositories.base import BaseRepository
from app.db.models import TaskDB

class TaskRepository(BaseRepository):
    entity = TaskDB
    
    # Mapping filter fields:
    # q = Query object, v = Value input, t = Table entity
    filter_map = {
        **BaseRepository.filter_map,
        "title": lambda x, v: x.filter(lambda t: t.title.lower() == v),
        "status": lambda x, v: x.filter(lambda t: t.status == v),
        "user_id": lambda x, v: x.filter(
            lambda t: t.assigned_to and t.assigned_to.id == uuid.UUID(v)
        ),
        "group_id": lambda x, v: (
            x.filter(lambda t: t.group is None)
            if v in (None, "null", "")
            else x.filter(lambda t: t.group and t.group.id == uuid.UUID(v))
        ),
    }
    
    def __init__(self):
        # We pass the repo and the schema variable to the parent
        super().__init__(schema_class=TaskResponse)
