from .base_user import BaseUser, UserRole
from . import db

class Admin(BaseUser):
    role: UserRole = UserRole.Admin

    def __init__(self, email: str, first_name: str, last_name: str, *args, **kwargs):
        super().__init__(email, first_name, last_name, *args, **kwargs)

        
        
        
# a = Admin("abdallahahmed.wrk@gmail.com","a","b")
# a.set_password("123")
# Admin.insert(a)
