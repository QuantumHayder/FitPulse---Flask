from typing import Self, Optional
from . import db
from .training_class import TrainingClass
from .client import Client


class Review:
    def __init__(
        self,
        training_class: int,
        client: int,
        rating: int,
        description: Optional[str] = None,
        *args,
        **kwargs,
    ) -> None:
        self.client = client
        self.training_class = training_class
        self.rating = rating
        self.description = description

    @classmethod
    def get_all(cls):
        reviews = db.fetch_query('SELECT * FROM public."Review";')
        return [cls(**review) for review in reviews]

    @classmethod
    def insert(cls, review: Self) -> None:
        if review.training_class is None:
            raise ValueError("Cannot insert review with training_class set to NULL.")
        if review.client is None:
            raise ValueError("Cannot insert review with client set to NULL.")
        if review.rating is None:
            raise ValueError("Cannot insert review with rating set to NULL.")

        training_class = TrainingClass.get(review.training_class)

        if training_class is None:
            raise ValueError("Cannot assign review to non existing training class.")

        client = Client.get(review.client)

        if client is None:
            raise ValueError("Cannot assign review to non existing client.")

        db.execute_query(
            'INSERT INTO public."Review" ("training_class", "client", "rating", "description") VALUES (%s, %s, %s, %s)',
            (
                review.training_class,
                review.client,
                review.rating,
                review.description,
            ),
        )

    @classmethod
    def delete(cls, training_class: int, client: int) -> None:
        db.execute_query(
            'DELETE FROM public."Review" WHERE training_class = %s AND client = %s;',
            (
                training_class,
                client,
            ),
        )

    def __str__(self):
        return f"Review(training_class={self.training_class}, client={self.client}, rating={self.rating})"
