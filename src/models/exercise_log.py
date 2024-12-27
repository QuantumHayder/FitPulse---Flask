from typing import Self

from . import db
from .client import Client
from .exercise import Exercise
from datetime import datetime


class ExerciseLog:
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

    def get_exercises(self):
        exercises = db.fetch_query(
            'SELECT * FROM public."LogExerciseMap" as l, public."Exercise" as e WHERE l.log = %s AND l.exercise = e.id',
            (self.id,),
        )

        return [(Exercise(**exercise), exercise["reps"]) for exercise in exercises]

    def insert_exercise(self, exercise: int, reps: int) -> None:
        e = Exercise.get(exercise)
        if not e:
            raise ValueError("Cannot add a non-existent exercise to log.")

        db.execute_query(
            'INSERT INTO public."LogExerciseMap" ("log", "exercise", "reps") VALUES (%s, %s, %s)',
            (self.id, exercise, reps),
        )

    def update_exercise(self, exercise: int, reps: int) -> None:
        e = Exercise.get(exercise)
        if not e:
            raise ValueError("Cannot update a non-existent exercise to log.")

        l = ExerciseLog.get(self.id)
        if not l:
            raise ValueError("Cannot update a non-existent log in ExerciseLogMap.")

        exercises_log = db.fetch_query(
            'SELECT * FROM public."LogExerciseMap" WHERE log = %s AND exercise= %s ',
            (self.id, exercise),
        )

        if not exercises_log:
            return None

        db.execute_query(
            'UPDATE public."LogExerciseMap" SET reps = %s WHERE log= %s AND exercise= %s',
            (reps, self.id, exercise),
        )

    @classmethod
    def get(cls, id: int):
        exercises_log = db.fetch_query(
            'SELECT * FROM public."ExerciseLog" WHERE id = %s ', (id,)
        )

        if not exercises_log:
            return None

        log = cls(**exercises_log[0])

        return log, log.get_exercises()

    @classmethod
    def get_all(cls, client_id: int):
        exercises_log = db.fetch_query(
            'SELECT * FROM public."ExerciseLog" WHERE client=%s;', (client_id,)
        )
        return [cls(**exercise_log) for exercise_log in exercises_log]

    @classmethod
    def insert(cls, exercise_log: Self) -> None:
        if exercise_log.client is None:
            raise ValueError("Cannot insert log with client set to NULL.")
        if exercise_log.timestamp is None:
            raise ValueError("Cannot insert log with timestamp set to NULL.")

        client = Client.get(exercise_log.client)

        if not client:
            raise ValueError("Cannot create a log without an existing client.")

        db.execute_query(
            'INSERT INTO public."ExerciseLog" ("client", "timestamp") VALUES (%s, %s)',
            (
                exercise_log.client,
                exercise_log.timestamp,
            ),
        )

    @classmethod
    def delete(cls, id: int) -> None:
        db.execute_query('DELETE FROM public."ExerciseLog" WHERE id = %s;', (id,))

    def __str__(self):
        return f"ExerciseLog(id={self.id}, client={self.client}, timestamp={self.timestamp})"


if __name__ == "__main__":
    log, exercises = ExerciseLog.get(7)

    log.insert_exercise(603, 10)
    log.insert_exercise(605, 2)
