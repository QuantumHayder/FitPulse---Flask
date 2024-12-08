import subprocess
import pathlib

src = pathlib.Path(__file__).resolve().parent
theme = src / "theme"

try:
    subprocess.run(["npm", "run", "watch"], check=True, cwd=theme)
except subprocess.CalledProcessError as e:
    print(f"Error running TailwindCSS watcher: {e}")
