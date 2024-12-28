from typing import Self, Optional
from datetime import datetime, time, date

from . import db
from .trainer import Trainer
import src.models.promotion as promotion


class TrainingClass:
    def __init__(
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

    def get_current_promotion(self):
        p = promotion.Promotion.get(self.id)

        if not p:
            return None

        return p.amount

    def get_trainer(self):
        return Trainer.get(self.trainer)

    def student_count(self):
        classes = db.fetch_query(
            'SELECT COUNT(*) as count FROM public."ClientTrainingClassMap" WHERE training_class = %s',
            (self.id,),
        )

        if not classes:
            return 0

        return classes[0]["count"]

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
    def get_all_by_trainer(cls, trainer_id):
        classes = db.fetch_query(
            'SELECT * FROM public."TrainingClass" WHERE trainer = %s;', (trainer_id,)
        )
        return [cls(**training_class) for training_class in classes]

    @classmethod
    def get_all(cls):
        classes = db.fetch_query('SELECT * FROM public."TrainingClass";')
        return [cls(**training_class) for training_class in classes]

    @classmethod
    def avg_class_cost(cls):
        result = db.fetch_query(
            'SELECT AVG(cost) as average_cost FROM public."TrainingClass";'
        )
        average_cost = result[0]["average_cost"] if result else None

        return round(average_cost, 2) if average_cost is not None else None

    @classmethod
    def class_and_trainer(cls):
        query = """
        SELECT training_class, COUNT(client) as client_count 
        FROM public."ClientTrainingClassMap" 
        GROUP BY training_class 
        ORDER BY client_count DESC;
        """

        result = db.fetch_query(query)
        if not result:
            return None, None, None, None
        best_class_id = result[0][0]
        worst_class_id = result[-1][0]
        # -1,0
        best_training_class, best_trainer = TrainingClass.get(best_class_id) or (
            None,
            None,
        )
        worst_training_class, worst_trainer = TrainingClass.get(worst_class_id) or (
            None,
            None,
        )

        if best_training_class and worst_training_class:
            return (
                best_training_class,
                best_trainer,
                worst_training_class,
                worst_trainer,
            )
        else:
            best_training_class, best_trainer, worst_training_class, worst_trainer = (
                None,
                None,
                None,
                None,
            )
            return (
                best_training_class,
                best_trainer,
                worst_training_class,
                worst_trainer,
            )

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
