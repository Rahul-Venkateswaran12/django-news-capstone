# News Project

A Django-based news application with role-based access (reader, journalist, editor) and REST API integration.

## Setup Instructions

1. **Install Dependencies**
   - Ensure Python 3.13 and MySQL/MariaDB are installed.
   - Create a virtual environment: `python -m venv venv`
   - Activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
   - Install requirements: `pip install django djangorestframework djangorestframework-xml mysqlclient`

2. **Configure Database**
   - Update `news_project/settings.py` with your MySQL/MariaDB credentials if different:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'news_db',
             'USER': 'root',
             'PASSWORD': 'your_password',
             'HOST': 'localhost',
             'PORT': '3306',
         }
     }
   - Ensure MariaDB is running locally

3. **Apply Migrations**
   - Run migrations to set up the database structure: `python manage.py migrate`

4. **Load the Database Dump**
   - Use the provided `news_db_dump.sql` file to populate the database with sample data:
     - Import the dump into your `news_db` database:
       ```bash
       mysql -u root -p'your_password' news_db < news_db_dump.sql
