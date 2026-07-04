#!/usr/bin/env python3
"""Clone, install, and launch the EASINT app."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


DEFAULT_REPO_URL = "https://github.com/Bes920/Easint.git"
DEFAULT_TARGET_DIR = "Easint"
DEFAULT_VENV_DIR = ".venv"
DEFAULT_APP_ENTRY = "app.py"


def log(message: str) -> None:
    print(f"[install] {message}", flush=True)


def have(command: str) -> bool:
    return shutil.which(command) is not None


def run(cmd: list[str], cwd: Path | None = None) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def install_system_packages() -> None:
    if have("apt-get"):
        run(["sudo", "apt-get", "update"])
        run(["sudo", "apt-get", "install", "-y", "git", "python3", "python3-venv", "python3-pip", "exiftool"])
    elif have("dnf"):
        run(["sudo", "dnf", "install", "-y", "git", "python3", "python3-pip", "perl-Image-ExifTool"])
    elif have("yum"):
        run(["sudo", "yum", "install", "-y", "git", "python3", "python3-pip", "perl-Image-ExifTool"])
    elif have("pacman"):
        run(["sudo", "pacman", "-Sy", "--noconfirm", "git", "python", "python-pip", "perl-image-exiftool"])
    elif have("brew"):
        run(["brew", "update"])
        run(["brew", "install", "git", "python", "exiftool"])
    else:
        raise RuntimeError(
            "No supported package manager found. Install git, Python 3, pip, venv support, and exiftool manually."
        )


def ensure_python() -> None:
    if have("python3"):
        return
    log("python3 is missing; trying to install it.")
    install_system_packages()


def ensure_exiftool() -> None:
    if have("exiftool"):
        return
    log("exiftool is missing; installing it.")
    if have("apt-get"):
        run(["sudo", "apt-get", "update"])
        run(["sudo", "apt-get", "install", "-y", "exiftool"])
    elif have("dnf"):
        run(["sudo", "dnf", "install", "-y", "perl-Image-ExifTool"])
    elif have("yum"):
        run(["sudo", "yum", "install", "-y", "perl-Image-ExifTool"])
    elif have("pacman"):
        run(["sudo", "pacman", "-Sy", "--noconfirm", "perl-image-exiftool"])
    elif have("brew"):
        run(["brew", "install", "exiftool"])
    else:
        raise RuntimeError("Could not install exiftool automatically.")


def clone_repo(repo_url: str, target_dir: Path, branch: str | None) -> None:
    if (target_dir / ".git").exists():
        log(f"Repository already exists in {target_dir}; skipping clone.")
        return

    log(f"Cloning {repo_url} into {target_dir}")
    cmd = ["git", "clone"]
    if branch:
        cmd.extend(["--branch", branch, "--single-branch"])
    cmd.extend([repo_url, str(target_dir)])
    run(cmd)


def create_venv(venv_dir: Path, project_dir: Path) -> None:
    if venv_dir.exists():
        return
    log(f"Creating virtual environment in {venv_dir}")
    run(["python3", "-m", "venv", str(venv_dir)], cwd=project_dir)


def pip_install(project_dir: Path, venv_dir: Path) -> None:
    pip_path = venv_dir / "bin" / "pip"
    if not pip_path.exists():
        raise RuntimeError(f"pip not found at {pip_path}")

    log("Upgrading pip and installing Python dependencies")
    run([str(pip_path), "install", "--upgrade", "pip"], cwd=project_dir)
    run([str(pip_path), "install", "-r", "requirements.txt"], cwd=project_dir)


def run_app(project_dir: Path, venv_dir: Path, app_entry: str) -> None:
    python_path = venv_dir / "bin" / "python"
    if not python_path.exists():
        raise RuntimeError(f"python not found at {python_path}")

    log(f"Starting {app_entry}")
    os.execv(str(python_path), [str(python_path), app_entry])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Clone, install, and run the EASINT app.")
    parser.add_argument("--repo", default=os.environ.get("REPO_URL", DEFAULT_REPO_URL))
    parser.add_argument("--dir", default=os.environ.get("TARGET_DIR", DEFAULT_TARGET_DIR))
    parser.add_argument("--branch", default=os.environ.get("BRANCH") or None)
    parser.add_argument("--venv", default=os.environ.get("VENV_DIR", DEFAULT_VENV_DIR))
    parser.add_argument("--app", default=os.environ.get("APP_ENTRY", DEFAULT_APP_ENTRY))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_python()
    ensure_exiftool()

    project_dir = Path(args.dir).expanduser().resolve()
    clone_repo(args.repo, project_dir, args.branch)
    create_venv(project_dir / args.venv, project_dir)
    pip_install(project_dir, project_dir / args.venv)
    run_app(project_dir, project_dir / args.venv, args.app)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        print(f"[install] Command failed: {exc}", file=sys.stderr)
        raise SystemExit(exc.returncode) from exc
    except Exception as exc:
        print(f"[install] {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
