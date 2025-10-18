# 🚀 FastAPI Backend

A modern and high-performance backend built with **FastAPI**, **SQLAlchemy**, and **Alembic** for real-time database migrations.  
This setup is lightweight, modular, and ready for production deployment.

---

## 📦 Tech Stack

- **FastAPI** — Modern web framework for building APIs with Python  
- **Uvicorn** — ASGI server for running FastAPI apps  
- **SQLAlchemy** — ORM for database modeling and queries  
- **Alembic** — Database migration tool for SQLAlchemy  
- **Python 3.10+**  
- **Node.js & npm** — For managing frontend or tool dependencies (if required)

---

## 🧰 Project Setup Guide

### 1. Clone the Repository 
```bash
git clone https://github.com/himanshu1-sharma/fastapiwithpython.git
```
```bash
cd fastapiwithpython
```

### 2. Create and Activate Virtual Environment
For Windows:
```bash
python -m venv venv
```
```bash
venv\Scripts\activate
```
For macOS / Linux:
```bash
python3 -m venv venv
```
```bash
source venv/bin/activate
```


### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

If you don't have a requirements.txt file yet, you can create one:
```bash
pip freeze > requirements.txt
```


### 4. Setup Environment Variables

Create a .env file in the root directory and add your configuration details:
```bash
APP_NAME=XXXXXXXX
APP_ENV=XXXXXXXX

DB_USER=XXXXX
DB_PASSWORD=XXXXXXXX
DB_HOST=XXXXXX
DB_PORT=XXXXX
DB_NAME=XXXXXX

AWS_ACCESS_KEY_ID=XXXXXXXXXXXXXXX
AWS_SECRET_ACCESS_KEY=XXXXXXXXXXXXXXXXXXXXXXXXX
AWS_REGION=XXXXXXXXXXXXX
S3_BUCKET_NAME=XXXXXXXXXXXXXXX
```

### 5. Run Database Migrations (Alembic)

Initialize Alembic (if not already initialized):
```bash
alembic init alembic
```


To generate a new migration after model changes:
```bash
alembic revision --autogenerate -m "Initial migration"
```


To apply migrations:
```bash
alembic upgrade head
```


### 6. Run the Application
Using Uvicorn:
```bash
uvicorn app.main:app --reload
```

The app will be available at 👉 http://127.0.0.1:8000

### 7. API Documentation

Once the server is running, explore the automatic docs:
```bash
Swagger UI: http://127.0.0.1:8000/docs
```
```bash
ReDoc: http://127.0.0.1:8000/redoc
```
