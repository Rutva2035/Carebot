import pytest
from carebot import create_app, db
from carebot.models import User, Symptom, Condition, ConditionSymptom, Doctor
from werkzeug.security import generate_password_hash

@pytest.fixture()
def app():
    app = create_app({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,
        "SECRET_KEY": "test-secret",
        "SQLALCHEMY_DATABASE_URI": "sqlite://",
    })
    with app.app_context():
        db.create_all()
        user = User(name="Test User", email="test@example.com", password_hash=generate_password_hash("a-very-long-test-password"))
        symptom = Symptom(name="test symptom")
        condition = Condition(name="Demo match", description="Demo", advice="Not advice", source_note="Test fixture")
        db.session.add_all([user, symptom, condition])
        db.session.flush()
        db.session.add(ConditionSymptom(condition_id=condition.id, symptom_id=symptom.id, weight=2))
        db.session.add(Doctor(display_name="Test Provider", specialty="General Practice", clinic_name="Test Clinic", location="Test location"))
        db.session.commit()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture()
def client(app):
    return app.test_client()
