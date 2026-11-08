import os
from datetime import datetime, timezone
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash
from dotenv import load_dotenv

load_dotenv()
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY", "dev-only-change-me"),
        SQLALCHEMY_DATABASE_URI=os.getenv(
            "DATABASE_URL", "sqlite:///" + os.path.join(app.instance_path, "carebot.db")
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "false").lower() == "true",
        REMEMBER_COOKIE_HTTPONLY=True,
        REMEMBER_COOKIE_SAMESITE="Lax",
        MAX_CONTENT_LENGTH=2 * 1024 * 1024,
    )
    if test_config:
        app.config.update(test_config)

    os.makedirs(app.instance_path, exist_ok=True)
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"
    csrf.init_app(app)

    from . import models
    from .auth import bp as auth_bp
    from .main import bp as main_bp
    from .admin import bp as admin_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)

    @app.context_processor
    def inject_year():
        return {"current_year": datetime.now(timezone.utc).year}

    @app.cli.command("init-db")
    def init_db():
        """Create database tables."""
        db.create_all()
        print("CareBot database tables created.")

    @app.cli.command("create-admin")
    def create_admin():
        """Create an admin account interactively; no default credentials."""
        import getpass
        from .models import User
        email = input("Admin email: ").strip().lower()
        name = input("Admin name: ").strip()
        password = getpass.getpass("Admin password (12+ characters): ")
        if len(password) < 12:
            raise SystemExit("Password must be at least 12 characters.")
        if User.query.filter_by(email=email).first():
            raise SystemExit("An account with that email already exists.")
        user = User(name=name, email=email, password_hash=generate_password_hash(password), role="admin")
        db.session.add(user)
        db.session.commit()
        print("Admin account created.")

    @app.cli.command("seed-demo")
    def seed_demo():
        """Add clearly fictional demo catalogue entries; no real doctors or clinical advice."""
        from .models import Symptom, Condition, ConditionSymptom, Doctor
        if Symptom.query.first():
            print("Demo catalogue already exists; skipping.")
            return
        symptoms = {}
        for name in ["headache", "cough", "fever", "fatigue"]:
            symptoms[name] = Symptom(name=name)
            db.session.add(symptoms[name])
        db.session.flush()
        # Demonstration-only labels. Replace with clinician-reviewed content before real use.
        demo = Condition(
            name="Demo symptom pattern A",
            description="Illustrative catalogue entry for testing symptom matching.",
            advice="This is demo content, not medical advice.",
            source_note="Demo data; not clinically validated.",
        )
        db.session.add(demo)
        db.session.flush()
        for symptom in symptoms.values():
            db.session.add(ConditionSymptom(condition_id=demo.id, symptom_id=symptom.id, weight=1))
        db.session.add(Doctor(
            display_name="Demo Provider One",
            specialty="General Practice",
            clinic_name="Demo Clinic",
            location="Demo location — replace before use",
            contact_email="demo@example.invalid",
            active=True,
        ))
        db.session.commit()
        print("Demo catalogue added. These are fictional placeholders.")

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return db.session.get(User, int(user_id))
