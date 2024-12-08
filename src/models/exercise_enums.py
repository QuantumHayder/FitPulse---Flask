from enum import StrEnum


class ExerciseType(StrEnum):
    Strength = "Strength"
    Plyometrics = "Plyometrics"
    Cardio = "Cardio"
    Stretching = "Stretching"
    Powerlifting = "Powerlifting"
    Strongman = "Strongman"
    OlympicWeightlifting = "Olympic Weightlifting"


class BodyPart(StrEnum):
    Abdominals = "Abdominals"
    Adductors = "Adductors"
    Abductors = "Abductors"
    Biceps = "Biceps"
    Calves = "Calves"
    Chest = "Chest"
    Forearms = "Forearms"
    Glutes = "Glutes"
    Hamstrings = "Hamstrings"
    Lats = "Lats"
    LowerBack = "Lower Back"
    MiddleBack = "Middle Back"
    Traps = "Traps"
    Neck = "Neck"
    Quadriceps = "Quadriceps"
    Shoulders = "Shoulders"
    Triceps = "Triceps"


class Level(StrEnum):
    Beginner = "Beginner"
    Intermediate = "Intermediate"
    Expert = "Expert"


class Equipment(StrEnum):
    Bands = "Bands"
    Barbell = "Barbell"
    Kettlebells = "Kettlebells"
    Dumbbell = "Dumbbell"
    Other = "Other"
    Cable = "Cable"
    Machine = "Machine"
    BodyOnly = "Body Only"
    MedicineBall = "Medicine Ball"
    ExerciseBall = "Exercise Ball"
    FoamRoll = "Foam Roll"
    EZCurlBar = "E-Z Curl Bar"
