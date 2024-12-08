from flask import Blueprint, request, redirect, url_for, render_template, flash
from flask_login import login_required

base_bp = Blueprint("base", __name__)


@base_bp.route("/")
def home():
    return render_template("home.html")


@base_bp.route("/workouts")
def workouts():
    return render_template("workouts.html")


@base_bp.route("/nutrition")
def nutrition():
    return render_template("nutrition.html")


@base_bp.route("/community")
def community():
    return render_template("community.html")


@base_bp.route("/settings")
def settings():
    return render_template("settings.html")
