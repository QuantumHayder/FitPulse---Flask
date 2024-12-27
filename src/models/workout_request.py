from typing import Self

from . import db
import src.models.client as client
import src.models.trainer as trainer
from datetime import date, datetime
from .trainer_request import Status


class WorkoutRequest:
    def __init__(
        self,
        client: int,
        timestamp: date,
        trainer: int,
        description: str,
        status: str = Status.Pending,
        *args,
        **kwargs,
    ) -> None:
        self.id = kwargs.get("id")
        self.client = client
        self.timestamp = timestamp
        self.trainer = trainer
        self.description = description
        self.status = status

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

        t = trainer.Trainer.get(workout_request.trainer)

        if t is None:
            raise ValueError("Cannot assign workout plan to non existing trainer.")

        c = client.Client.get(workout_request.client)

        if c is None:
            raise ValueError("Cannot assign workout plan to non existing client.")

        db.execute_query(
            'INSERT INTO public."WorkoutRequest" ("client", "timestamp", "trainer", "description", "status") VALUES (%s, %s, %s, %s, %s)',
            (
                workout_request.client,
                workout_request.timestamp,
                workout_request.trainer,
                workout_request.description,
                workout_request.status,
            ),
        )

    @classmethod
    def delete(cls, id: int) -> None:
        db.execute_query(
            'DELETE FROM public."WorkoutRequest" WHERE id = %s',
            (id,),
        )

    def update_status(self, new_status: Status):
        if self.status == new_status:
            return
        db.execute_query(
            'UPDATE public."WorkoutRequest" SET status = %s WHERE id = %s;',
            (new_status, self.id),
        )

    @classmethod
    def get(cls, plan_id: int):
        requests = db.fetch_query(
            'SELECT * FROM public."WorkoutRequest" WHERE id = %s ',
            (plan_id,),
        )
        if not requests:
            return None

        return cls(**requests[0])

    def get_trainer(self):
        return trainer.Trainer.get(self.trainer)

    def get_client(self):
        return client.Client.get(self.client)

    def __str__(self):

        return f"WorkoutRequest(id={self.id}, client={self.client}, timestamp={self.timestamp}, trainer={self.trainer}, description={self.description}, status={self.status})"
