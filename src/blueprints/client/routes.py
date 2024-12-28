from flask import Blueprint, request, Response, redirect, url_for, render_template
from flask_login import login_required, current_user
from flask_htmx import HTMX
from flask import jsonify

from src.models.training_class import TrainingClass
from src.models.workout_request import WorkoutRequest
from src.models.client import Client
from src.models.trainer import Trainer
from src.models.food_log import FoodLog
from src.models.base_user import UserRole
from src.models.exercise_log import ExerciseLog
from src.models.exercise import Exercise
from src.models.trainer_request import Status
from src.models.workout_plan import WorkoutPlan

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

    context = {"friend_requests": current_user.get_pending_requests_received()}

    if request.method == "GET" and htmx:
        email = request.args.get("search")
        other = Client.get_by_email(email)
        if other:
            try:
                current_user.send_friend_request(other)
                message = {
                    "message": f"Request sent to {other.first_name} {other.last_name}",
                    "error": False,
                }
            except Exception as e:
                message = {
                    "message": f"{e}",
                    "error": True,
                }
        else:
            message = {
                "message": "This person does not exist.",
                "error": True,
            }

        return render_template("partials/friend_search.html", message=message)

    return render_template("client/friends.html", **context)


@client_bp.route("/request-workout-plan")
@login_required
def workout_plan():
    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    clients_requests = WorkoutRequest.get_requests_by_client(current_user.id)

    return render_template(
        "client/request-workout-plan.html",
        trainers=Trainer.get_all(),
        clients_request=clients_requests,
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

    if not trainer or not description:
        message = {"message": "All fields are required!", "error": True}
        return render_template(
            "partials/workout_plan_request.html",
            message=message,
            clients_request=WorkoutRequest.get_requests_by_client(current_user.id),
        )

    WorkoutRequest.insert(
        WorkoutRequest(
            current_user.id, datetime.now(), trainer, description, status=Status.Pending
        )
    )

    message = {"message": "Workout Request sent successfully!", "error": False}
    return render_template(
        "partials/workout_plan_request.html",
        message=message,
        clients_request=WorkoutRequest.get_requests_by_client(current_user.id),
    )


@client_bp.route("/dashboard")
@login_required
def dashboard():
    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    enrolled_classes = current_user.enrolled_classes()
    context = {
        "friend_requests": current_user.get_pending_requests_received(),
        "enrolled_classes": enrolled_classes,
        "exercises": Exercise.get_all(),
    }
    return render_template("client/dashboard.html", **context)


@client_bp.route("/goals", methods=["GET", "POST"])
@login_required
def goals():
    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    # Process and fetch user achievements
    current_user.process_user_achievements()  # This will update achievements based on the logs
    user_achievements = (
        current_user.get_user_achievements()
    )  # Fetch achievements for the current user

    if request.method == "GET":
        # Pass achievements and logs to the template
        return render_template("client/goals.html", achievements=user_achievements)

    # Handle POST request for updating calories
    calories = request.form.get("calories")
    if not calories:
        return '<div class="text-red-500 text-center my-1">Enter calories!</div>', 200

    current_user.update_calories(calories)

    return (
        '<div class="text-green-500 text-center my-1">Updated goal successfully</div>',
        200,
    )


@client_bp.route("/enroll_class/<int:class_id>")
@login_required
def enroll_class(class_id):

    training_class, _ = TrainingClass.get(class_id)

    if training_class.cost <= current_user.points:
        promotion = training_class.get_current_promotion()
        if promotion:
            current_user.update_points(
                max(current_user.points - (training_class.cost - promotion), 0)
            )
        else:
            current_user.update_points(
                max(current_user.points - training_class.cost, 0)
            )

        try:
            current_user.enroll_in_class(class_id)
            message = {"message": "Enrolled Successfully.", "error": False}
        except Exception as e:
            message = {"message": f"{e}", "error": True}
    else:
        message = {"message": "Could not enroll in class", "error": True}

    return render_template(
        "partials/class_enroll.html", message=message, training_class=training_class
    )


@client_bp.route("/logs")
@login_required
def logs():
    if current_user.role == UserRole.User:
        return redirect(url_for("base.onboarding"))

    user_logs = ExerciseLog.get_all(current_user.id)

    user_logs.sort(key=lambda ex: ex.timestamp, reverse=True)

    return render_template(
        "client/logs.html", user_logs=user_logs, exercises=Exercise.get_all()
    )


@client_bp.route("/update-log-reps/<int:log_id>/<int:exercise_id>", methods=["POST"])
@login_required
def update_log_reps(log_id, exercise_id):
    reps = request.form.get("reps")
    log, _ = ExerciseLog.get(log_id)
    log.update_exercise(exercise_id, reps)


@client_bp.route("/add-log-exercise/<int:log_id>", methods=["POST"])
@login_required
def add_log_exercise(log_id):
    exercise_id = request.form.get("exercise")
    try:
        log, _ = ExerciseLog.get(log_id)
        log.insert_exercise(exercise_id, 0)
        message = {"message": "", "error": False}
    except Exception as e:
        message = {
            "message": "Make sure to pick an exercise not in the log.",
            "error": True,
        }

    return render_template(
        "components/log_exercises_table.html", log=log, message=message
    )


@client_bp.route(
    "/delete-log-exercise/<int:log_id>/<int:exercise_id>", methods=["POST"]
)
@login_required
def delete_log_exercise(log_id, exercise_id):
    log, _ = ExerciseLog.get(log_id)
    log.delete_exercise(exercise_id)
    return render_template("components/log_exercises_table.html", log=log)


@client_bp.route("/delete-exercise-log/<int:log_id>", methods=["POST"])
@login_required
def delete_exercise_log(log_id):
    ExerciseLog.delete(log_id)
    user_logs = ExerciseLog.get_all(current_user.id)
    user_logs.sort(key=lambda ex: ex.timestamp, reverse=True)
    return render_template(
        "components/exercise_log_list.html",
        user_logs=user_logs,
        exercises=Exercise.get_all(),
    )


@client_bp.route("/add-exercise-log", methods=["POST"])
@login_required
def add_exercise_log():
    e = ExerciseLog(current_user.id, datetime.now())
    ExerciseLog.insert(e)
    user_logs = ExerciseLog.get_all(current_user.id)
    user_logs.sort(key=lambda ex: ex.timestamp, reverse=True)
    return render_template(
        "components/exercise_log_list.html",
        user_logs=user_logs,
        exercises=Exercise.get_all(),
    )


@client_bp.route("/foodLog")
@login_required
def food_log():
    if current_user.role != UserRole.Client:
        return redirect(url_for("base.onboarding"))
    logs = FoodLog.get_all(current_user.id)
    logs.sort(key=lambda l: l.timestamp, reverse=True)
    return render_template("client/foodLog.html", logs=logs)


@client_bp.route("/trainer/<int:trainer_id>")
@login_required
def trainer_page(trainer_id):
    t = Trainer.get(trainer_id)
    classes = TrainingClass.get_all_by_trainer(t.id)
    return render_template("trainer/trainer_profile.html", trainer=t, classes=classes)


@client_bp.route("/get_exercise_data/<int:exercise_id>")
@login_required
def get_exercise_data(exercise_id: int):
    labels, values, exercise = current_user.get_exercise_graph(exercise_id)
    result = {"labels": labels, "values": values, "exercise": exercise.title.title()}
    return jsonify(result)


@client_bp.route("/workout_plans")
@login_required
def workout_plans():
    workout_plans = WorkoutPlan.get_client_workouts(current_user.id)
    workout_plans.sort(key=lambda c: not c.is_active)
    return render_template("client/workout_plans.html", workout_plans=workout_plans)


@client_bp.route("/toggle-workout-plan-active/<int:plan_id>", methods=["POST"])
def toggle_workout_plan_active(plan_id):
    WorkoutPlan.toggle_active(plan_id)
    return render_template(
        "partials/workout_plan_active_button.html",
        workout_plan=WorkoutPlan.get(plan_id),
    )
