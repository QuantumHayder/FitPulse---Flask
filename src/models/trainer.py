from .base_user import BaseUser, UserRole
from .trainer_request import Status
import src.models.workout_request as workout_request

from datetime import date, datetime


class Trainer(BaseUser):
    role: UserRole = UserRole.Trainer

    def __init__(self, email: str, first_name: str, last_name: str, *args, **kwargs):
        super().__init__(email, first_name, last_name, *args, **kwargs)

    def get_pending_requests_by_trainer(self):
        requests = [
            r
            for r in workout_request.WorkoutRequest.get_requests_by_trainer(self.id)
            if r.status == Status.Pending
        ]
        return requests

    def reject_plan_request(self, plan_id: int) -> None:
        if request := workout_request.WorkoutRequest.get(plan_id):
            request.update_status(Status.Rejected)

    def accept_plan_request(self, plan_id: int) -> None:
        if request := workout_request.WorkoutRequest.get(plan_id):
            request.update_status(Status.Accepted)
