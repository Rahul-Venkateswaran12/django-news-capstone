# News Project

A Django-based news application with role-based access (reader, journalist, editor) and REST API integration.

---

## Setup Instructions (venv method)

1. **Install Dependencies**
   - Ensure Python 3.10+ and MySQL/MariaDB are installed on your system.
   - Create a virtual environment:
     ```bash
     python -m venv venv
     ```
   - Activate it:
     - Linux/Mac:
       ```bash
       source venv/bin/activate
       ```
     - Windows (PowerShell):
       ```powershell
       venv\Scripts\activate
       ```
   - Install requirements:
     ```bash
     pip install -r requirements.txt
     ```

2. **Configure Database**
   - In `news_project/settings.py`, update credentials for your MySQL/MariaDB setup:
     ```python
     DATABASES = {
         'default': {
             'ENGINE': 'django.db.backends.mysql',
             'NAME': 'news_db',
             'USER': 'root',
             'PASSWORD': 'your_password_here',
             'HOST': 'localhost',
             'PORT': '3306',
         }
     }

3. **Configure secrets**
   - In `news/twitter_api.py`, update credentials for the consumer key and secret:
     ```python
     CONSUMER_KEY = 'CONS_KEY'
     CONSUMER_SECRET = 'CONS_SECRET'
   - Can use the secrets provided in secrets.txt or your own.

3. **Apply Migrations**
   - Run:
     ```bash
     python manage.py makemigrations
     python manage.py migrate
     ```

4. **Load Sample Data(optional)**
   - Use the provided `news_db_dump.sql` file:
     ```bash
     mysql -u root -p'your_password_here' news_db < news_db_dump.sql
     ```

5. **Run Development Server**
   - Start the server:
     ```bash
     python manage.py runserver
     ```
   - Open in browser: [http://localhost:8000]

6. **Access the sphinx doccumentation**
   - Open docs/_build/html/index.html
---

## Setup Instructions (Docker method)

1. **Build the Image**
   ```bash
   docker build -t my-django-app .
2. **Run the Image**
   docker run --name my-django-container -p 8000:8000 my-django-app
3. **Test the image**
   Open in browser: [http://localhost:8000]
