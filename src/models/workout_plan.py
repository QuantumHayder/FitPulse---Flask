from typing import Self

from . import db
from .client import Client
from .trainer import Trainer
from .exercise import Exercise


class WorkoutPlan:
    def __init__(
        self,
        trainer: int,
        client: int,
        is_active: bool,
        name: str,
        description: str,
        *args,
        **kwargs,
    ) -> None:
        self.id = kwargs.get("id")
        self.client = client
        self.trainer = trainer
        self.is_active = is_active
        self.name = name
        self.description = description

    def add_exercise(self, exercise_id: int):
        exercise = Exercise.get(exercise_id)

        if exercise is None:
            raise ValueError("Exercise does not exist.")

        db.execute_query(
            'INSERT INTO public."WorkoutPlanExerciseMap" ("workout", "exercise") VALUES (%s, %s)',
            (self.id, exercise_id),
        )

    def get_exercises(self):
        if WorkoutPlan.get(self.id) is None:
            return None

        exercises = db.fetch_query(
            'SELECT e.* FROM public."WorkoutPlanExerciseMap" as w, public."Exercise" as e WHERE w.exercise = e.id AND w.workout = %s ',
            (self.id,),
        )

        return [Exercise(id=exercise[0], *exercise[1:]) for exercise in exercises]

    @classmethod
    def get(cls, id: int):
        workout = db.fetch_query(
            'SELECT * FROM public."WorkoutPlan" WHERE id = %s ', (id,)
        )

        if not workout:
            return None

        user = workout[0]

        return cls(**user)

    @classmethod
    def get_client_workouts(cls, client_id: int):
        workouts = db.fetch_query(
            'SELECT * FROM public."WorkoutPlan" WHERE client = %s;', (client_id,)
        )
        return [cls(**workout) for workout in workouts]

    @classmethod
    def get_trainer_workouts(cls, trainer_id: int):
        workouts = db.fetch_query(
            'SELECT * FROM public."WorkoutPlan" WHERE trainer_id = %s;', (trainer_id,)
        )
        return [cls(**workout) for workout in workouts]

    def get_trainer(self):
        return Trainer.get(self.trainer)

    @classmethod
    def insert(cls, workout: Self) -> None:
        if workout.trainer is None:
            raise ValueError("Cannot insert workout with trainer_id set to NULL.")
        if workout.client is None:
            raise ValueError("Cannot insert workout with client_id set to NULL.")
        if workout.is_active is None:
            raise ValueError("Cannot insert workout with active set to NULL.")
        if workout.name is None:
            raise ValueError("Cannot insert workout with name set to NULL.")

        trainer = Trainer.get(workout.trainer)

        if trainer is None:
            raise ValueError("Cannot assign workout plan to non existing trainer.")

        client = Client.get(workout.client)

        if client is None:
            raise ValueError("Cannot assign workout plan to non existing client.")

        return db.fetch_query(
            'INSERT INTO public."WorkoutPlan" ("trainer", "client", "is_active", "name", "description") VALUES (%s, %s,%s, %s, %s) RETURNING id',
            (
                workout.trainer,
                workout.client,
                workout.is_active,
                workout.name,
                workout.description,
            ),
        )[0][0]

    @classmethod
    def delete(cls, id: int) -> None:
        db.execute_query('DELETE FROM public."WorkoutPlan" WHERE id = %s;', (id,))

    @classmethod
    def toggle_active(cls, id: int) -> None:
        db.execute_query(
            'UPDATE "WorkoutPlan" SET is_active = NOT is_active WHERE id = %s', (id,)
        )

    def __str__(self):
        return f"WorkoutPlan(id={self.id}, trainer={self.trainer}, client={self.client}, is_active={self.is_active}, name={self.name}, description={self.description})"
