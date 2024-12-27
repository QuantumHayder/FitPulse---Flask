from typing import Self, Optional
from datetime import datetime, time, date

from . import db
from .trainer import Trainer


class TrainingClass:
    def __init__(  # Keep order or __init__ consistent with the database
        self,
        trainer: int,
        date: date,
        time: time,
        duration: int,
        title: str,
        description: Optional[str],
        cost: int,
        *args,
        **kwargs,
    ) -> None:
        self.id = kwargs.get("id")
        self.title = title
        self.description = description
        self.trainer = trainer
        self.date = date
        self.time = time
        self.duration = duration
        self.cost = cost

    def get_trainer(self):
        return Trainer.get(self.trainer)

    @classmethod
    def get(cls, id: int):
        classes = db.fetch_query(
            'SELECT * FROM public."TrainingClass" as c, public."Trainer" as t WHERE c.id = %s AND c.trainer = t.id',
            (id,),
        )

        if not classes:
            return None

        class_and_trainer = classes[0]

        training_class: list = class_and_trainer[:8]
        trainer: list = class_and_trainer[8:]

        return cls(id=training_class.pop(0), *training_class), Trainer(
            id=trainer.pop(0), password=trainer.pop(1), *trainer
        )

    @classmethod
    def get_all(cls):
        classes = db.fetch_query('SELECT * FROM public."TrainingClass";')
        return [cls(**training_class) for training_class in classes]
    
    @classmethod
    def avgClassCost(cls):
        result = db.fetch_query('SELECT AVG(cost) as average_cost FROM public."TrainingClass";')
        average_cost = result[0]['average_cost'] if result else None
        return round(average_cost, 2) if average_cost is not None else None
    
    @classmethod
    def insert(cls, training_class: Self) -> None:
        if training_class.title is None:
            raise ValueError("Cannot insert training class with title set to NULL.")
        if training_class.trainer is None:
            raise ValueError("Cannot insert training class with trainer set to NULL.")
        if training_class.date is None:
            raise ValueError("Cannot insert training class with date set to NULL.")
        if training_class.time is None:
            raise ValueError("Cannot insert training class with time set to NULL.")
        if training_class.duration is None:
            raise ValueError("Cannot insert training class with duration set to NULL.")
        if training_class.cost is None:
            raise ValueError("Cannot insert training class with cost set to NULL.")

        trainer = Trainer.get(training_class.trainer)

        if trainer is None:
            raise ValueError("Cannot assign training class to non existing trainer.")

        db.execute_query(
            'INSERT INTO public."TrainingClass" ("title", "description", "trainer", "date", "time", "duration", "cost") VALUES (%s, %s, %s, %s, %s, %s, %s)',
            (
                training_class.title,
                training_class.description,
                training_class.trainer,
                training_class.date,
                training_class.time,
                training_class.duration,
                training_class.cost,
            ),
        )

    @classmethod
    def search(
        cls,
        title: Optional[str] = None,
        trainer: Optional[int] = None,
    ):
        if not title and trainer is None:
            return TrainingClass.get_all()

        query = 'SELECT * FROM public."TrainingClass" WHERE '
        conditions = []
        variables = []

        if trainer is not None:
            conditions.append("trainer=%s")
            variables.append(trainer)

        if title:
            conditions.append("title ILIKE %s")
            variables.append("%" + title + "%")

        query += " AND ".join(conditions) + ";"

        classes = db.fetch_query(query, variables)
        return [cls(**training_class) for training_class in classes]

    @classmethod
    def delete(cls, id: int) -> None:
        db.execute_query('DELETE FROM public."TrainingClass" WHERE id = %s;', (id,))

    def __str__(self):
        return f"Training_Class(id={self.id}, title={self.title}, description={self.description}, trainer={self.trainer}, date={self.date}, time={self.time}, duration={self.duration}, cost={self.cost})"
