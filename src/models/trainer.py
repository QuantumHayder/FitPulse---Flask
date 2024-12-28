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
            
    def count_my_classes(self):
        from .training_class import TrainingClass
        classes = TrainingClass.get_all_by_trainer(self.id)
        return len(classes)

    def best_class(self):
        from .training_class import TrainingClass
        classes = TrainingClass.get_all_by_trainer(self.id)
        
        max_count = 0
        best_class = None

        for training_class in classes:
            count = training_class.student_count()  
            if count > max_count:
                max_count = count
                best_class = training_class

        return best_class
    
    def worst_class(self):
        from .training_class import TrainingClass
        classes = TrainingClass.get_all_by_trainer(self.id)
        
        least_count = 1000
        worst_class = None

        for training_class in classes:
            count = training_class.student_count()  
            if count < least_count:
                least_count = count
                worst_class = training_class

        return worst_class
    
    def get_my_request_counts(self):
        from .workout_request import WorkoutRequest
        requests = WorkoutRequest.get_requests_by_trainer(self.id)

        
        accepted_count = sum(1 for request in requests if request.status == "Accepted")
        rejected_count = sum(1 for request in requests if request.status == "Rejected")
        pending_count = sum(1 for request in requests if request.status == "Pending")

        return {
            "Accepted": accepted_count,
            "Rejected": rejected_count,
            "Pending": pending_count,
        }
        
    def count_my_clients(self):
        from .training_class import TrainingClass
        classes = TrainingClass.get_all_by_trainer(self.id)
        if not classes:  
            return 0 
        count=0
        for training_class in classes:
            count += training_class.student_count()  
        return count
    
    def profit_per_class(self):
        from .training_class import TrainingClass
        classes = TrainingClass.get_all_by_trainer(self.id)
        if not classes:  
            return None
        class_profit = []
        for training_class in classes:
            count = training_class.student_count()  
            profit = count * training_class.cost    
            class_profit.append((training_class.title, profit))
            
        class_profit.sort(key=lambda x: x[1], reverse=True)  # Sort by the second element (profit)
        return class_profit


