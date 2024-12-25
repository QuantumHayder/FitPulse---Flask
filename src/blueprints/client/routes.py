from flask import Blueprint, request, Response, redirect, url_for, render_template
from flask_login import login_required, current_user
from flask_htmx import HTMX

from src.models.training_class import TrainingClass
from src.models.client import Client
from src.models.base_user import UserRole

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
        "components/friend-request-section.html",
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
        "components/friend-request-section.html",
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


@client_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    context = {"friend_requests": current_user.get_pending_requests_received()}
    return render_template("dashboard.html", **context)
