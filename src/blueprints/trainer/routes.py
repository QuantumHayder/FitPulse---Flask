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

trainer_bp = Blueprint("trainer", __name__)
htmx = HTMX(trainer_bp)

@trainer_bp.route("/create-training-class", methods=["GET"])
@login_required
def create_class():
    if current_user.role != UserRole.Trainer:
        return Response("Bad Request", 400)
    return render_template("trainer/create-training-class.html")