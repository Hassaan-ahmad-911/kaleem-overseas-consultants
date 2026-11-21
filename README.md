# Kaleem Overseas Consultants

Django website for Kaleem Overseas Consultants Pvt. Ltd., a visa consultancy and travel services company.

## Features

- Public pages: Home, About, Services, Visit Visa, Business Visa, Visa Guidance, Countries, Tour Packages, Gallery, Success Stories, Contact
- Appointment booking with automatic appointment numbers (`KOC-<year><0001>`)
- Appointment status lookup (appointment number + phone number) and PDF appointment letter download once approved
- Contact form (messages are stored and read in the admin)
- Django admin for all content: services, countries, appointments (approve/reject), contact messages, testimonials, gallery, tour packages, success stories

## Tech stack

Django 5.1, PostgreSQL, Bootstrap 5.3, Font Awesome 6.5, ReportLab (PDF letters), python-decouple (settings from `.env`). Deployed with Gunicorn + Nginx.

## Project layout

| Path | Contents |
|---|---|
| `kaleem_overseas/` | Project settings and root URLs |
| `core/` | The only app: models, views, forms, admin, PDF/number helpers (`utils.py`), contact details (`context_processors.py`), template tags, management commands |
| `templates/` | `base.html`, `navbar.html`, `footer.html`, `intro.html` and page templates in `templates/core/` |
| `static/` | CSS, JavaScript and permanent images |
| `media/` | Uploaded files and generated letters (not in Git) |

Contact details shown across the site (phone, email, address, hours, social links) are defined once in `core/context_processors.py`.

## Run locally

1. Install Python 3.12+ and PostgreSQL, and create a database.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in the values. For local development set `DEBUG=True`.
4. Apply migrations and create an admin user:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```
5. Start the development server and open http://127.0.0.1:8000/:
   ```bash
   python manage.py runserver
   ```

## Deploy (VPS: Gunicorn + Nginx)

1. Make sure the server's `.env` has `DEBUG=False`, a strong `SECRET_KEY`, `ALLOWED_HOSTS` set to the site's domain(s) and server IP, and `CSRF_TRUSTED_ORIGINS` set to the `https://` origins (see `.env.example`).
2. On the server:
   ```bash
   git pull
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   sudo systemctl restart gunicorn
   ```
3. Nginx must serve `/static/` from `staticfiles/` and `/media/` from `media/`.

## Maintenance

- `python manage.py secure_appointment_letters` lists appointment letters that still have guessable file names; add `--apply` to rename them and delete unused letter files.
