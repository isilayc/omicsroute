"""Build the browser planner and publish its assets to Vercel's CDN."""
from pathlib import Path
import shutil
import subprocess


def main():
    root = Path(__file__).resolve().parent
    frontend = root / "frontend"
    npm = shutil.which("npm")
    if npm is None:
        raise RuntimeError("Node.js/npm is required to build the planner")
    subprocess.run([npm, "ci"], cwd=frontend, check=True)
    subprocess.run([npm, "run", "build"], cwd=frontend, check=True)
    output = frontend / "out"
    if not (output / "index.html").is_file():
        raise RuntimeError("Next.js did not produce the planner's index.html")
    shutil.copytree(output, root / "web_static", dirs_exist_ok=True)
    print("Planner assets copied to web_static/ for FastAPI CDN promotion")


if __name__ == "__main__":
    main()
