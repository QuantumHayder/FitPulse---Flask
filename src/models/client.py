from typing import Self
from datetime import datetime
from .base_user import BaseUser, UserRole
from .trainer_request import Status
from .friend_request import FriendRequest
from . import db


class Client(BaseUser):
    role: UserRole = UserRole.Client

    def __init__(self, email: str, first_name: str, last_name: str, *args, **kwargs):
        super().__init__(email, first_name, last_name, *args, **kwargs)

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


if __name__ == "__main__":
    c1 = Client.get(3)
    c2 = Client.get(10)
