# Document Management System

A simple document management system built with Django.

## Features
- Upload documents
- View documents
- Basic metadata (title, description)
- Simple owner-based access control
- Basic categories

## Setup
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `python manage.py migrate`
6. Create superuser: `python manage.py createsuperuser`
7. Run the development server: `python manage.py runserver`

## Technology Stack
- Python
- Django
- SQLite (for development)
- HTML/CSS
- JavaScript

## Created by
Avishek Paul