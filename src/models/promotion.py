from typing import Self

from . import db
import src.models.training_class as training_class
from datetime import datetime, time, date


class Promotion:
    def __init__(
        self,
        amount: int,
        date: date,
        start: time,
        duration: int,
        training_class: int,
        *args,
        **kwargs,
    ) -> None:
        self.training_class = training_class
        self.amount = amount
        self.date = date
        self.start = start
        self.duration = duration

    @classmethod
    def avgPromotionAmount(cls):
        result = db.fetch_query(
            'SELECT AVG(amount) as promotion_amount FROM public."Promotion";'
        )
        average_promotion = result[0]["promotion_amount"] if result else None
        return round(average_promotion, 2) if average_promotion is not None else None

    @classmethod
    def get(cls, training_class: int):
        promotion = db.fetch_query(
            'SELECT * FROM public."Promotion" WHERE training_class = %s',
            (training_class,),
        )

        if not promotion:
            return None

        user = promotion[0]

        return cls(**user)

    @classmethod
    def insert(cls, promotion: Self) -> None:
        if promotion.training_class is None:
            raise ValueError("Cannot insert promotion with training_class set to NULL.")
        if promotion.amount is None:
            raise ValueError("Cannot insert promotion with amount set to NULL.")
        if promotion.date is None:
            raise ValueError("Cannot insert promotion with date set to NULL.")
        if promotion.start is None:
            raise ValueError("Cannot insert promotion with start set to NULL.")
        if promotion.duration is None:
            raise ValueError("Cannot insert promotion with duration set to NULL.")

        t = training_class.TrainingClass.get(promotion.training_class)

        if t is None:
            raise ValueError("Cannot assign promotion to non existing training_class.")

        try:
            db.execute_query(
                'INSERT INTO public."Promotion" ("training_class", "amount", "date", "start", "duration") VALUES (%s, %s, %s, %s, %s)',
                (
                    promotion.training_class,
                    promotion.amount,
                    promotion.date,
                    promotion.start,
                    promotion.duration,
                ),
            )
        except Exception:
            raise Exception("Training class already has a promotion.")

    @classmethod
    def delete(cls, training_class: int) -> None:
        db.execute_query(
            'DELETE FROM public."Promotion" WHERE training_class = %s',
            (training_class,),
        )

    def __str__(self):
        return f"Promotion(training_class={self.training_class}, amount={self.amount}, date={self.date}, start={self.start}, duration={self.duration})"
