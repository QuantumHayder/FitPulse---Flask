from typing import Self
from datetime import datetime
from .base_user import BaseUser, UserRole
from .trainer_request import Status
from .friend_request import FriendRequest

from src.models import db

from .training_class import TrainingClass
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
            return None, None  # Return None if no clients are found
        
        # Create a dictionary to store the number of friends for each client
        friends_count = {}

        for client in clients:
            # Get the list of friends for each client
            friends = client.get_friends()
            friends_count[client] = len(friends)

        # Find the client with the most friends
        top_client = max(friends_count, key=friends_count.get, default=None)
        
        # Find the client with the fewest friends
        bottom_client = min(friends_count, key=friends_count.get, default=None)

        # Return the top and bottom clients along with their friend counts
        return (top_client, friends_count[top_client]) if top_client else None, \
            (bottom_client, friends_count[bottom_client]) if bottom_client else None


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

        # Check if a friend request doesn't already exist
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
            raise ValueError("Already enrolled in the course")

    def __str__(self):
        return f"Client(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email}, points={self.points})"
