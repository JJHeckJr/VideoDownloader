import psycopg2

DATABASE_URL = "postgresql://videodownloader:videodownloader@localhost:5433/videodownloader"

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()