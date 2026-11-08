from datetime import datetime, timedelta
from carebot import db
from carebot.models import User, Doctor, Appointment

def login(client):
    return client.post("/auth/login", data={"email": "test@example.com", "password": "a-very-long-test-password"}, follow_redirects=True)

def test_home_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"CareBot" in response.data

def test_register_requires_long_password(client):
    response = client.post("/auth/register", data={
        "name": "New User", "email": "new@example.com", "password": "short"
    }, follow_redirects=True)
    assert b"at least 12 characters" in response.data

def test_user_can_open_assessment(client):
    login(client)
    response = client.get("/assessment")
    assert response.status_code == 200
    assert b"test symptom" in response.data

def test_assessment_creates_catalogue_match(client):
    login(client)
    response = client.post("/assessment", data={"symptoms": ["1"]}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Demo match" in response.data

def test_booking_persists(client, app):
    login(client)
    future = (datetime.now() + timedelta(days=3)).replace(hour=10, minute=0, second=0, microsecond=0)
    response = client.post("/appointments/book", data={
        "doctor_id": "1", "date": future.strftime("%Y-%m-%d"),
        "time": future.strftime("%H:%M"), "reason": "Test request"
    }, follow_redirects=True)
    assert response.status_code == 200
    with app.app_context():
        assert Appointment.query.count() == 1

def test_duplicate_doctor_slot_rejected(client, app):
    login(client)
    future = (datetime.now() + timedelta(days=4)).replace(hour=11, minute=0, second=0, microsecond=0)
    data = {"doctor_id": "1", "date": future.strftime("%Y-%m-%d"), "time": future.strftime("%H:%M")}
    client.post("/appointments/book", data=data)
    response = client.post("/appointments/book", data=data, follow_redirects=True)
    assert b"already has a booking" in response.data
    with app.app_context():
        assert Appointment.query.count() == 1
