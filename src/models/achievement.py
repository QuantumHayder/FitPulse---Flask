from typing import Self, Optional

from . import db
from .exercise import Exercise
from .exercise_enums import Level


class Achievement:
    def __init__(
        self,
        exercise: int,
        title: str,
        description: str,
        points: int,
        level: Level,
        reps: int,
        *args,
        **kwargs,
    ) -> None:
        self.id = kwargs.get("id")
        self.exercise = exercise
        self.title = title
        self.description = description
        self.points = points
        self.level = level
        self.reps = reps

    @classmethod
    def get(cls, id: int):
        achievements = db.fetch_query(
            'SELECT * FROM public."Achievement" WHERE id = %s ', (id,)
        )

        if not achievements:
            return None

        achievement = achievements[0]

        exercises = db.fetch_query(
            'SELECT * FROM public."Exercise" WHERE id = %s ', (achievement["exercise"],)
        )

        if not exercises:
            return None

        return Achievement(**achievement), Exercise(**exercises[0])

    @classmethod
    def get_all(cls):
        achievements = db.fetch_query('SELECT * FROM public."Achievement";')
        return [cls(**achievement) for achievement in achievements]

    @classmethod
    def insert(cls, achievement: Self) -> None:
        if achievement.title is None:
            raise ValueError("Cannot insert Achievement with title set to NULL.")
        if achievement.exercise is None:
            raise ValueError("Cannot insert Achievement with exericse set to NULL.")
        if achievement.level is None:
            raise ValueError("Cannot insert Achievement with level set to NULL.")
        if achievement.points is None:
            raise ValueError("Cannot insert Achievement with points set to NULL.")
        if achievement.reps is None:
            raise ValueError("Cannot insert Achievement with reps set to NULL.")

        exercises = Exercise.get(achievement.exercise)

        if not exercises:
            raise ValueError("Cannot assign the achievement to non existing exercise!")

        db.execute_query(
            'INSERT INTO public."Achievement" ("title", "description", "exercise", "level", "points", "reps") VALUES (%s, %s, %s, %s, %s, %s)',
            (
                achievement.title,
                achievement.description,
                achievement.exercise,
                achievement.level,
                achievement.points,
                achievement.reps,
            ),
        )

    @classmethod
    def search(
        cls,
        title: Optional[str] = None,
        exercise: Optional[int] = None,
        level: Optional[Level] = None,
    ):
        values = (title, exercise, level)
        if all(not bool(value) for value in values):
            return Achievement.get_all()

        query = 'SELECT * FROM public."Achievement" WHERE '
        conditions = []
        variables = []

        if title:
            conditions.append("title ILIKE %s")
            variables.append("%" + title + "%")

        if exercise:
            conditions.append("exercise=%s")
            variables.append(exercise)

        if level:
            conditions.append("level=%s")
            variables.append(level)

        query += " AND ".join(conditions) + ";"

        achievements = db.fetch_query(query, variables)

        return [cls(**achievement) for achievement in achievements]

    @classmethod
    def delete(cls, id: int) -> None:
        db.execute_query('DELETE FROM public."Achievement" WHERE id = %s;', (id,))

    def __str__(self):
        return f"Achievement(id={self.id}, title={self.title}, description={self.description}, exercise={self.exercise}, level={self.level}, points={self.points}, reps={self.reps})"
