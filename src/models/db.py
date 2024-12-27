import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import DictCursor


def connect_db():
    load_dotenv()
    return psycopg2.connect(
        dbname=os.getenv("DBNAME"),
        user=os.getenv("DBUSER"),
        password=os.getenv("DBPASS"),
        host=os.getenv("DBHOST"),
        port=os.getenv("DBPORT"),
        cursor_factory=DictCursor,
    )


def execute_query(query, params=None):
    with connect_db() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, params)
            conn.commit()


def fetch_query(query, params=None):
    with connect_db() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()
