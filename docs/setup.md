# Setup Guide

Follow these steps to set up the development environment.

## 🛠 Prerequisites
- Python 3.10+
- PostgreSQL
- Virtual Environment (venv)

## 📥 Installation

1. **Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**:
   Create a `.env` file in the root directory based on `.env.example`:
   ```text
   DEBUG=True
   SECRET_KEY=your_secret_key
   DB_NAME=multi_vendor
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ```

4. **Database Migration**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Superuser Creation**:
   ```bash
   python manage.py createsuperuser
   ```

## 🚀 Running the App
```bash
python manage.py runserver
```
Access the API at `http://localhost:8000/api/v1/`.
