from datetime import datetime
from typing import Self, Optional

from .trainer_request import Status
from . import db


class FriendRequest:
    def __init__(
        self,
        receiver: int,
        sender: int,
        status: Status,
        timestamp: Optional[datetime.date] = datetime.now(),
        *args,
        **kwargs,
    ) -> None:
        self.sender = sender
        self.receiver = receiver
        self.timestamp = timestamp
        self.status = status

    def update_status(self, new_status: Status):
        if self.status == new_status:
            return

        db.execute_query(
            'UPDATE public."FriendRequest" SET status = %s WHERE "receiver" = %s AND sender = %s;',
            (new_status, self.receiver, self.sender),
        )

    @classmethod
    def get(cls, sender: int, receiver: int):
        requests = db.fetch_query(
            'SELECT * FROM public."FriendRequest" WHERE "receiver" = %s AND "sender" = %s ',
            (receiver, sender),
        )

        if not requests:
            return None

        return cls(**requests[0])

    @classmethod
    def get_all_sent(cls, sender: int):
        requests = db.fetch_query(
            'SELECT * FROM public."FriendRequest" WHERE "sender" = %s',
            (sender,),
        )

        return [FriendRequest(**request) for request in requests]

    @classmethod
    def get_all_received(cls, received: int):
        requests = db.fetch_query(
            'SELECT * FROM public."FriendRequest" WHERE "receiver" = %s',
            (received,),
        )
        return [FriendRequest(**request) for request in requests]

    @classmethod
    def insert(cls, friend_request: Self) -> None:
        if friend_request.sender is None:
            raise ValueError("Cannot insert friend request with sender set to NULL.")
        if friend_request.receiver is None:
            raise ValueError("Cannot insert friend request with receiver set to NULL.")

        db.execute_query(
            'INSERT INTO public."FriendRequest" ("receiver", "sender", "timestamp") VALUES (%s, %s, %s)',
            (
                friend_request.receiver,
                friend_request.sender,
                friend_request.timestamp or datetime.now(),
            ),
        )

    @classmethod
    def delete(cls, sender: int, receiver: int) -> None:
        db.execute_query(
            'DELETE FROM public."FriendRequest" WHERE sender = %s AND receiver = %s;',
            (sender, receiver),
        )

    def __str__(self):
        return f"FriendRquest(sender={self.sender}, receiver={self.receiver}, status={self.status})"
