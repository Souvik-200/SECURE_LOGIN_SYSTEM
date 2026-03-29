# Secure Login System with Role-Based Access Control

A production-minded demonstration of authenticated web sessions, **RBAC** (Admin vs User), password hashing with **bcrypt**, **JWT** delivered via **httpOnly** cookies, **server-side math CAPTCHA**, **account lockout** after repeated failed logins, **CSRF** protection on mutating requests, and **ORM-only** database access to avoid SQL injection.

## Features

| Area | Implementation |
|------|----------------|
| Authentication | Email + password; JWT (access) in signed httpOnly cookie |
| Authorization | Admin-only routes; user dashboard separated from admin panel |
| Passwords | bcrypt (cost factor 12) |
| Sessions / tokens | Flask-JWT-Extended; optional longer expiry (“remember”) |
| CAPTCHA | Server-side numeric challenge stored in Flask session (one-shot verify) |
| Lockout | Configurable max failures + lock duration (`MAX_FAILED_LOGIN_ATTEMPTS`, `LOCKOUT_MINUTES`) |
| Input validation | WTForms + client-side hints; duplicate email/username handled safely |
| SQL injection mitigation | SQLAlchemy ORM exclusively (no string-concatenated SQL) |
| CSRF | Flask-WTF on registration, login, and admin POST actions |

## 📸 Screenshots

### 🔐 Signin Page
<p align="center">
   <img src="docs/screenshots/sign_in.png" width="600"/>
</p>

### 📝 Register Page
<p align="center">
   <img src="docs/screenshots/register.png" width="600"/>
</p>

## 📊 Dashboard Preview
<p align="center">
  <img src="docs/screenshots/Admin_dashboard.png" width="600"/>
</p>

## Project layout

```
SECURE_LOGIN_SYSTEM/
├── app/
│   ├── __init__.py          # Application factory, CLI commands
│   ├── captcha.py           # CAPTCHA generation / verification
│   ├── decorators.py        # admin_required (RBAC)
│   ├── extensions.py        # db, jwt, csrf
│   ├── forms.py             # WTForms + password policy
│   ├── models.py            # User model
│   ├── security.py          # bcrypt helpers
│   ├── routes/
│   │   ├── auth.py          # Register, login, logout
│   │   ├── admin.py         # Admin dashboard & user management
│   │   ├── main.py          # Home / health
│   │   └── user_dashboard.py
│   └── services/
│       └── user_service.py  # Registration, auth, lockout logic
├── config.py
├── docs/
│   └── screenshots/         # Add your screenshots here for the assignment
├── instance/                # Local SQLite file (gitignored when used)
├── static/
│   ├── css/style.css
│   └── js/validation.js
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── user_dashboard.html
│   └── admin_dashboard.html
├── tests/
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── wsgi.py
```

## Prerequisites

- Python 3.10+ (tested on 3.10)
- Optional: MySQL 8+ if you use MySQL instead of the default SQLite

## Quick start (SQLite default)

1. **Clone** (or copy) the project and enter the directory.

2. **Create a virtual environment and install dependencies**

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\pip install -r requirements.txt
   ```

3. **Environment**

   ```powershell
   copy .env.example .env
   ```

   Edit `.env`: set strong random values for `SECRET_KEY` and `JWT_SECRET_KEY` (each at least 32 bytes of randomness in production).

4. **Create an administrator (recommended)**

   Public registration defaults new accounts to the **user** role unless `ALLOW_PUBLIC_ADMIN_REGISTRATION=true` (discouraged in production).

   ```powershell
   .\.venv\Scripts\flask --app wsgi:app create-admin YourAdmin admin@example.com
   ```

5. **Run the app**

   ```powershell
   .\.venv\Scripts\flask --app wsgi:app run
   ```

   Open `http://127.0.0.1:5000` — you will be redirected to login. Use the admin account or register a new user.

## MySQL setup

1. Create a database, for example: `CREATE DATABASE secure_login CHARACTER SET utf8mb4;`

2. In `.env` set:

   ```env
   DATABASE_URL=mysql+pymysql://USER:PASSWORD@127.0.0.1:3306/secure_login
   ```

3. Restart the app; tables are created on startup (`db.create_all()`). For larger deployments, prefer **Flask-Migrate** / Alembic migrations (not included to keep the teaching scope focused).

## Configuration reference

| Variable | Purpose |
|----------|---------|
| `SECRET_KEY` | Flask session signing, CSRF salt |
| `JWT_SECRET_KEY` | JWT signing (keep distinct from `SECRET_KEY` in production) |
| `JWT_COOKIE_SECURE` | Set `true` behind HTTPS |
| `ALLOW_PUBLIC_ADMIN_REGISTRATION` | If `true`, registration form may create admins (unsafe for public internet) |
| `MAX_FAILED_LOGIN_ATTEMPTS` | Failures before lockout |
| `LOCKOUT_MINUTES` | Lock duration |

## Testing

```powershell
.\.venv\Scripts\python -m pytest tests -v
```

Tests cover duplicate registration, login + user dashboard redirect, account lockout with correct password rejected, and **403** for a normal user accessing `/admin/dashboard`.

## Screenshots (for your submission)

Capture and place images under `docs/screenshots/`, for example:

- Login page with CAPTCHA  
- Registration with validation errors  
- User dashboard  
- Admin dashboard with user table and actions  

Reference them in your report or add markdown image links in this README after export.

## Security notes for production

- Terminate TLS and set `JWT_COOKIE_SECURE=true`, strong secrets, and disable `ALLOW_PUBLIC_ADMIN_REGISTRATION`.  
- Prefer hosting CAPTCHA with a proven provider (e.g. Turnstile, reCAPTCHA) for stronger bot resistance; the built-in math CAPTCHA is suitable for coursework and layered defense, not as the only control on the open internet.  
- Add rate limiting (e.g. Flask-Limiter) at reverse proxy or app layer.  
- Consider refresh tokens and shorter access lifetimes if you expose APIs to third parties.

## Challenges faced and solutions

1. **Balancing usability and assignment requirements**  
   The UI allows selecting Admin at registration for demos, but the server **defaults to `user`** unless `ALLOW_PUBLIC_ADMIN_REGISTRATION=true`, so accidental open admin registration is avoided while still satisfying the “role field” requirement.

2. **Brute-force mitigation without external APIs**  
   Combined **CAPTCHA** (per attempt regeneration) with **incremental lockout** so automated guessing is throttled even before network-level rate limits.

3. **JWT in cookies vs. pure sessions**  
   JWTs in **httpOnly** cookies give stateless verification and match the brief; CSRF for cookie-based JWT is a known topic—mutations are limited to **form POSTs with Flask-WTF CSRF**, and cookies use **SameSite=Lax** as a baseline.

4. **Template path with package layout**  
   The Flask app lives under the `app` package, so `template_folder` and `static_folder` are resolved relative to the **repository root** explicitly (see `app/__init__.py`).

## License

Educational / demonstration use. Harden and review before any production deployment.
