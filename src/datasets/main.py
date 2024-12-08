import pandas as pd
import numpy as np

from ..models.exercise import Exercise


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
