from enum import StrEnum

from typing import Self

from . import db


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
        self.user = user
        self.timestamp = timestamp
        self.description = description
        self.linkedin_url = linkedin_url
        self.status = status

    @classmethod
    def get(cls, user_id: int):
        trainer_requests = db.fetch_query(
            'SELECT * FROM public."TrainerRequest" WHERE "user" = %s ', (user_id,)
        )

        if not trainer_requests:
            return None

        return [cls(**trainer_request) for trainer_request in trainer_requests]

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
    def delete(cls, user_id: int) -> None:
        db.execute_query(
            'DELETE FROM public."TrainerRequest" WHERE "user" = %s;', (user_id,)
        )

    def __str__(self):
        return f"TrainerRequest(user={self.user}, timestamp={self.timestamp}, linkedin_url={self.linkedin_url}, status={self.status})"


if __name__ == "__main__":
    from datetime import datetime

    r = TrainerRequest(
        22,
        datetime.now(),
        "This is my description",
        "https://www.linkedin.com/moalkhateeb",
        Status.Accepted,
    )

    TrainerRequest.insert(r)
