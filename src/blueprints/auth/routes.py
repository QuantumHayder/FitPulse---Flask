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


auth_bp = Blueprint("auth", __name__)

login_manager = LoginManager()
login_manager.login_view = "auth.login"


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("base.home"))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        remember = True if request.form.get("remember") else False

        user = User.get_by_email(email)

        if user and check_password_hash(user._password, password):
            login_user(user, remember=remember)
            next_page = request.args.get("next")
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
        if user:
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

    User.update_user(current_user.id, first_name, last_name, email)

    flash("Profile updated successfully")
    return redirect(url_for("profile"))


@auth_bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")

    current_user_password = User.get_password(current_user.id)

    if check_password_hash(current_user_password, old_password):
        User.update_password(current_user.id, new_password)
        flash("Password updated successfully")
    else:
        flash("Current password is incorrect")

    return redirect(url_for("profile"))


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
