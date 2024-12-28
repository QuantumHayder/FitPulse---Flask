from typing import Self
from datetime import datetime
from .base_user import BaseUser, UserRole
from .trainer_request import Status
from .friend_request import FriendRequest

from src.models import db

from .training_class import TrainingClass
from .exercise import Exercise
from . import db


class Client(BaseUser):
    role: UserRole = UserRole.Client

    def __init__(
        self,
        email: str,
        first_name: str,
        last_name: str,
        *args,
        points: int = 0,
        calories: int = 2000,
        **kwargs,
    ):
        super().__init__(email, first_name, last_name, *args, **kwargs)
        self.points = points
        self.calories = calories

    @classmethod
    def get_all(cls):
        classes = db.fetch_query('SELECT * FROM public."Client";')
        return [cls(**training_class) for training_class in classes]

    def get_exercise_graph(self, exercise_id: int):
        counts = db.fetch_query(
            """SELECT timestamp, reps FROM public."ExerciseLog" as elog, public."LogExerciseMap" as emap 
                WHERE elog.client = %s AND emap.log = elog.id 
                AND emap.exercise = %s 
                ORDER BY timestamp 
                ASC;""",
            (self.id, exercise_id),
        )

        labels = [count[0] for count in counts]
        value = [count[1] for count in counts]
        return labels, value, Exercise.get(exercise_id)

    def update_points(self, points: int):
        db.execute_query(
            'UPDATE public."Client" SET points = %s WHERE id = %s;',
            (points, self.id),
        )

    def update_calories(self, calories: int):
        db.execute_query(
            'UPDATE public."Client" SET calories = %s WHERE id = %s;',
            (calories, self.id),
        )

    def get_friends(self):

        received = {
            r.sender
            for r in FriendRequest.get_all_received(self.id)
            if r.status == Status.Accepted
        }

        sent = {
            r.receiver
            for r in FriendRequest.get_all_sent(self.id)
            if r.status == Status.Accepted
        }

        user_ids = list(sent.union(received))

        return [Client.get(uid) for uid in user_ids]

    @classmethod
    def top_and_bottom_clients(cls):
        # Get all clients
        clients = cls.get_all()

        if not clients:
            return None, None

        friends_count = {}

        for client in clients:
            friends = client.get_friends()
            friends_count[client] = len(friends)

        top_client = max(friends_count, key=friends_count.get, default=None)

        bottom_client = min(friends_count, key=friends_count.get, default=None)

        return (top_client, friends_count[top_client]) if top_client else None, (
            (bottom_client, friends_count[bottom_client]) if bottom_client else None
        )

    def get_pending_requests_received(self):
        user_ids = [
            r.sender
            for r in FriendRequest.get_all_received(self.id)
            if r.status == Status.Pending
        ]

        return [Client.get(uid) for uid in user_ids]

    def reject_friend_request(self, other: Self) -> None:
        other_client = self.get(other.id)

        if other_client is None:
            raise ValueError("Cannot add a client that doesn't exist as a friend.")

        if self.id == other.id:
            raise ValueError("You cannot send a friend request to yourself.")

        if request := FriendRequest.get(other.id, self.id):
            request.update_status(Status.Rejected)

    def accept_friend_request(self, other: Self) -> None:
        other_client = self.get(other.id)

        if other_client is None:
            raise ValueError("Cannot add a client that doesn't exist as a friend.")

        if self.id == other.id:
            raise ValueError("You cannot send a friend request to yourself.")

        if request := FriendRequest.get(other.id, self.id):
            request.update_status(Status.Accepted)

    def send_friend_request(self, other: Self) -> None:
        other_client = self.get(other.id)

        if other_client is None:
            raise ValueError("Cannot add a client that doesn't exist as a friend.")

        if self.id == other.id:
            raise ValueError("You cannot send a friend request to yourself.")

        you_sent_request = FriendRequest.get(sender=self.id, receiver=other.id)

        if you_sent_request:
            raise ValueError("Cannot send a request to the same person again.")

        you_recieved_request = FriendRequest.get(sender=other.id, receiver=self.id)

        if you_recieved_request:
            you_recieved_request.update_status(Status.Accepted)
            return

        FriendRequest.insert(
            FriendRequest(receiver=other.id, sender=self.id, status=Status.Pending)
        )

    def enrolled_classes(self):
        k = db.fetch_query(
            """
            SELECT "TrainingClass".id
            FROM public."ClientTrainingClassMap"
            JOIN public."TrainingClass" 
            ON "ClientTrainingClassMap".training_class = "TrainingClass".id
            WHERE "ClientTrainingClassMap".client = %s;
            """,
            (self.id,),
        )

        if not k:
            return []

        enrolled_classes = []

        for class_item in k:
            class_id = class_item[0]

            training_class, trainer = TrainingClass.get(class_id)

            enrolled_classes.append(
                {"training_class": training_class, "trainer": trainer}
            )

        return enrolled_classes

    def is_enrolled_in_class(self, class_id: int) -> bool:
        k = db.fetch_query(
            'SELECT * FROM public."ClientTrainingClassMap" WHERE "client" = %s AND "training_class" = %s;',
            (self.id, class_id),
        )

        return bool(k)

    def enroll_in_class(self, class_id: int) -> None:
        c, _ = TrainingClass.get(class_id)

        if not c:
            raise ValueError("Class unavailable")

        try:
            db.execute_query(
                'INSERT INTO public."ClientTrainingClassMap" ("training_class", "client") VALUES (%s, %s)',
                (class_id, self.id),
            )
        except Exception:
            raise ValueError("Already enrolled in the class")
        
    def get_exercise_logs(self):
        # Fetch logs specific to the current user (self.client_id)
        query = 'SELECT * FROM public."ExerciseLog" WHERE client = %s;'  # Query with placeholder
        logs = db.fetch_query(query, (self.id,))  # Pass parameters as tuple
        return logs 
        
    def process_user_achievements(self):
        # Fetch logs for the current user
        logs = self.get_exercise_logs()
        
        # Fetch exercises with their total reps for the current user
        total_reps_by_exercise = {}
        for log in logs:
            # Fetch associated exercises and reps from logExerciseMap using the log's id
            query = f'SELECT exercise, SUM(reps) as total_reps FROM public."LogExerciseMap" WHERE log = {log["id"]} GROUP BY exercise;'
            exercises = db.fetch_query(query)
            for exercise in exercises:
                exercise_id = exercise["exercise"]
                total_reps = exercise["total_reps"]
                if exercise_id not in total_reps_by_exercise:
                    total_reps_by_exercise[exercise_id] = 0
                total_reps_by_exercise[exercise_id] += total_reps

        # Fetch all achievements
        achievements = db.fetch_query('SELECT * FROM public."Achievement";')
        
        # Map achievements for the user
        for achievement in achievements:
            achievement_id = achievement["id"]
            exercise_id = achievement["exercise"]
            required_reps = achievement["reps"]
            achievement_points = achievement["points"]  # Get points for the achievement
            
            # Check if the user qualifies for the achievement
            if (
                exercise_id in total_reps_by_exercise
                and total_reps_by_exercise[exercise_id] >= required_reps
            ):
                # Check if the client already has this achievement
                query = f'SELECT * FROM public."ClientAchievementMap" WHERE client = {self.id} AND achievement = {achievement_id};'
                existing_mapping = db.fetch_query(query)
                
                # Add achievement if not already present
                if not existing_mapping:
                    insert_query = f'INSERT INTO public."ClientAchievementMap" (client, achievement) VALUES ({self.id}, {achievement_id});'
                    db.execute_query(insert_query)
                    update_points_query = f'UPDATE public."Client" SET points = points + {achievement_points} WHERE id = {self.id};'
                    db.execute_query(update_points_query)
    
    def get_user_achievements(self):
        # Query to fetch all achievement details achieved by the user
        query = f'''
            SELECT *
            FROM public."ClientAchievementMap"
            JOIN public."Achievement" 
            ON public."ClientAchievementMap".achievement = public."Achievement".id
            WHERE public."ClientAchievementMap".client = {self.id};
        '''
        achievements = db.fetch_query(query)
        return achievements



    def __str__(self):
        return f"Client(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email}, points={self.points})"
