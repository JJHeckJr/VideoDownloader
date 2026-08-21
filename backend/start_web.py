import shutil
import subprocess

from backend.db.db_connection import setup_database

def main():
    conn = setup_database()
    if conn is None:
        return
    conn.close()
    npm = shutil.which("npm") or "npm"
    backend = subprocess.Popen(["uvicorn", "backend.main:app", "--reload"])
    frontend = None
    try:
        frontend = subprocess.Popen([npm, "run", "dev"], cwd="frontend")
        frontend.wait()
    except KeyboardInterrupt:
        pass
    finally:
        backend.terminate()
        if frontend is not None:
            frontend.terminate()
if __name__ == "__main__":
    main()