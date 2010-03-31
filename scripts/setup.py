#!/usr/bin/env python
# Initialization script template.  Change as needed.

# path of the root directory for the Django application
rootdir = "/../../noizereduzer"

import os
import sys
# Adds the directory where settings_locals.py can be found.
sys.path.append(os.path.abspath(__file__ + rootdir))
from settings import DATABASE_ENGINE, DATABASE_NAME, DATABASE_USER

if DATABASE_ENGINE == "postgresql_psycopg2" or DATABASE_ENGINE == "postgresql":
    commands = (
           "sudo -u postgres psql --command 'CREATE DATABASE " + DATABASE_NAME + ";'",
           "sudo -u postgres psql --command '\l'", # Same as SHOW DATABASES in MySQL
           "sudo -u postgres psql " + DATABASE_NAME + " --command 'CREATE USER " + DATABASE_USER + ";'",
           "sudo -u postgres psql --command '\du'", # Users
    )
elif DATABASE_ENGINE == "mysql":
    commands = (
                #TODO
    )
    pass

for command in commands:
    exitcode = os.system(command)

exitcode = os.system("cd " + rootdir[4:] + """
pwd
ls -la
python manage.py syncdb
""")
