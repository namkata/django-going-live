Going live in production with a Django web application involves several steps to ensure that your application is secure, performant, and stable. Here's a high-level overview of the process:

# 01. Creating a production environment
It’s time to deploy your Django project in a production environment. You are going to follow these steps to get your project live:
- Configure project settings for a production environment
- Use a PostgreSQL database
- Set up a web server with uWSGI and NGINX
- Serve static assets through NGINX
- Secure connections using SSL
- Use Daphne to serve Django Channels

# 02. Managing settings for multiple environments
In real-world projects, you will have to deal with multiple environments. You will have at least a local and  a production environment, but you could have other environments as well, such as testing or preproduction environments. Some project settings will be common to all environments, but others will have to be overriden per environment. Let's set up project settings for multiple environments, while keeping everything neatly organized.

Create a ***settings/*** directory next to the ***settings.py*** file of the ***educa*** project. Rename the ***settings.py*** file to ***base.py*** and move it into the new ***settings/*** directory. Create the following additional files inside the ***settings/*** folder so that the new directory books as follows:
```
settings/
    __init__.py
    base.py
    local.py
    pro.py
```
These files are as follows:
- `base.py`: The base settings file that contains common settings (previously `settings.py`)
- `local.py`: Custom settings for your local environment
- `pro.py`: Custom settings for the production environment

Edit the `settings/base.py` file and replace the following line:
```python
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
```
or
```python
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```
with the following one:
```python
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.path.join(__file__,os.pardir))))
```
You have moved your settings files to a directory one level lower, so you need `BASE_DIR` to point to the parent directory to be correct. You achieve this by pointing to parent directory with `os.pardir`.
Edit the `settings/local.py` file and add following lines of code:
```python
import os
from .base import *
DEBUG = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3')
    }
}
```
This is the settings file for your local environment. You import all settings defined in the `base.py` file and you only define specific settings for this environment. You copy the `DEBUG` and `DATABASES` settings from the `base.py` file, since these will be set per environment. You can remove the `DATABASES` and `DEBUG` settings from the `base.py` settings file.
Edit the `settings/pro.py` file and make it look as follows:
```python
import os
from .base import *
DEBUG = False
ADMINS = (
    ('root', 'root@example.com')
)
ALLOWED_HOSTS = ['*']
DATABASES = {
    'default': {
    }
}
```
These are the settings for the production environment. Let's take a closer look at each of them:
- `DEBUG`: Setting `DEBUG` to `False` should be mandatory for any production environment. Failing to do so will result in the traceback information and sensitive configuration data being exposed to everyone.
- `ADMINS`: When `DEBUG` is `False` and a view raises an exception, all information will be sent by email to the people listed in the `ADMINS` setting. Make sure that you replace the name/email tuple with your own information.
- `ALLOWED_HOSTS`:` Django will only allow the hosts included in this list to serve the application. This is a security measure. You include the asterisk symbol, *, to refer to all hostnames that can be used for serving the application later.
- `DATABASES`: You just keep this setting empty. We are going to cover the database setup for production later.

When handling multiple environments, create a base settings file and a settings file for each environment. Environment settings files should inherit the common settings and override environment-specific settings.

You have placed the project settings in a different location than the default `settings.py` file. You will not be able to execute any commands with the `manage.py` tool unless you specify the settings module to use. You will need to add a `--settings` flag when you run management commands from the shell or set a `DJANGO_SETTINGS_MODULE` environment variable.

Open the shell and run the following command:
```python
export DJANGO_SETTINGS_MODULE=educa.settings.pro
```

This will set the `DJANGO_SETTINGS_MODULE` environment variable for the current shell session. If you want to avoid executing this command for each new shell, add this command to your shell's configuration in the `.bashrc` or `.bash_profile` files. If you don't set this variable, you will have to run management commands, including the `--settings` flag, as follows:
```python
python manage.py shell --settings=educa.settings.pro
```

You have successfully organized settings for handling multiple environments.

# 03. Using PostgreSQL

Throughout this book, you have mostly used the SQLite database. SQLite is simple and quick to set up, but for a production environment, you will need a more powerful database, such as PostgreSQL, MySQL or Oracle. You already learned how to install PostgreSQL and set up a PostgreSQL database, Extending Your Blog Application. If you need to install PostgreSQL, you can read the Installing PostgreSQL section.

Let's create a PostgreSQL user. Open the shell and run the following commands to create a database user:
```shell
su postgres
createuser -dP educa
```
You will be prompted for a password and the permissions that you want to give to this user. Enter the desired password and permissions, and then create a new database with the following command:
```shell
createdb -E utf8 -U educa educadb
```
Then, edit the `settings/pro.py` file and modify the `DATABASES` setting to make it look as follows:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'educa',
        'USER': 'educa',
        'PASSWORD': '*********'
    }
}
```
Replace the preceding data with the database name and credentials for the user you created. The new database is empty. Run the following command to apply all database migrations:
```python
python manage.py migrate
```
Finally, create a superuser with the following command:
```python
python manage.py createsuperuser
```
# Checking your project
Django includes the `check` management command for checking your project at any time. This command inspects the applications installed in your Django project and outputs any errors or warnings. If you include the `--deploy` option, additional checks only relevant for production use will be triggered. Open the shell and run the following command to perform a check:
```shell
python manage.py check --deploy
```
You will see output with no errors, but several warnings. This means the check was successful, but you should go through the warnings to see if there is anything more you can do to make your project safe for production. We are not going to go deeper into this, but keep in mind that you should check your project before production use to look for any relevant issues.

# Serving Django through WSGI
Django's primary deployment platform is WSGI. `WSGI` stands for ***Web Server Gateway Interface*** and it is the standard for serving Python applications on the web.

When you generate a new project using the `startproject` command, Django creates a `wsgi.py` file inside your project directory. This file contains a WSGI application callable, which is an access point to your application.

WSGI is used for both running your project with the Django development server and deploying your application with the server of your choice in a production environment.

You can learn more about WSGI at [`link`](https://wsgi.readthedocs.io/en/latest/)

# Installing uWSGI
