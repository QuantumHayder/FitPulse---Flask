from enum import StrEnum

from typing import Self


from . import db
from .user import User


class Status(StrEnum):
    Accepted = "Accepted"
    Pending = "Pending"
    Rejected = "Rejected"


class TrainerRequest:
    def __init__(
        self,
        user: int,
        timestamp: int,
        description: str,
        linkedin_url: str,
        status: Status = Status.Pending,
        *args,
        **kwargs,
    ) -> None:
        self.request_id = kwargs.get("request_id")
        self.user = user
        self.timestamp = timestamp
        self.description = description
        self.linkedin_url = linkedin_url
        self.status = status

    def accept_request(self):
        db.execute_query(
            'UPDATE public."TrainerRequest" SET "status" = %s WHERE "request_id" = %s ',
            (
                Status.Accepted,
                self.request_id,
            ),
        )

    def reject_request(self):
        db.execute_query(
            'UPDATE public."TrainerRequest" SET "status" = %s WHERE "request_id" = %s ',
            (
                Status.Rejected,
                self.request_id,
            ),
        )

    @classmethod
    def get(cls, request_id: int):
        trainer_requests = db.fetch_query(
            'SELECT * FROM public."TrainerRequest" WHERE "request_id" = %s ',
            (request_id,),
        )

        if not trainer_requests:
            return None

        trainer_request = trainer_requests[0]

        return cls(**trainer_request)

    @classmethod
    def get_by_user(cls, user_id: int):
        trainer_requests = db.fetch_query(
            'SELECT * FROM public."TrainerRequest" WHERE "user" = %s ', (user_id,)
        )

        if not trainer_requests:
            return None

        trainer_requests.sort(key=lambda r: r["timestamp"], reverse=True)

        return [cls(**trainer_request) for trainer_request in trainer_requests]

    @classmethod
    def get_all(cls):
        requests = db.fetch_query(
            'SELECT * FROM public."TrainerRequest" as t, public."User" as u WHERE t.user = u.id;'
        )

        return [(cls(**r), User(**r)) for r in requests]
    
    @classmethod
    def count_rejected(cls):
        requests = db.fetch_query(
            f'SELECT COUNT(*) as count FROM public."TrainerRequest" WHERE status = %s;', (Status.Rejected,)
        )
        return requests[0]['count'] if requests else 0
    @classmethod
    def count_pending(cls):
        requests = db.fetch_query(
            f'SELECT COUNT(*) as count FROM public."TrainerRequest" WHERE status = %s;', (Status.Pending,)
        )
        return requests[0]['count'] if requests else 0



    @classmethod
    def insert(cls, trainer_request: Self) -> None:
        if trainer_request.user is None:
            raise ValueError("Cannot insert trainer_request with user set to NULL.")
        if trainer_request.timestamp is None:
            raise ValueError(
                "Cannot insert trainer_request with timestamp set to NULL."
            )
        if trainer_request.description is None:
            raise ValueError(
                "Cannot insert trainer_request with description set to NULL."
            )
        if trainer_request.linkedin_url is None:
            raise ValueError("Cannot insert trainer_request with LI url set to NULL.")
        if trainer_request.status is None:
            raise ValueError("Cannot insert trainer_request with status set to NULL.")

        db.execute_query(
            'INSERT INTO public."TrainerRequest" ("user", "timestamp", "description", "linkedin_url", "status") VALUES (%s, %s, %s, %s, %s)',
            (
                trainer_request.user,
                trainer_request.timestamp,
                trainer_request.description,
                trainer_request.linkedin_url,
                trainer_request.status,
            ),
        )

    @classmethod
    def delete(cls, id: int) -> None:
        db.execute_query(
            'DELETE FROM public."TrainerRequest" WHERE "request_id" = %s;', (id,)
        )

    def __str__(self):
        return f"TrainerRequest(request_id={self.request_id}, user={self.user}, timestamp={self.timestamp}, linkedin_url={self.linkedin_url}, status={self.status})"
