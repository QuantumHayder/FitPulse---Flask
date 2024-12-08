from .BaseUser import BaseUser, UserRole


class Client(BaseUser):
    role: UserRole = UserRole.Client

    def __init__(self, email: str, first_name: str, last_name: str, *args, **kwargs):
        super().__init__(email, first_name, last_name, *args, **kwargs)
