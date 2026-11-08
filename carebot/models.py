from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from . import db

def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    @property
    def is_admin(self):
        return self.role == "admin"

class Symptom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)

class Condition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    advice = db.Column(db.Text, nullable=False)
    source_note = db.Column(db.String(255), default="Content requires clinical review.")
    active = db.Column(db.Boolean, nullable=False, default=True)

class ConditionSymptom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    condition_id = db.Column(db.Integer, db.ForeignKey("condition.id"), nullable=False)
    symptom_id = db.Column(db.Integer, db.ForeignKey("symptom.id"), nullable=False)
    weight = db.Column(db.Integer, nullable=False, default=1)
    condition = db.relationship("Condition", backref="symptom_links")
    symptom = db.relationship("Symptom")
    __table_args__ = (db.UniqueConstraint("condition_id", "symptom_id", name="uq_condition_symptom"),)

class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    display_name = db.Column(db.String(150), nullable=False)
    specialty = db.Column(db.String(120), nullable=False)
    clinic_name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    contact_email = db.Column(db.String(255))
    active = db.Column(db.Boolean, nullable=False, default=True)

class Assessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    symptoms_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    user = db.relationship("User", backref="assessments")

class AssessmentMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey("assessment.id"), nullable=False)
    condition_id = db.Column(db.Integer, db.ForeignKey("condition.id"), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    assessment = db.relationship("Assessment", backref="matches")
    condition = db.relationship("Condition")

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False, index=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False, index=True)
    starts_at = db.Column(db.DateTime, nullable=False, index=True)
    reason = db.Column(db.String(500), default="")
    status = db.Column(db.String(20), nullable=False, default="booked")
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    user = db.relationship("User", backref="appointments")
    doctor = db.relationship("Doctor")
    __table_args__ = (
        db.UniqueConstraint("doctor_id", "starts_at", name="uq_doctor_start_slot"),
    )
