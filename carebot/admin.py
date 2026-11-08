from functools import wraps
from flask import Blueprint, abort, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from . import db
from .models import Appointment, Doctor, Symptom, Condition, ConditionSymptom

bp = Blueprint("admin", __name__, url_prefix="/admin")

def admin_required(fn):
    @wraps(fn)
    @login_required
    def wrapper(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return fn(*args, **kwargs)
    return wrapper

@bp.get("/")
@admin_required
def dashboard():
    return render_template(
        "admin.html",
        appointments=Appointment.query.order_by(Appointment.starts_at.desc()).limit(50).all(),
        doctors=Doctor.query.order_by(Doctor.display_name).all(),
        symptoms=Symptom.query.order_by(Symptom.name).all(),
        conditions=Condition.query.order_by(Condition.name).all(),
    )

@bp.post("/appointments/<int:appointment_id>/cancel")
@admin_required
def cancel_appointment(appointment_id):
    appointment = db.get_or_404(Appointment, appointment_id)
    appointment.status = "cancelled"
    db.session.commit()
    flash("Appointment marked as cancelled.", "success")
    return redirect(url_for("admin.dashboard"))

@bp.post("/doctors")
@admin_required
def add_doctor():
    name = request.form.get("display_name", "").strip()
    specialty = request.form.get("specialty", "").strip()
    clinic = request.form.get("clinic_name", "").strip()
    location = request.form.get("location", "").strip()
    email = request.form.get("contact_email", "").strip() or None
    if not all([name, specialty, clinic, location]):
        flash("Complete all required provider fields.", "error")
    else:
        db.session.add(Doctor(display_name=name, specialty=specialty, clinic_name=clinic, location=location, contact_email=email))
        db.session.commit()
        flash("Provider added.", "success")
    return redirect(url_for("admin.dashboard"))

@bp.post("/symptoms")
@admin_required
def add_symptom():
    name = request.form.get("name", "").strip()
    if not name:
        flash("Enter a symptom name.", "error")
    elif Symptom.query.filter_by(name=name).first():
        flash("That symptom already exists.", "error")
    else:
        db.session.add(Symptom(name=name))
        db.session.commit()
        flash("Symptom added.", "success")
    return redirect(url_for("admin.dashboard"))
