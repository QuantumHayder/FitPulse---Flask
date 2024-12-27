from typing import Self
from datetime import datetime
from .base_user import BaseUser, UserRole
from .trainer_request import Status
from .friend_request import FriendRequest


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

    def __str__(self):
        return f"Client(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email}, points={self.points})"
