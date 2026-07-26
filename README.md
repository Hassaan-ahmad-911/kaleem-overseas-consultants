# Kaleem Overseas Consultant

A Django-based visa consultancy website for Kaleem Overseas Consultant.

## Features
- Home, About, Services, Countries, Contact, Apply Visa, Dashboard
- User registration, login, logout
- Visa application submission with file uploads
- Appointment booking after login
- Admin management for countries, applications, testimonials, and appointments

## Run Locally
1. Create and activate the project virtual environment if needed:
   ```bash
   .venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Apply migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```
4. Create an admin user:
   ```bash
   python manage.py createsuperuser
   ```
5. Start the development server:
   ```bash
   python manage.py runserver
   ```
6. Open `http://127.0.0.1:8000/` in your browser.

In VS Code, the project is configured to use the local `.venv` interpreter when available.
