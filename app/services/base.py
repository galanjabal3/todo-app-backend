from typing import TypeVar, Generic, Optional
from app.utils.logger import logger
from app.utils.other import list_filter_dict_to_list
from app.utils.http_exceptions import not_found
from app.repositories.base import BaseRepositoryProtocol

TRepo = TypeVar("TRepo", bound=BaseRepositoryProtocol)

class BaseService(Generic[TRepo]):
    """
    BaseService provides a generic service layer for interacting with repositories and schemas.

    Attributes:
        repository: The default repository to be used by the service.
    """
    repository: Optional[TRepo] = None

    def __init__(self, repository: Optional[TRepo] = None):
        """
        Initialize the BaseService with a repository and schema class.

        Args:
            repository: An instance of the repository to interact with the database.
            schema_class: A Pydantic model class for data validation and serialization.

        Raises:
            ValueError: If no repository is provided.
        """
        self.repo: TRepo = repository or self.repository
        if not self.repo:
            raise ValueError("Repository must be provided")
    
    @property
    def entity_name(self):
        return self.repo.entity_label
    
    def format_filters(self, filters=None):
        return filters if isinstance(filters, list) else list_filter_dict_to_list(filters=filters or [])

    def get_all_with_filters_and_pagination(self, filters=[], page=1, limit=10, to_model=False, schema_response=None):
        """
        Retrieve all records with filters and pagination.

        Args:
            filters: A list of filters to apply.
            page: The page number for pagination.
            limit: The number of records per page.
            schema_response: The schema to use for serializing the response data.

        Returns:
            A tuple containing the filtered data and pagination details.

        Raises:
            Exception: If an error occurs during data retrieval.
        """
        try:
            datas, pagination = self.repo.get_all_with_filters_and_pagination(
                filters=filters,
                page=page,
                limit=limit,
                to_model=to_model,
                schema_response=schema_response
            )
            
            return datas, pagination
        except Exception as e:
            logger.error(f"Err in get_all_with_filters_and_pagination: {e}", exc_info=e)
            raise

    def get_all_with_filters(self, filters=None, to_model=False, schema_response=None):
        """
        Retrieve all records with filters.

        Args:
            filters: A list/dict of filters to apply.

        Returns:
            A list/dict of filtered data.

        Raises:
            Exception: If an error occurs during data retrieval.
        """
        try:
            filters = self.format_filters(filters)
            datas, _ = self.get_all_with_filters_and_pagination(filters=filters, to_model=to_model, schema_response=schema_response)
            return datas
        except Exception as e:
            logger.error(f"Err in get_all_with_filters: {e}", exc_info=e)
            raise

    def get_by_id(self, id=None, to_model=False, schema_response=None, raise_error=True):
        """
        Retrieve a record by its ID.

        Args:
            id: The ID of the record to retrieve.
            to_model: If True, convert the record to a model instance.
            schema_response: The schema to use for serializing the response data.
            raise_error: If True, return None instead of raising error when not found.

        Returns:
            The record with the specified ID.

        Raises:
            Exception: If an error occurs during data retrieval.
        """
        try:
            datas = self.repo.get_by_id(id, to_model=to_model, schema_response=schema_response)
            if not datas and raise_error:
                not_found(
                    title=f"{self.entity_name} not found",
                    msg=f"{self.entity_name} does not exist"
                )
            
            return datas
        except Exception as e:
            logger.error(f"Err in get_by_id: {e}", exc_info=e)
            raise

    def get_one_by_filters(self, filters=None, to_model=False, schema_response=None, raise_error=True):
        """
        Retrieve a single record matching the filters.

        Args:
            filters: A list/dict of filters to apply.
            to_model: If True, convert the record to a model instance.
            schema_response: The schema to use for serializing the response data.
            raise_error: If True, return None instead of raising error when not found.

        Returns:
            The record matching the filters.

        Raises:
            Exception: If an error occurs during data retrieval.
        """
        try:
            filters = self.format_filters(filters)
            datas = self.repo.get_one_by_filters(filters, to_model=to_model, schema_response=schema_response)
            if not datas and raise_error:
                not_found(
                    title=f"{self.entity_name} not found",
                    msg=f"{self.entity_name} does not exist"
                )
            
            return datas
        except Exception as e:
            logger.error(f"Err in get_one_by_filters: {e}", exc_info=e)
            raise
    
    def count_all_with_filters(self, filters=None):
        try:
            filters = self.format_filters(filters)
            return self.repo.count_all_with_filters(filters=filters)
        except Exception as e:
            logger.error(f"Err in count_all_with_filters: {e}")
            raise

    def create(self, data, to_model: bool = False):
        """
        Create a new record.

        Args:
            data: The data for the new record.

        Returns:
            The created record.

        Raises:
            Exception: If an error occurs during record creation.
        """
        try:
            new_record = self.repo.create(data, to_model=to_model)
            validated_data = self.repo.schema.model_validate(new_record)
            return validated_data.model_dump(mode="json")
        except Exception as e:
            logger.error(f"Err in create: {e}", exc_info=e)
            raise

    def update(self, data):
        """
        Update an existing record.

        Args:
            data: The updated data for the record.

        Returns:
            The updated record.

        Raises:
            Exception: If an error occurs during record update.
        """
        try:
            datas = self.repo.update(data)
            if datas is None:
                not_found(
                    title=f"{self.entity_name} not found",
                    msg=f"{self.entity_name} does not exist"
                )
            
            return self.repo.schema.model_validate(datas).model_dump(mode="json")
        except Exception as e:
            logger.error(f"Err in update: {e}", exc_info=e)
            raise
    
    def update_one_with_filters(self, filters=None, data: dict = {}):
        """
        Update an existing record.

        Args:
            data: The updated data for the record.

        Returns:
            The updated record.

        Raises:
            Exception: If an error occurs during record update.
        """
        try:
            filters = self.format_filters(filters)
            datas = self.repo.update_one_with_filters(filters, data)
            if datas is None:
                not_found(
                    title=f"{self.entity_name} not found",
                    msg=f"{self.entity_name} does not exist"
                )

            return self.repo.schema.model_validate(datas).model_dump(mode="json")
        except Exception as e:
            logger.error(f"Err in update_one_with_filters: {e}", exc_info=e)
            raise

    def delete_by_id(self, id, soft_delete=True):
        """
        Delete a record by its ID.

        Args:
            id: The ID of the record to delete.
            soft_delete: Whether to perform a soft delete (default: True).

        Returns:
            The result of the delete operation.

        Raises:
            Exception: If an error occurs during record deletion.
        """
        try:
            datas = self.get_by_id(id=id)
            if not datas:
                not_found(
                    title=f"{self.entity_name} not found",
                    msg=f"{self.entity_name} with id '{id}' does not exist"
                )
            
            return self.repo.delete_by_id(id, soft_delete=soft_delete)
        except Exception as e:
            logger.error(f"Err in delete_by_id: {e}", exc_info=e)
            raise
