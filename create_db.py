"""
Creates the neurolearn_db database if it doesn't already exist.
Run this once: python create_db.py
"""

import psycopg2
from psycopg2 import sql

# ---- EDIT THIS if your PostgreSQL user/password/host/port differ ----
DB_USER = "postgres"
DB_PASSWORD = "yasir123"   # <-- apna PostgreSQL password yahan daalo
DB_HOST = "localhost"
DB_PORT = "5432"
NEW_DB_NAME = "neurolearn_db"
# -----------------------------------------------------------------------

conn = psycopg2.connect(
    dbname="postgres",  # connect to the default admin database first
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
)
conn.autocommit = True
cur = conn.cursor()

cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (NEW_DB_NAME,))
exists = cur.fetchone()

if exists:
    print(f"Database '{NEW_DB_NAME}' already exists. Nothing to do.")
else:
    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(NEW_DB_NAME)))
    print(f"Database '{NEW_DB_NAME}' created successfully!")

cur.close()
conn.close()
