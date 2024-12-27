from .base_user import BaseUser, UserRole


class Trainer(BaseUser):
    role: UserRole = UserRole.Trainer

    def __init__(self, email: str, first_name: str, last_name: str, *args, **kwargs):
        super().__init__(email, first_name, last_name, *args, **kwargs)
