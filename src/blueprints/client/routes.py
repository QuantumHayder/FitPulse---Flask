from flask import Blueprint, request, Response, redirect, url_for, render_template
from flask_login import login_required, current_user
from flask_htmx import HTMX

from src.models.training_class import TrainingClass
from src.models.user import User
from src.models.base_user import UserRole

client_bp = Blueprint("client", __name__)
htmx = HTMX(client_bp)


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
    return render_template("dashboard.html")
