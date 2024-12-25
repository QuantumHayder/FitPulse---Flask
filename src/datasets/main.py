import os
import pandas as pd
import numpy as np

from ..models.exercise import Exercise
from ..models.food import Food


def load_exercises():
    df = pd.read_csv("src/datasets/megaGymDataset.csv").replace({np.nan: None})
    for _, row in df.iterrows():
        e = Exercise(
            row["Title"],
            row["Desc"],
            row["Type"],
            row["BodyPart"],
            row["Equipment"],
            row["Level"],
        )
        Exercise.insert(e)


def load_food():
    BASE_PATH = "src/datasets/FINAL FOOD DATASET"
    files = (
        os.path.join(BASE_PATH, file)
        for file in os.listdir(BASE_PATH)
        if file.endswith(".csv")
    )

    for file in files:
        df = pd.read_csv(file)
        for _, row in df.iterrows():
            f = Food(
                name=row["food"],
                calories=row["Caloric Value"],
                carbs=row["Carbohydrates"],
                proteins=row["Protein"],
                fats=row["Fat"],
            )
            Food.insert(f)
