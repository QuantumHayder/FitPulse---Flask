from enum import StrEnum
from typing import Self, Optional
from flask_login import UserMixin
from werkzeug.security import generate_password_hash
from . import db


class UserRole(StrEnum):
    User = "User"
    Admin = "Admin"
    Client = "Client"
    Trainer = "Trainer"


class BaseUser(UserMixin):

    role: UserRole = UserRole.User

    def __init__(
        self, email: str, first_name: str, last_name: str, *args, **kwargs
    ) -> None:
        self.email = email
        self.first_name = first_name
        self.last_name = last_name
        self.id = kwargs.get("id")
        self._password = kwargs.get("password")

    def set_password(self, password: str) -> None:
        self._password = generate_password_hash(password)

    def get_id(self) -> str:
        return str(self.id) + "-" + self.role

    @classmethod
    def get(cls, id: int) -> Optional[Self]:
        users = db.fetch_query(
            f'SELECT * FROM public."{cls.__name__}" WHERE id = %s ', (id,)
        )
        if not users:
            return None

        user = users[0]

        return cls(**user)

    @classmethod
    def get_all(cls) -> list[Self]:
        users = db.fetch_query(f'SELECT * FROM public."{cls.__name__}";')

        return [cls(**user) for user in users]

    @classmethod
    def get_password(cls, id: int) -> Optional[str]:
        passwords = db.fetch_query(
            f'SELECT password FROM public."{cls.__name__}" WHERE id = %s',
            (id,),
        )
        if len(passwords) != 1:
            return None
        return passwords[0][0]

    @classmethod
    def update_password(cls, id: int, password: str) -> None:
        db.execute_query(
            f'UPDATE public."{cls.__name__}" SET password = %s WHERE id = %s',
            (generate_password_hash(password), id),
        )

    @classmethod
    def get_by_email(cls, email: str) -> Optional[Self]:
        users = db.fetch_query(
            f'SELECT * FROM public."{cls.__name__}" WHERE "email" = %s', (email,)
        )

        if not users:
            return None

        user = users[0]

        return cls(**user)

    @classmethod
    def insert(cls, user: Self) -> None:
        if user._password is None:
            raise ValueError("Cannot insert user with password set to NULL.")
        if None in (user.first_name, user.last_name):
            raise ValueError("Cannot insert user with name set to NULL.")
        if user.email is None:
            raise ValueError("Cannot insert user with email set to NULL.")

        db.execute_query(
            f'INSERT INTO public."{cls.__name__}" ("first_name", "last_name", "email", "password") VALUES (%s, %s, %s, %s)',
            (user.first_name, user.last_name, user.email, user._password),
        )

    @classmethod
    def update(
        cls,
        id: int,
        first_name: Optional[str],
        last_name: Optional[str],
        email: Optional[str],
    ) -> None:
        if first_name:
            db.execute_query(
                f'UPDATE public."{cls.__name__}" SET "first_name" = %s WHERE "id" = %s',
                (first_name, id),
            )
        if last_name:
            db.execute_query(
                f'UPDATE public."{cls.__name__}" SET "last_name" = %s WHERE "id" = %s',
                (last_name, id),
            )
        if email:
            db.execute_query(
                f'UPDATE public."{cls.__name__}" SET "email" = %s WHERE "id" = %s',
                (email, id),
            )

    @classmethod
    def delete(cls, id: int) -> None:
        db.execute_query(f'DELETE FROM public."{cls.__name__}" WHERE id = %s;', (id,))

    @classmethod
    def count_all(cls) -> int:
        users = db.fetch_query(f'SELECT COUNT(*) as count FROM public."{cls.__name__}";')
        return users[0]['count'] if users else 0

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email})"
