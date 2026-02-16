from app.schemas.group import *
from app.repositories.base import BaseRepository
from app.db.models import GroupDB

class GroupRepository(BaseRepository):
    entity = GroupDB
    
    # Mapping filter fields:
    # q = Query object, v = Value input, t = Table entity
    filter_map = {
        "ids": lambda x, v: x.filter(lambda t: t.id in v),
        "name": lambda x, v: x.filter(lambda t: t.name.lower() == v),
    }
    
    def __init__(self):
        # We pass the repo and the schema variable to the parent
        super().__init__(schema_class=GroupResponse)