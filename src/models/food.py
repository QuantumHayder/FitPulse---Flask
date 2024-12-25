from typing import Self, Optional
from . import db


class Food:
    def __init__(
        self,
        name: str,
        calories: float,
        carbs: float,
        proteins: float,
        fats: float,
        *args,
        **kwargs,
    ) -> None:
        self.id = kwargs.get("id")
        self.name = name
        self.calories = calories
        self.carbs = carbs
        self.proteins = proteins
        self.fats = fats

    @classmethod
    def get(cls, id: int):
        foods = db.fetch_query('SELECT * FROM public."Food" WHERE id = %s ', (id,))

        if not foods:
            return None

        user = foods[0]

        return cls(**user)

    @classmethod
    def get_all(cls):
        foods = db.fetch_query('SELECT * FROM public."Food";')
        return [cls(**food) for food in foods]

    @classmethod
    def insert(cls, food: Self) -> None:
        if food.name is None:
            raise ValueError("Cannot insert food with name set to NULL.")
        if food.calories is None:
            raise ValueError("Cannot insert food with calories set to NULL.")
        if food.carbs is None:
            raise ValueError("Cannot insert food with carbs set to NULL.")
        if food.proteins is None:
            raise ValueError("Cannot insert food with protein set to NULL.")
        if food.fats is None:
            raise ValueError("Cannot insert food with fats set to NULL.")

        db.execute_query(
            'INSERT INTO public."Food" ("name", "calories", "carbs", "proteins", "fats") VALUES (%s, %s, %s, %s, %s)',
            (
                food.name,
                food.calories,
                food.carbs,
                food.proteins,
                food.fats,
            ),
        )

    @classmethod
    def search(cls, name: Optional[str] = None):
        if not name:
            return Food.get_all()

        foods = db.fetch_query(
            'SELECT * FROM public."Food" WHERE name ILIKE %s;', (f"%{name}%",)
        )

        return [cls(**food) for food in foods]

    @classmethod
    def delete(cls, id: int) -> None:
        db.execute_query('DELETE FROM public."Food" WHERE id = %s;', (id,))

    def __str__(self):
        return f"Food(id={self.id}, name={self.name}, calories={self.calories}, carbs={self.carbs}, proteins={self.proteins}, fats={self.fats})"
