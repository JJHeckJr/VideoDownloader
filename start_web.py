import subprocess
def main():
    backend = subprocess.Popen(["uvicorn", "main:app", "--reload"])
    frontend = subprocess.Popen(["npm", "run", "dev"], cwd="frontend")
    try:
        frontend.wait()
    except KeyboardInterrupt:
        pass
    finally:
        backend.terminate()
        frontend.terminate()
if __name__ == "__main__":
    main()