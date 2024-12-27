from typing import Self

from . import db
from .client import Client
from .trainer import Trainer
from datetime import date, datetime


class WorkoutRequest:
    def __init__(
        self,
        client: int,
        timestamp: date,
        trainer: int,
        description: str,
        *args,
        **kwargs,
    ) -> None:
        self.id = kwargs.get("id")
        self.client = client
        self.timestamp = timestamp
        self.trainer = trainer
        self.description = description

    @classmethod
    def get_requests_by_trainer(cls, trainer: int):
        workout_requests = db.fetch_query(
            'SELECT * FROM public."WorkoutRequest" WHERE trainer = %s',
            (trainer,),
        )

        if not workout_requests:
            return None

        return [cls(**r) for r in workout_requests]

    @classmethod
    def get_requests_by_client(cls, client: int):
        workout_requests = db.fetch_query(
            'SELECT * FROM public."WorkoutRequest" WHERE client = %s',
            (client,),
        )

        if not workout_requests:
            return None

        return [cls(**r) for r in workout_requests]

    @classmethod
    def insert(cls, workout_request: Self) -> None:
        if workout_request.client is None:
            raise ValueError("Cannot insert workout_request with client set to NULL.")

        if workout_request.trainer is None:
            raise ValueError("Cannot insert workout_request with trainer set to NULL.")

        if workout_request.timestamp is None:
            raise ValueError(
                "Cannot insert workout_request with timestamp set to NULL."
            )
        if not workout_request.description:
            raise ValueError(
                "Cannot insert workout_request with description set to NULL."
            )

        trainer = Trainer.get(workout_request.trainer)

        if trainer is None:
            raise ValueError("Cannot assign workout plan to non existing trainer.")

        client = Client.get(workout_request.client)

        if client is None:
            raise ValueError("Cannot assign workout plan to non existing client.")

        db.execute_query(
            'INSERT INTO public."WorkoutRequest" ("client", "timestamp", "trainer", "description") VALUES (%s, %s, %s, %s)',
            (
                workout_request.client,
                workout_request.timestamp,
                workout_request.trainer,
                workout_request.description,
            ),
        )

    @classmethod
    def delete(cls, client: int, timestamp: date, trainer: int) -> None:
        db.execute_query(
            'DELETE FROM public."WorkoutRequest" WHERE client = %s AND timestamp = %s AND trainer = %s',
            (
                client,
                timestamp,
                trainer,
            ),
        )
    def get_trainer(self):
        return Trainer.get(self.trainer)
    
    def get_client(self):
        return Client.get(self.client)

    def __str__(self):
        return f"WorkoutRequest(client={self.client}, timestamp={self.timestamp}, trainer={self.trainer}, description={self.description})"