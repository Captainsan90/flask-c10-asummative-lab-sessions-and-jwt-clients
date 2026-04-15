# Flask Auth API

A Flask backend that supports both session-based authentication and JWT-based authentication, plus protected CRUD routes for user notes.

## Features
- Signup and login
- Session auth and JWT auth
- Check session / current user
- Logout
- Protected CRUD routes
- Pagination for notes
- Password hashing with Flask-Bcrypt
- Database migrations with Flask-Migrate

## Install

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt