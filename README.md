# Speed_Detection_System

Real-time speed violation monitoring system with license plate–based vehicle management, admin dashboard, and automated violation notification emails.

## Overview

This project is a **Flask + MongoDB web application** that helps traffic authorities or organizations track and manage speed violations.
It provides dashboards for key statistics, management views for vehicles and users, and automatic email notifications to vehicle owners when violations occur.

## Features

- **Dashboard**
  - Summary of total violations, violations by zone, current-month counts, and speeding violations.
  - Recent violations list and basic time-series data for analytics.

- **Vehicle & Violation Management**
  - CRUD operations for vehicle records (owner, license plate, email, phone).
  - Violation list with pagination and filtering.
  - Import vehicles from CSV and export users to CSV.

- **User & Role Management**
  - Login system with sessions.
  - Admin and non-admin roles.
  - Admin panel for managing users and system settings.

- **Notifications**
  - Bulk email sending for violations using configurable templates.
  - Stores notification metadata (date, notified flag) in MongoDB.

- **Configurable Settings**
  - Adjustable speed threshold.
  - Customizable email notification template.

## Tech Stack

- **Backend**: Python, Flask
- **Database**: MongoDB (via `pymongo`)
- **Frontend**: HTML templates (Jinja2), CSS, JavaScript
- **Email**: SMTP (configured in `email_sender.py` / `app.py`)

## Getting Started

### Prerequisites

- Python 3.10+ installed
- MongoDB running locally on `mongodb://localhost:27017/`
- Git (if you are cloning the repository)

### Clone the repository

```bash
git clone https://github.com/MayankShukla08/Speed_Detection_System.git
cd Speed_Detection_System
```

### (Optional) Create and activate a virtual environment

```bash
python -m venv .venv
.\.venv\Scripts\activate  # Windows
```

### Install dependencies

Install the core dependencies (adjust as needed based on your environment):

```bash
pip install flask pymongo
```

If you create a `requirements.txt` later, you can instead do:

```bash
pip install -r requirements.txt
```

### Configure email settings

Update the SMTP/email credentials in the code (`email_sender.py` / `app.py`) with your own email account and app password or environment variables.

### Run the application

```bash
python app.py
```

Then open your browser at:

```text
http://127.0.0.1:5000/
```

## Project Structure (high level)

- `app.py` – Main Flask application and routes (dashboard, management, APIs).
- `email_sender.py` – Logic for composing and sending violation emails.
- `database_schema/` – Example JSON/CSV schema and seed data.
- `templates/` – HTML templates for dashboard, login, management, settings, violations, etc.
- `violations/` – Example violation images.

## Notes

- This is a demo/academic-style project; for production, you should:
  - Move secrets (email passwords, secret keys) into environment variables.
  - Add password hashing for users.
  - Harden authentication and authorization.
