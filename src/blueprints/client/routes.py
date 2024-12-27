from flask import Blueprint, request, Response, redirect, url_for, render_template
from flask_login import login_required, current_user
from flask_htmx import HTMX

from src.models.training_class import TrainingClass
from src.models.workout_request import WorkoutRequest
from src.models.client import Client
from src.models.trainer import Trainer
from src.models.base_user import UserRole
from src.models.exercise_log import ExerciseLog

from datetime import date, datetime

client_bp = Blueprint("client", __name__)
htmx = HTMX(client_bp)


@client_bp.route("/accept-friend-request/<int:client_id>/", methods=["POST"])
@login_required
def accept_friend_request(client_id):
    if not htmx:
        return Response("Bad Request", status=201)

    sender = Client.get(client_id)

    if sender is None:
        return

    current_user.accept_friend_request(sender)

    return render_template(
        "components/friend_request_section.html",
        friend_requests=current_user.get_pending_requests_received(),
    )


@client_bp.route("/reject-friend-request/<int:client_id>/", methods=["POST"])
@login_required
def reject_friend_request(client_id):
    if not htmx:
        return Response("Bad Request", status=201)

    sender = Client.get(client_id)

    if sender is None:
        return

    current_user.reject_friend_request(sender)

    return render_template(
        "components/friend_request_section.html",
        friend_requests=current_user.get_pending_requests_received(),
    )


@client_bp.route("/training-class-search")
@login_required
def training_class_search():
    if not htmx:
        return Response("Bad Request", status=201)

    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    title = request.args.get("title")
    trainer_id = request.args.get("trainer")

    if not trainer_id:
        trainer_id = None

    training_classes = TrainingClass.search(title=title, trainer=trainer_id)
    

    return render_template(
        "partials/training_class_table.html", training_classes=training_classes
    )


@client_bp.route("/friends")
@login_required
def friends():
    if current_user.role != UserRole.Client:
        return Response("Bad Request", status=201)

    if request.method == "GET" and htmx:
        email = request.args.get("search")
        other = Client.get_by_email(email)
        if other:
            current_user.send_friend_request(other)
            return f"<div class='text-green-500'>Request sent to {other.first_name} {other.last_name}</div>"
        return f"<div class='text-red-500'>No user with the specified email.</div>"

    context = {"friend_requests": current_user.get_pending_requests_received()}
    return render_template("client/friends.html", **context)

@client_bp.route("/request-workout-plan")
@login_required
def workout_plan():
    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    clients_requests=WorkoutRequest.get_requests_by_client(current_user.id)

    return render_template(
        "request-workout-plan.html",trainers=Trainer.get_all() ,  clients_request = clients_requests
    )


@client_bp.route("/workout-plan-request")
@login_required
def workout_plan_request():
    if not htmx:
        return Response("Bad Request", status=201)

    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    trainer = request.args.get("trainer")
    description = request.args.get("description")
    
    if not description or not trainer:
            return '<div class="text-red-500">All fields are required!</div>', 200

    WorkoutRequest.insert(WorkoutRequest(current_user.id, datetime.now(), trainer , description))
   
    success_message = f"<div class='text-green-500'>Workout Request sent successfully!</div>"
    return success_message, 201




@client_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    context = {"friend_requests": current_user.get_pending_requests_received()}
    return render_template("client/dashboard.html", **context)


@client_bp.route("/goals")
@login_required
def goals():
    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    return render_template("client/goals.html")


@client_bp.route("/logs")
@login_required
def logs():
    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    user_logs = ExerciseLog.get_all(current_user.id)

    user_logs.sort(key=lambda ex: ex.timestamp, reverse=True)

    return render_template("client/logs.html", user_logs=user_logs)
