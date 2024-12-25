from typing import Self

from . import db
from .client import Client
from .food import Food
from datetime import datetime


class FoodLog:
    def __init__(
        self,
        client: int,
        timestamp: datetime,
        *args,
        **kwargs,
    ) -> None:
        self.id = kwargs.get("id")
        self.client = client
        self.timestamp = timestamp

    def get_food(self):
        food = db.fetch_query(
            'SELECT * FROM public."LogFoodMap" as l, public."Food" as e WHERE l.log = %s AND l.food = e.id',
            (self.id,),
        )

        return [Food(**f) for f in food]

    def insert_food(self, food: int) -> None:
        f = Food.get(food)
        if not f:
            raise ValueError("Cannot add a non-existent food to log.")

        db.execute_query(
            'INSERT INTO public."LogFoodMap" ("log", "food") VALUES (%s, %s)',
            (self.id, food),
        )

    @classmethod
    def get(cls, id: int):
        food_logs = db.fetch_query(
            'SELECT * FROM public."FoodLog" WHERE id = %s ', (id,)
        )

        if not food_logs:
            return None

        log = cls(**food_logs[0])

        return log, log.get_food()

    @classmethod
    def get_all(cls, client_id: int):
        food_logs = db.fetch_query(
            'SELECT * FROM public."FoodLog" WHERE client=%s;', (client_id,)
        )
        return [cls(**food_log) for food_log in food_logs]

    @classmethod
    def insert(cls, food_log: Self) -> None:
        if food_log.client is None:
            raise ValueError("Cannot insert log with client set to NULL.")
        if food_log.timestamp is None:
            raise ValueError("Cannot insert log with timestamp set to NULL.")

        client = Client.get(food_log.client)

        if not client:
            raise ValueError("Cannot create a log without an existing client.")

        db.execute_query(
            'INSERT INTO public."FoodLog" ("client", "timestamp") VALUES (%s, %s)',
            (
                food_log.client,
                food_log.timestamp,
            ),
        )

    @classmethod
    def delete(cls, id: int) -> None:
        db.execute_query('DELETE FROM public."FoodLog" WHERE id = %s;', (id,))

    def __str__(self):
        return (
            f"FoodLog(id={self.id}, client={self.client}, timestamp={self.timestamp})"
        )
