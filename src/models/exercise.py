from typing import Self, Optional

from . import db
from .exercise_enums import ExerciseType, BodyPart, Equipment, Level


class Exercise:
    def __init__(
        self,
        title: str,
        description: str,
        type: ExerciseType,
        body_part: BodyPart,
        equipment: Equipment,
        level: Level,
        *args,
        **kwargs,
    ) -> None:
        self.id = kwargs.get("id")
        self.title = title
        self.description = description
        self.type = type
        self.body_part = body_part
        self.equipment = equipment
        self.level = level

    @classmethod
    def get(cls, id: int):
        exercises = db.fetch_query(
            'SELECT * FROM public."Exercise" WHERE id = %s ', (id,)
        )

        if not exercises:
            return None

        user = exercises[0]

        return cls(**user)

    @classmethod
    def get_all(cls):
        exercises = db.fetch_query('SELECT * FROM public."Exercise";')
        return [cls(**exercise) for exercise in exercises]

    @classmethod
    def insert(cls, exercise: Self) -> None:
        if exercise.title is None:
            raise ValueError("Cannot insert exercise with title set to NULL.")
        if exercise.type is None:
            raise ValueError("Cannot insert exercise with type set to NULL.")
        if exercise.body_part is None:
            raise ValueError("Cannot insert exercise with body_part set to NULL.")
        if exercise.level is None:
            raise ValueError("Cannot insert exercise with level set to NULL.")

        db.execute_query(
            'INSERT INTO public."Exercise" ("title", "description", "type", "body_part", "equipment", "level") VALUES (%s, %s, %s, %s, %s, %s)',
            (
                exercise.title,
                exercise.description,
                exercise.type,
                exercise.body_part,
                exercise.equipment,
                exercise.level,
            ),
        )

    @classmethod
    def search(
        cls,
        title: Optional[str] = None,
        type: Optional[ExerciseType] = None,
        body_part: Optional[BodyPart] = None,
        equipment: Optional[Equipment] = None,
        level: Optional[Level] = None,
    ):
        values = (title, type, body_part, equipment, level)
        if all(not bool(value) for value in values):
            return Exercise.get_all()

        query = 'SELECT * FROM public."Exercise" WHERE '
        conditions = []
        variables = []

        if title:
            conditions.append("title ILIKE %s")
            variables.append("%" + title + "%")

        if type:
            conditions.append("type=%s")
            variables.append(type)

        if body_part:
            conditions.append("body_part=%s")
            variables.append(body_part)

        if equipment:
            conditions.append("equipment=%s")
            variables.append(equipment)

        if level:
            conditions.append("level=%s")
            variables.append(level)

        query += " AND ".join(conditions) + ";"

        exercises = db.fetch_query(query, variables)
        return [cls(**exercise) for exercise in exercises]

    @classmethod
    def delete(cls, id: int) -> None:
        db.execute_query('DELETE FROM public."Exercise" WHERE id = %s;', (id,))

    def __str__(self):
        return f"Exercise(id={self.id}, title={self.title}, type={self.type}, body_part={self.body_part}, level={self.level}, equipment={self.equipment})"
