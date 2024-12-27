from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    render_template,
    flash,
    Response,
)
from flask_login import login_required, current_user, logout_user, login_user
from flask_htmx import HTMX

from src.models.base_user import UserRole
from src.models.workout_request import WorkoutRequest
from src.models.workout_plan import WorkoutPlan
from src.models.training_class import TrainingClass
from src.models.trainer import Trainer
from src.models.exercise import Exercise
from src.models.client import Client

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

        if (
            not title
            or not description
            or not date
            or not time
            or not duration
            or not cost
        ):
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

    pending_requests=current_user.get_pending_requests_by_trainer()
    
    return render_template("trainer/view-plan-requests.html",clients_request = pending_requests , exercises=Exercise.get_all())






@trainer_bp.route("/view-old-plan-requests", methods=["GET", "POST"])
@login_required
def view_old_plan_requests():
    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    all_requests=WorkoutRequest.get_requests_by_trainer(current_user.id)
    return render_template("trainer/view-old-plan-requests.html", all_requests=all_requests)



@trainer_bp.route("/accept-plan-request/<int:plan_id>/", methods=["POST"])
@login_required
def accept_plan_request(plan_id):
    if not htmx:
        return Response("Bad Request", status=201)

    plan = WorkoutRequest.get(plan_id)
    if plan is None:
        return

    current_user.accept_plan_request(plan_id)
    return render_template(
        "trainer/accept_plan_requests.html",
        accepted=True,
        exercises=Exercise.get_all()

    )


@trainer_bp.route("/reject-plan-request/<int:plan_id>", methods=["POST"])
@login_required
def reject_plan_request(plan_id):
    if not htmx:
        return Response("Bad Request", status=201)

    plan = WorkoutRequest.get(plan_id)
    if plan is None:
        return

    current_user.reject_plan_request(plan_id)
    return render_template(
        "trainer/accept_plan_requests.html",
        accepted=False,
    )


@trainer_bp.route("/profile")
@login_required
def profile():
    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))
    trainer_info = Trainer.get(current_user.id)
    return render_template("trainer/profile.html", trainer_info=trainer_info)

@trainer_bp.route("/create-workout", methods=["POST"])
def create_workout():
    trainer=current_user.id
    


    