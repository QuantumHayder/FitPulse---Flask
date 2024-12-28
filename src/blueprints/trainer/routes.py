from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    render_template,
    Response,
)
from flask_login import login_required, current_user
from flask_htmx import HTMX

import os
import matplotlib.pyplot as plt
from io import BytesIO
from flask import send_file, current_app

from src.models.exercise import Exercise
from src.models.base_user import UserRole
from src.models.workout_plan import WorkoutPlan
from src.models.training_class import TrainingClass
from src.models.workout_request import WorkoutRequest

trainer_bp = Blueprint("trainer", __name__)
htmx = HTMX(trainer_bp)


@trainer_bp.route("/create-training-class", methods=["GET", "POST"])
@login_required
def create_class():
    if current_user.role != UserRole.Trainer:
        return Response("Bad Request", 400)

    if request.method == "POST":
        title = request.form.get("title")
        description = request.form.get("description")
        date = request.form.get("date")
        time = request.form.get("time")
        duration = request.form.get("duration")
        cost = request.form.get("cost")

        if not all((title, description, date, time, duration, cost)):
            return '<div class="text-red-500">All fields are required!</div>', 200

        TrainingClass.insert(
            TrainingClass(
                current_user.id, date, time, duration, title, description, cost
            )
        )

        success_message = (
            f"<div class='text-green-500'>Class {title} created successfully!</div>"
        )
        return success_message, 201
    return render_template("trainer/create-training-class.html")


@trainer_bp.route("/view-plan-requests", methods=["GET", "POST"])
@login_required
def view_plan_requests():
    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    pending_requests = current_user.get_pending_requests_by_trainer()

    return render_template(
        "trainer/view-plan-requests.html",
        clients_request=pending_requests,
        exercises=Exercise.get_all(),
    )


@trainer_bp.route("/view-old-plan-requests", methods=["GET", "POST"])
@login_required
def view_old_plan_requests():
    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    all_requests = WorkoutRequest.get_requests_by_trainer(current_user.id)
    return render_template(
        "trainer/view-old-plan-requests.html", all_requests=all_requests
    )


@trainer_bp.route(
    "/accept-plan-request/<int:workout_request_id>/<int:client_id>", methods=["POST"]
)
@login_required
def accept_plan_request(workout_request_id, client_id):
    if not htmx:
        return Response("Bad Request", status=201)

    plan_request = WorkoutRequest.get(workout_request_id)
    if plan_request is None:
        return

    title = request.form.get("title")
    description = request.form.get("description")
    exercises = request.form.getlist("exercises")

    if not all((title, description, exercises)):
        return render_template(
            "partials/workout-requests-table.html",
            clients_request=current_user.get_pending_requests_by_trainer(),
            message="All fields are required.",
        )

    current_user.accept_plan_request(workout_request_id)

    new_plan = WorkoutPlan(
        trainer=current_user.id,
        client=client_id,
        is_active=True,
        name=title,
        description=description,
    )
    new_plan.id = WorkoutPlan.insert(new_plan)

    for exercise in exercises:
        new_plan.add_exercise(exercise)

    pending_requests = current_user.get_pending_requests_by_trainer()

    return render_template(
        "partials/workout-requests-table.html",
        clients_request=pending_requests,
    )


@trainer_bp.route("/reject-plan-request/<int:workout_request_id>", methods=["POST"])
@login_required
def reject_plan_request(workout_request_id):
    if not htmx:
        return Response("Bad Request", status=201)

    plan_request = WorkoutRequest.get(workout_request_id)
    if plan_request is None:
        return

    current_user.reject_plan_request(workout_request_id)

    pending_requests = current_user.get_pending_requests_by_trainer()
    return render_template(
        "partials/workout-requests-table.html",
        clients_request=pending_requests,
    )


@trainer_bp.route("/profile")
@login_required
def profile():
    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))
    classes = TrainingClass.get_all_by_trainer(current_user.id)
    return render_template("trainer/profile.html", classes=classes)

@trainer_bp.route("/Dashboard")
@login_required
def Dashboard():
    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    class_count = current_user.count_my_classes()
    best_class = current_user.best_class()
    if best_class:
        best_class.student_count = best_class.student_count()

    worst_class = current_user.worst_class()
    if worst_class:
        worst_class.student_count = worst_class.student_count()

    request_counts = current_user.get_my_request_counts()  
    accepted = request_counts["Accepted"]
    rejected = request_counts["Rejected"]
    pending = request_counts["Pending"]

    client_count = current_user.count_my_clients()
    
    class_profit = current_user.profit_per_class()

    
    if class_profit:  
        fig, ax = plt.subplots(figsize=(10, 6))
        class_titles = [item[0] for item in class_profit]
        profits = [item[1] for item in class_profit]
        
        bar_width = 0.1
        ax.bar(class_titles, profits, color='skyblue' , width=bar_width)
        
        ax.set_xlabel('Class Title')
        ax.set_ylabel('Profit')
        ax.set_title('Profit per Class')
        plt.xticks(rotation=45, ha='right')

        static_folder = os.path.join(current_app.root_path, 'static')
        if not os.path.exists(static_folder):
            os.makedirs(static_folder)

        plot_image_path = os.path.join(static_folder, 'class_profit_plot.png')

        plt.tight_layout()
        plt.savefig(plot_image_path)

        plt.close(fig)

    return render_template("trainer/dashboard.html",
                           class_count=class_count,
                           best_class=best_class,
                           worst_class=worst_class,
                           accepted=accepted,
                           rejected=rejected,
                           pending=pending,
                           client_count=client_count,
                           class_profit=class_profit,
                           plot_image_path='class_profit_plot.png') 