from datetime import datetime
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

from src.models.client import Client
from src.models.base_user import UserRole
from src.models.user import User
from src.models.exercise import Exercise
from src.models.food import Food
from src.models.exercise_enums import ExerciseType, Level, Equipment, BodyPart
from src.models.trainer_request import TrainerRequest
from src.models.trainer import Trainer

base_bp = Blueprint("base", __name__)
htmx = HTMX(base_bp)


@base_bp.route("/client-request", methods=["POST"])
@login_required
def client_request():
    if current_user.role != UserRole.User:
        return Response("Bad Request", 400)

    c = Client(
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        password=current_user._password,
    )
    Client.insert(c)
    User.delete(current_user.id)
    logout_user()
    c = Client.get_by_email(c.email)
    login_user(c)
    return redirect(url_for("client.dashboard"))


@base_bp.route("/trainer-request", methods=["POST", "GET"])
@login_required
def trainer_request():
    if current_user.role != UserRole.User:
        return Response("Bad Request", 400)

    if request.method == "POST" and htmx:

        description = request.form.get("description")
        linked_in = request.form.get("linkedin_url")

        TrainerRequest.insert(
            TrainerRequest(current_user.id, datetime.now(), description, linked_in)
        )

        return render_template(
            "trainer/trainer_requests.html",
            trainer_requests=TrainerRequest.get_by_user(current_user.id),
        )

    return render_template(
        "trainer/trainer_onboarding.html",
        trainer_requests=TrainerRequest.get_by_user(current_user.id),
    )


@base_bp.route("/")
def home():
    if current_user.is_authenticated:
        if current_user.role == UserRole.User:
            return redirect(url_for("base.onboarding"))
        if current_user.role == UserRole.Admin:
            return redirect(url_for("admin.dashboard"))
        if current_user.role == UserRole.Client:
            return redirect(url_for("client.dashboard"))
        if current_user.role == UserRole.Trainer:
            return redirect(url_for("trainer.profile"))
    return render_template("home.html")


@base_bp.route("/onboarding")
@login_required
def onboarding():
    if current_user.role != UserRole.User:
        return redirect(url_for("base.home"))

    return render_template("onboarding.html")


@base_bp.route("/exercises", methods=["GET"])
@login_required
def exercises():
    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    return render_template(
        "exercises.html",
        levels=Level,
        exercise_types=ExerciseType,
        body_parts=BodyPart,
        equipment_types=Equipment,
    )


@base_bp.route("/exercise-search")
@login_required
def exercise_search():
    if not htmx:
        return Response("Bad Request", status=201)

    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    title = request.args.get("title")
    exercise_type = request.args.get("type")
    body_part = request.args.get("body_part")
    equipment = request.args.get("equipment")
    level = request.args.get("level")

    exercises = Exercise.search(title, exercise_type, body_part, equipment, level)

    return render_template("partials/exercise_table.html", exercises=exercises)


@base_bp.route("/exercises/<int:exercise_id>")
@login_required
def show_exercise(exercise_id):

    if not htmx:
        return Response("Bad Request", status=201)

    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    exercise = Exercise.get(exercise_id)

    if exercise is None:
        return Response("Bad Request", status=201)

    return render_template("partials/show_exercise.html", exercise=exercise)


@base_bp.route("/nutrition")
@login_required
def nutrition():
    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))
    return render_template("nutrition.html")


@base_bp.route("/nutrition-search")
@login_required
def nutrition_search():
    if not htmx:
        return Response("Bad Request", status=201)

    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    name = request.args.get("food")
    food = Food.search(name=name)

    return render_template("partials/nutrition_table.html", food=food)


@base_bp.route("/community")
@login_required
def community():
    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    return render_template("community.html", trainers=Trainer.get_all())


@base_bp.route("/settings")
@login_required
def settings():
    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))
    return render_template("settings.html")
