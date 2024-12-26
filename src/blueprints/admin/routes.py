from flask import (
    Blueprint,
    request,
    Response,
    redirect,
    url_for,
    render_template,
    flash,
)
from flask_login import login_required, current_user
from flask_htmx import HTMX


from src.blueprints.auth.routes import validate_password
from src.models.base_user import UserRole
from src.models.user import User
from src.models.admin import Admin
from src.models.trainer import Trainer
from src.models.food import Food
from src.models.trainer_request import TrainerRequest, Status

admin_bp = Blueprint("admin", __name__)
htmx = HTMX(admin_bp)


@admin_bp.route("/hire-trainer")
@login_required
def handle_trainer_request():
    if current_user.role != UserRole.Admin:
        return Response("Bad Request", 400)

    trainer_requests = TrainerRequest.get_all()

    accepted_requests = list(
        filter(lambda r: r[0].status == Status.Accepted, trainer_requests)
    )

    pending_requests = list(
        filter(lambda r: r[0].status == Status.Pending, trainer_requests)
    )

    return render_template(
        "admin/hire_trainer.html",
        trainer_requests=trainer_requests,
        accepted_requests=accepted_requests,
        pending_requests=pending_requests,
    )


@admin_bp.route("/accept-trainer-request/<int:request_id>", methods=["POST"])
@login_required
def accept_trainer_request(request_id):
    if current_user.role != UserRole.Admin:
        return Response("Bad Request", 400)

    r = TrainerRequest.get(request_id)

    if r is not None:
        r.accept_request()

    user = User.get(r.user)
    Trainer.insert(
        Trainer(user.email, user.first_name, user.last_name, password=user._password)
    )
    User.delete(user.id)

    trainer_requests = TrainerRequest.get_all()

    accepted_requests = list(
        filter(lambda r: r[0].status == Status.Accepted, trainer_requests)
    )

    pending_requests = list(
        filter(lambda r: r[0].status == Status.Pending, trainer_requests)
    )

    return render_template(
        "admin/admin_trainer_request.html",
        trainer_requests=trainer_requests,
        accepted_requests=accepted_requests,
        pending_requests=pending_requests,
    )


@admin_bp.route("/reject-trainer-request/<int:request_id>", methods=["POST"])
@login_required
def reject_trainer_request(request_id):
    if current_user.role != UserRole.Admin:
        return Response("Bad Request", 400)

    r = TrainerRequest.get(request_id)

    if r is not None:
        r.reject_request()

    trainer_requests = TrainerRequest.get_all()

    accepted_requests = list(
        filter(lambda r: r[0].status == Status.Accepted, trainer_requests)
    )

    pending_requests = list(
        filter(lambda r: r[0].status == Status.Pending, trainer_requests)
    )

    return render_template(
        "admin/admin_trainer_request.html",
        trainer_requests=trainer_requests,
        accepted_requests=accepted_requests,
        pending_requests=pending_requests,
    )


@admin_bp.route("/create-nutrition", methods=["GET", "POST"])
@login_required
def create_nutrition():
    if current_user.role != UserRole.Admin:
        return Response("Bad Request", 400)

    if request.method == "GET":
        return render_template("admin/create_nutrition.html")

    food = request.form.get("food")
    carbs = request.form.get("carbs")
    proteins = request.form.get("proteins")
    calories = request.form.get("calories")
    fats = request.form.get("fats")

    try:
        carbs = float(carbs)
        proteins = float(proteins)
        calories = float(calories)
        fats = float(fats)
    except ValueError:
        return (
            '<div class="text-red-500">carbs, Proteins, Calories and Fats Fields should be floats</div>',
            200,
        )

    Food.insert(Food(food, calories, carbs, proteins, fats))

    return f"<div class='text-green-500'>{food} created successfully!</div>", 201


@admin_bp.route("/create-admin", methods=["GET", "POST"])
@login_required
def create_admin():
    if current_user.role != UserRole.Admin:
        return Response("Bad Request", 400)

    if request.method == "GET":
        return render_template("admin/create_admin.html")

    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")

    if not first_name or not last_name or not email or not password:
        return '<div class="text-red-500">All fields are required!</div>', 200

    if password != confirm_password:
        return '<div class="text-red-500">Passwords do not match!</div>', 200

    invalid = validate_password(password)

    if invalid:
        return f'<div class="text-red-500">{invalid}</div>'

    a = Admin(email, first_name, last_name)
    a.set_password(password)
    Admin.insert(a)

    success_message = f"<div class='text-green-500'>Admin {first_name} {last_name} created successfully!</div>"
    return success_message, 201


@admin_bp.route("/manage-promotion", methods=["GET", "POST"])
@login_required
def manage_promotion():
    if current_user.role != UserRole.Admin:
        return Response("Bad Request", 400)
    return render_template("admin/manage_promotion.html")


@admin_bp.route("/admin-dashboard", methods=["GET"])
@login_required
def dashboard():
    if current_user.role != UserRole.Admin:
        return Response("Bad Request", 400)
    return render_template("admin/dashboard.html")
