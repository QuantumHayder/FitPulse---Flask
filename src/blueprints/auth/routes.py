import re
from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import (
    current_user,
    login_user,
    LoginManager,
    login_required,
    logout_user,
)
from werkzeug.security import check_password_hash

from src.models.user import User
from src.models.admin import Admin
from src.models.client import Client
from src.models.trainer import Trainer
from src.models.base_user import UserRole


auth_bp = Blueprint("auth", __name__)

login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    user_id, user_type = user_id.split("-")

    try:
        user_id = int(user_id)
    except ValueError:
        return None

    match user_type:
        case UserRole.User:
            return User.get(user_id)
        case UserRole.Client:
            return Client.get(user_id)
        case UserRole.Trainer:
            return Trainer.get(user_id)
        case UserRole.Admin:
            return Admin.get(user_id)
        case _:
            return None


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("base.home"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False

        user = User.get_by_email(email)
        client = Client.get_by_email(email)
        admin = Admin.get_by_email(email)
        trainer = Trainer.get_by_email(email)

        if not any((user, client, admin, trainer)):
            flash("Invalid email or password")
            return redirect(url_for("auth.login"))

        valid_user = None

        if user and check_password_hash(user._password, password):
            valid_user = user
        elif client and check_password_hash(client._password, password):
            valid_user = client
        elif trainer and check_password_hash(trainer._password, password):
            valid_user = trainer
        elif admin and check_password_hash(admin._password, password):
            valid_user = admin

        if valid_user is not None:
            login_user(valid_user, remember=remember)
            next_page = request.args.get("next")
            if current_user.role == UserRole.Client:
                return redirect(next_page or url_for("client.dashboard"))
            return redirect(next_page or url_for("base.home"))

        flash("Invalid email or password")
        return redirect(url_for("auth.login"))

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("base.home"))

    if request.method == "POST":

        form_data = {
            "email": request.form.get("email"),
            "first_name": request.form.get("first_name"),
            "last_name": request.form.get("last_name"),
            "password": request.form.get("password"),
        }

        email = form_data["email"]
        first_name = form_data["first_name"]
        last_name = form_data["last_name"]
        password = form_data["password"]

        error = validate_password(password)
        if error:
            flash(error)
            return render_template("auth/register.html", **form_data)

        user = User.get_by_email(email=email)

        admin = Admin.get_by_email(email=email)
        trainer = Trainer.get_by_email(email=email)
        client = Client.get_by_email(email=email)

        if any((user, admin, trainer, client)):
            flash("Email address already exists")
            return render_template("auth/register.html", **form_data)

        new_user = User(email=email, first_name=first_name, last_name=last_name)
        new_user.set_password(password)

        User.insert(new_user)

        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    if request.method == "GET":
        return render_template("auth/logout.html")
    logout_user()
    return redirect(url_for("base.home"))


@auth_bp.route("/update-profile", methods=["POST"])
@login_required
def update_profile():
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    email = request.form.get("email")

    if not any((first_name, last_name, email)):
        return f"<div class='text-red-500'>Can't leave everthing empty.</div>", 200

    if email:
        u = User.get_by_email(email)
        a = Admin.get_by_email(email)
        t = Trainer.get_by_email(email)
        c = Client.get_by_email(email)

        if any((u, a, t, c)):
            return f"<div class='text-red-500'>Email already taken.</div>", 200

    current_user.update(current_user.id, first_name, last_name, email)

    success_message = (
        f"<div class='text-green-500'>Information updated successfully!</div>"
    )
    return success_message, 200


@auth_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")

    current_user_password = current_user.get_password(current_user.id)

    invalid = validate_password(new_password)
    if invalid:
        return f'<div class="text-red-500">{invalid}</div>'

    if check_password_hash(current_user_password, current_password):
        current_user.update_password(current_user.id, new_password)
        return '<div class="text-green-500">Password updated successfully</div>'

    return '<div class="text-red-500">Current password is incorrect</div>'


def validate_password(password):
    """
    Validates if a password meets the criteria:
    - At least 8 characters long
    - Contains at least one letter
    - Contains at least one number
    - Contains at least one special symbol
    """
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Za-z]", password):
        return "Password must contain at least one letter."
    if not re.search(r"\d", password):
        return "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return "Password must contain at least one special symbol."

    return ""
