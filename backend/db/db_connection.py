import subprocess
import sys
import time

import psycopg2

from backend.db.schema import CREATE_VIDEO_REQUESTS_TABLE

DATABASE_URL = "postgresql://videodownloader:videodownloader@localhost:5433/videodownloader"

DOCKER_DESKTOP_PATH = r"C:\Program Files\Docker\Docker\Docker Desktop.exe"

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()

def ensure_docker_running():
    def docker_is_up():
        return subprocess.run(["docker", "info"], capture_output=True).returncode == 0

    if docker_is_up():
        return

    if sys.platform == "win32":
        subprocess.Popen([DOCKER_DESKTOP_PATH])
    elif sys.platform == "darwin":
        subprocess.Popen(["open", "-a", "Docker"])
    else:
        raise RuntimeError("Docker engine is not running. Please start it and try again.")

    print("Starting Docker...")
    for _ in range(60):
        if docker_is_up():
            return
        time.sleep(2)
    raise RuntimeError("Timed out waiting for Docker to start")

def setup_database():
    ensure_docker_running()
    subprocess.run(["docker", "compose", "up", "-d"], check=True)

    for _ in range(10):
        try:
            conn = psycopg2.connect(DATABASE_URL)
            break
        except psycopg2.OperationalError:
            print("Waiting for database to be ready...")
            time.sleep(1)
    else:
        print("Could not connect to the database")
        return None
    cur = conn.cursor()
    cur.execute(CREATE_VIDEO_REQUESTS_TABLE)
    conn.commit()
    return conn
