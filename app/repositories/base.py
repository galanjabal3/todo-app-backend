import math
from typing import Type, Protocol, Optional
from pydantic import BaseModel
from pony.orm import select, desc
from app.utils.logger import logger


# -------------------------------
# Protocol (type hint / interface)
# -------------------------------
class BaseRepositoryProtocol(Protocol):
    """
    Protocol for repository type hinting and IDE autocomplete.
    This defines the "contract" that concrete repositories must follow.
    """

    # runtime attributes every repository should have
    entity: object                 # ORM model / database entity
    schema_class: Optional[Type[BaseModel]]  # Pydantic schema for serialization/deserialization

    # Example generic methods every repository should implement
    def __init__(self, schema_class: Optional[Type[BaseModel]] = None): ...
    
    def entity_label(self) -> str: ...
    
    def apply_query_options(self, query, filters, order_by=None): ...
    
    def get_by_id(self, id): ...
    
    def get_all_with_filters_and_pagination(self, filters=None, page=1, limit=10, order_by="-created_at", to_model=False,  schema_response=None): ...
    
    def get_one_by_filters(self, filters=None, to_model=False, schema_response=None): ...

    def count_all_with_filters(self, filters=None): ...
    
    def create(self, data: dict): ...
    
    def update(self, data: dict): ...
    
    def update_one_with_filters(self, filters=None, data: dict = {}): ...
    
    def delete_by_id(self, id, soft_delete=True): ...
    

# -------------------------------
# BaseRepository (runtime)
# -------------------------------
class BaseRepository:
    """
    BaseRepository provides a generic repository layer for interacting with the database.

    Attributes:
        entity: The database entity (model) associated with this repository.
        schema_class: The default schema class to be used for data serialization/deserialization.
        filter_map: A mapping of fields to their respective filter handlers.
    """
    entity: None
    schema_class = Type[BaseModel]
    
    # mapping field to filter → handler
    filter_map = {
        "id": lambda x, v: x.filter(lambda t: str(t.id) == v),
        "is_deleted": lambda x, v: x.filter(lambda t: t.is_deleted == v),
    }
    
    def __init__(self, schema_class: Type[BaseModel] = None):
        """
        Initialize the BaseRepository.
        """
        self.schema = schema_class or self.schema_class
        if self.entity is None:
            raise NotImplementedError(
                "Repository must define entity"
            )
    
    @property
    def entity_label(self) -> str:
        name = self.entity.__name__ if self.entity else self.__class__.__name__
        return name.replace("DB", "").replace("Model", "")

    def apply_query_options(self, query, filters, order_by=None):
        """
        Apply filters to a query.

        Args:
            query: The query to apply filters to.
            filters: A list of filters to apply.

        Returns:
            The filtered query.
        """
        try:
            filters = filters or []
            
            # Default soft delete
            if not any(f.get("field") == "is_deleted" for f in filters):
                handler = self.filter_map.get("is_deleted")
                if handler:
                    query = handler(query, False)

            # Apply filters
            for f in filters:
                field = f.get("field")
                value = f.get("value")

                handler = self.filter_map.get(field)
                if handler:
                    query = handler(query, value)
            
            # Apply ordering
            if order_by:
                descending = order_by.startswith("-")
                field_name = order_by.lstrip("-")

                field = getattr(self.entity, field_name, None)
                if field:
                    query = query.order_by(desc(field) if descending else field)
            
            return query
        except Exception as e:
            logger.error(f"Error in apply_query_options: {e}", exc_info=e)
            raise

    # @db_session
    def get_by_id(self, id, to_model=False, schema_response=None):
        """
        Retrieve an entity by its ID.

        Args:
            id: The ID of the entity to retrieve.

        Returns:
            The entity with the specified ID.

        Raises:
            Exception: If an error occurs during retrieval.
        """
        try:
            filters = {"id": id}
            if hasattr(self.entity, "is_deleted"):
                filters["is_deleted"] = False

            query = self.entity.get(**filters)
            if to_model:
                return query
            
            schema = schema_response or self.schema
            if schema and query is not None:
                query = schema.model_validate(query).model_dump(mode="json")
            
            return query
        except Exception as e:
            logger.error(f"Error in get_by_id: {e}", exc_info=e)
            raise

    # @db_session
    def get_all_with_filters_and_pagination(self, filters=None, page=1, limit=10, order_by="created_at", to_model=False,  schema_response=None):
        """
        Retrieve all entities with filters and pagination.

        Args:
            filters: A list of filters to apply.
            page: The page number for pagination.
            limit: The number of entities per page.
            order_by: Field name to sort by, prefixed with "-" for descending order. 

        Returns:
            A tuple containing the filtered entities and pagination details.

        Raises:
            Exception: If an error occurs during retrieval.
        """
        try:
            if filters is None:
                filters = []
            
            query = select(e for e in self.entity)
            query = self.apply_query_options(query, filters, order_by)
            
            # Paginate
            page = max(page, 1)
            if limit <= 0:
                items = list(query)  # ✅ Convert to list
                total = len(items)
                total_pages = 1
            else:
                limit = max(limit, 1)
                total = query.count()
                total_pages = math.ceil(total / limit)

                offset = (page - 1) * limit
                # ✅ Use .limit() and .offset() instead of slicing
                items = list(query.limit(limit, offset=offset))
            
            schema = schema_response or self.schema

            if schema and not to_model:
                items = [
                    schema.model_validate(obj).model_dump(mode="json")
                    for obj in items
                ]
            
            return items, {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages
            }
        except Exception as e:
            logger.error(f"Error in get_all_with_filters_and_pagination: {e}", exc_info=e)
            return [], {
                "page": page,
                "limit": limit,
                "total": 0,
                "total_pages": 0
            }
    
    # @db_session
    def get_one_by_filters(self, filters=None, to_model=False, schema_response=None):
        """
        Retrieve a single entity matching the filters.

        Args:
            filters: A list of filters to apply.

        Returns:
            The entity matching the filters.

        Raises:
            Exception: If an error occurs during retrieval.
        """
        try:
            if filters is None:
                filters = []
            
            # Build query
            query = select(e for e in self.entity)
            query = self.apply_query_options(query, filters)

            result = query.first()

            if to_model:
                return result

            schema = schema_response or self.schema
            if schema and result is not None:
                result = schema.model_validate(result).model_dump(mode="json")

            return result
        except Exception as e:
            logger.error(f"Error in get_one_by_filters: {e}", exc_info=e)
            raise
    
    def count_all_with_filters(self, filters=None):
        """
        Count all entities matching the specified filters.
        
        Args:
            filters (list, optional): A list of filter conditions to apply to the query.
                Defaults to None, which is treated as an empty list.
        
        Returns:
            int: The total count of entities that match the applied filters.
        
        Raises:
            Exception: If an error occurs during the query execution. The error is logged
                with full traceback information before being re-raised.
        
        Example:
            >>> count = repository.count_all_with_filters(filters=[filter_condition])
            >>> print(count)
            5
        """
        try:
            filters = filters or []

            query = select(e for e in self.entity)
            query = self.apply_query_options(query, filters)

            return query.count()

        except Exception as e:
            logger.error(f"Error in count_all_with_filters: {e}", exc_info=True)
            raise

    # @db_session
    def create(self, data: dict, to_model=False):
        """
        Create a new entity.

        Args:
            data: The data for the new entity.

        Returns:
            The created entity.

        Raises:
            Exception: If an error occurs during creation.
        """
        try:
            entity_obj = self.entity(**data)
            if to_model:
                return entity_obj
            
            return entity_obj.to_dict(with_collections=True)
        except Exception as e:
            logger.error(f"Error in create: {e}", exc_info=e)
            raise

    # @db_session
    def update(self, data: dict):
        """
        Update an existing entity.

        Args:
            data: The updated data for the entity.

        Returns:
            The updated entity, or None if the entity does not exist.

        Raises:
            Exception: If an error occurs during update.
        """
        try:
            entity_obj = self.get_by_id(data.get("id"), to_model=True)
            if not entity_obj:
                return None
            
            entity_obj.set(**data)
            result = entity_obj
            
            if self.schema and result is not None:
                result = self.schema.model_validate(result).model_dump(mode="json")
            
            return result
        except Exception as e:
            logger.error(f"Error in update: {e}", exc_info=e)
            raise
    
    # @db_session
    def update_one_with_filters(self, filters=None, data: dict = {}):
        """
        Update an existing entity with filters.

        Args:
            data: The updated data for the entity with filters.

        Returns:
            The updated entity, or None if the entity does not exist.

        Raises:
            Exception: If an error occurs during update.
        """
        try:
            entity_obj = self.get_one_by_filters(filters, to_model=True)
            if not entity_obj:
                return None
            
            entity_obj.set(**data)
            result = entity_obj
            
            if self.schema and result is not None:
                result = self.schema.model_validate(result).model_dump(mode="json")
            
            return result
        except Exception as e:
            logger.error(f"Error in update_one_with_filters: {e}", exc_info=e)
            raise

    # @db_session
    def delete_by_id(self, id, soft_delete=True):
        """
        Delete an entity by its ID.

        Args:
            id: The ID of the entity to delete.
            soft_delete: Whether to perform a soft delete (default: True).

        Returns:
            The result of the delete operation.

        Raises:
            Exception: If an error occurs during deletion.
        """
        try:
            obj = self.get_by_id(id, to_model=True)
            if not obj:
                return None

            if soft_delete and hasattr(obj, "is_deleted"):
                obj.is_deleted = True
            else:
                obj.delete()
            
            return True
        except Exception as e:
            logger.error(f"Error in delete_by_id: {e}", exc_info=e)
            raise
