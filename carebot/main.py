from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from . import db
from .models import Symptom, Assessment, AssessmentMatch, Doctor, Appointment
from .services import match_conditions

bp = Blueprint("main", __name__)

@bp.get("/")
def index():
    return render_template("index.html")

@bp.get("/dashboard")
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for("admin.dashboard"))
    appointments = Appointment.query.filter_by(user_id=current_user.id).order_by(Appointment.starts_at.desc()).limit(10).all()
    assessments = Assessment.query.filter_by(user_id=current_user.id).order_by(Assessment.created_at.desc()).limit(10).all()
    return render_template("dashboard.html", appointments=appointments, assessments=assessments)

@bp.route("/assessment", methods=["GET", "POST"])
@login_required
def assessment():
    symptoms = Symptom.query.filter_by(active=True).order_by(Symptom.name).all()
    if request.method == "POST":
        selected_ids = request.form.getlist("symptoms")
        free_text = request.form.get("other_symptoms", "").strip()
        selected = [s for s in symptoms if str(s.id) in selected_ids]
        names = [s.name for s in selected]
        if free_text:
            names.extend([x.strip() for x in free_text.split(",") if x.strip()])
        if not names:
            flash("Select at least one symptom or enter one in the text field.", "error")
            return render_template("assessment.html", symptoms=symptoms)
        assessment_record = Assessment(user_id=current_user.id, symptoms_text=", ".join(names))
        db.session.add(assessment_record)
        db.session.flush()
        matches = match_conditions(names)
        for condition, score in matches:
            db.session.add(AssessmentMatch(assessment_id=assessment_record.id, condition_id=condition.id, score=score))
        db.session.commit()
        return render_template("assessment_result.html", assessment=assessment_record, matches=matches, doctors=Doctor.query.filter_by(active=True).order_by(Doctor.specialty).all())
    return render_template("assessment.html", symptoms=symptoms)

@bp.route("/appointments/book", methods=["POST"])
@login_required
def book_appointment():
    doctor_id = request.form.get("doctor_id", type=int)
    date_text = request.form.get("date", "")
    time_text = request.form.get("time", "")
    reason = request.form.get("reason", "").strip()[:500]
    doctor = db.session.get(Doctor, doctor_id) if doctor_id else None
    if not doctor or not doctor.active:
        flash("Choose a valid provider.", "error")
        return redirect(url_for("main.dashboard"))
    try:
        starts_at = datetime.strptime(f"{date_text} {time_text}", "%Y-%m-%d %H:%M")
    except ValueError:
        flash("Enter a valid appointment date and time.", "error")
        return redirect(url_for("main.dashboard"))
    if starts_at <= datetime.now() or starts_at.minute not in (0, 30):
        flash("Choose a future time on the hour or half-hour.", "error")
        return redirect(url_for("main.dashboard"))
    appointment = Appointment(user_id=current_user.id, doctor_id=doctor.id, starts_at=starts_at, reason=reason)
    db.session.add(appointment)
    try:
        db.session.commit()
        flash("Appointment request saved. Contact the clinic to confirm real availability.", "success")
    except IntegrityError:
        db.session.rollback()
        flash("That provider already has a booking at this exact time. Choose another slot.", "error")
    return redirect(url_for("main.dashboard"))

@bp.get("/appointments")
@login_required
def appointments():
    query = Appointment.query
    if not current_user.is_admin:
        query = query.filter_by(user_id=current_user.id)
    items = query.order_by(Appointment.starts_at.desc()).all()
    return render_template("appointments.html", appointments=items)
