# CareBot — Full-stack portfolio upgrade

A responsive Flask web application demonstrating account management, symptom
record capture, weighted catalogue matching, provider directory management,
and appointment-request scheduling.

## Important scope and safety statement

CareBot is an educational software prototype, **not a medical device**. It
does not diagnose, triage, rule out illness, recommend treatment, or determine
whether care is urgent. The catalogue-matching score is a software
demonstration only; it is not a probability or clinical severity score.
Demo catalogue records and providers are fictional placeholders. Do not use
real patient data or present the app as clinically validated.

For a real healthcare product, obtain clinical, privacy, security and legal
review; use clinician-approved content; validate the workflow; and integrate
with verified provider systems. A saved appointment in this app is only a
request and does not confirm clinic availability.

## What is included

- Responsive Flask web interface.
- User registration and sign-in with Werkzeug password hashing.
- Admin role and protected admin routes.
- CSRF protection on forms.
- SQLAlchemy models with SQLite by default and MySQL support.
- Symptom catalogue and transparent weighted matching demonstration.
- Assessment history associated with the signed-in user.
- Provider directory maintained by admin.
- Appointment request creation directly from provider cards, user-specific history and admin cancellation.
- Unique database constraint preventing duplicate provider/time slots.
- Automated tests for registration, assessment and appointment booking.

## Requirements

- Python 3.10+
- SQLite (default) or MySQL 8+

## Local setup (SQLite — easiest)

```bash
python -m venv .venv

# Windows PowerShell
.venv\\Scripts\\Activate.ps1

# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env`. Generate a secret key, for example:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Put the generated value in `SECRET_KEY`. Keep `.env` private.

Create the schema:

```bash
flask --app run.py init-db
```

Create an admin account interactively:

```bash
flask --app run.py create-admin
```

Optionally add fictional demo catalogue entries:

```bash
flask --app run.py seed-demo
```

Run locally:

```bash
flask --app run.py run
```

Open http://127.0.0.1:5000

## MySQL configuration

Create a dedicated database and least-privilege database user. Then set
`DATABASE_URL` in `.env`:

```text
DATABASE_URL=mysql+pymysql://carebot_user:URL_ENCODED_PASSWORD@localhost:3306/carebot
```

URL-encode special characters in the password. Initialise tables using the
same `flask --app run.py init-db` command.

For an existing MySQL deployment, back up the database first. This project
uses a new SQLAlchemy schema and does not automatically migrate the old
Tkinter project's tables. Migrate only after reviewing and mapping the old
schema to the models in `carebot/models.py`.

## Admin workflow

Use the `create-admin` CLI command. Admins can:
- View appointment requests.
- Mark appointments cancelled.
- Add provider directory entries.
- Add symptom catalogue entries.

The demo seed data is fictional. Replace it with verified directory data only
if you have permission and a reliable source.

## Appointment behaviour

- Users choose a listed provider, date and time.
- Start times must be in the future and on `:00` or `:30`.
- A unique constraint on `(doctor_id, starts_at)` prevents duplicate bookings
  for the same provider and exact start time.
- Users see their own appointment requests; admins can see all requests.
- Admins can cancel requests.

This is not a live clinic booking integration. It does not query external
calendars, reserve a real clinic slot, send notifications, handle payments or
confirm provider availability. Contact the clinic directly.

## Run tests

```bash
pytest -q
```

## Security and production-readiness checklist

Before deploying publicly:
- Set a strong random `SECRET_KEY`.
- Set `COOKIE_SECURE=true` behind HTTPS.
- Use a dedicated least-privilege MySQL account.
- Add database migrations (e.g. Flask-Migrate/Alembic).
- Add rate limiting, login throttling, password reset and email verification.
- Add audit logs, backups, monitoring and dependency scanning.
- Review privacy requirements before collecting any personal or health data.
- Do not store sensitive health data without a proper legal/security review.
- Never commit `.env`, credentials, real patient data or database dumps.
- Rotate credentials that were previously committed to public Git history and
  rewrite Git history to remove exposed secrets.

## Project structure

```text
CareBot_Professional/
├── carebot/
│   ├── __init__.py
│   ├── models.py
│   ├── services.py
│   ├── auth.py
│   ├── main.py
│   ├── admin.py
│   ├── templates/
│   └── static/css/style.css
├── tests/
├── instance/
├── .env.example
├── .gitignore
├── requirements.txt
├── run.py
└── README.md
```

## Resume description (only after you run and verify it)

**CareBot — Healthcare Workflow Web Application | Python, Flask, MySQL, SQLAlchemy**
- Built a responsive web application with user authentication, role-based admin
  access, symptom-record capture, and a configurable symptom-catalogue matching
  workflow.
- Designed relational data models for users, symptom catalogues, assessment
  history, providers and appointment requests.
- Implemented appointment scheduling with server-side validation and database
  constraints to prevent duplicate provider/time bookings.
- Added CSRF protection, password hashing, environment-based configuration and
  automated tests.

Do not claim production deployment, clinical validation, live clinic booking,
or MySQL deployment until you have implemented and verified those items.
