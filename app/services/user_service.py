import re
from app.schemas.user import *
from app.repositories.user_repository import UserRepository
from app.services.base import BaseService
from app.utils.logger import logger
from app.utils.other import check_string, hash_string
from app.utils.jwt import create_access_token
from app.utils.http_exceptions import not_found, unauthorized, conflict

class UserService(BaseService[UserRepository]):
    EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
    
    def __init__(self):
        # We pass the repo and the schema variable to the parent
        super().__init__(repository=UserRepository())
        
    def auth_login(self, payload: dict = {}):
        try:
            identity = payload.get("identity")
            password = payload.get("password")

            # detect email or username
            if self.EMAIL_REGEX.match(identity):
                identity = "email"
            else:
                identity = "username"
                
            user_exist = self.get_one_by_filters({
                identity: payload.get("identity")
            }, to_model=True)

            if not user_exist:
                not_found(msg="Email or Username not found.")

            if not check_string(password, user_exist.password):
                unauthorized(msg="Password is incorrect.")
            
            user_resp = UserPublicResponse.model_validate(user_exist).model_dump(mode="json")
            
            token = create_access_token(user_resp)
            
            return {
                **user_resp,
                "token": token,
            }
        
        except Exception as e:
            logger.error(f"Err in auth_login: {e}", exc_info=e)
            raise e

    def auth_register(self, payload: dict):
        try:
            email = payload.get("email")
            if self.get_one_by_filters({"email": email}, to_model=True, raise_error=False):
                conflict("Registration Failed", "This email already exists.")

            user_data = UserCreate.model_validate(payload)
            user_dict = user_data.model_dump()
            user_dict["password"] = hash_string(user_dict["password"])
            
            new_user = self.create(user_dict)
            
            return UserPublicResponse.model_validate(new_user).model_dump(mode="json")

        except Exception as e:
            logger.error(f"Err in auth_register: {str(e)}", exc_info=True)
            raise e
    