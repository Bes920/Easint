#!/usr/bin/env bash
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/Bes920/Easint.git}"
TARGET_DIR="${TARGET_DIR:-Easint}"
BRANCH="${BRANCH:-}"
APP_ENTRY="${APP_ENTRY:-app.py}"
VENV_DIR="${VENV_DIR:-.venv}"

log() {
  printf '[install] %s\n' "$*"
}

have() {
  command -v "$1" >/dev/null 2>&1
}

ensure_python() {
  if have python3; then
    return
  fi

  log "python3 is missing; trying to install it with the available package manager."
  install_python_packages
}

install_system_packages() {
  if have apt-get; then
    sudo apt-get update
    sudo apt-get install -y git python3 python3-venv python3-pip exiftool
  elif have dnf; then
    sudo dnf install -y git python3 python3-pip perl-Image-ExifTool
  elif have yum; then
    sudo yum install -y git python3 python3-pip perl-Image-ExifTool
  elif have pacman; then
    sudo pacman -Sy --noconfirm git python python-pip perl-image-exiftool
  elif have brew; then
    brew update
    brew install git python exiftool
  else
    log "No supported package manager found."
    log "Install git, python3, pip, venv support, and exiftool manually, then rerun this script."
    exit 1
  fi
}

install_python_packages() {
  if have apt-get || have dnf || have yum || have pacman || have brew; then
    install_system_packages
  else
    log "python3 is required but could not be installed automatically."
    exit 1
  fi
}

ensure_exiftool() {
  if have exiftool; then
    return
  fi

  log "exiftool is missing; installing it now."
  if have apt-get; then
    sudo apt-get update
    sudo apt-get install -y exiftool
  elif have dnf; then
    sudo dnf install -y perl-Image-ExifTool
  elif have yum; then
    sudo yum install -y perl-Image-ExifTool
  elif have pacman; then
    sudo pacman -Sy --noconfirm perl-image-exiftool
  elif have brew; then
    brew install exiftool
  else
    log "Could not install exiftool automatically."
    log "Please install exiftool manually and rerun the script."
    exit 1
  fi
}

clone_repo() {
  if [ -d "$TARGET_DIR/.git" ]; then
    log "Repository already exists in $TARGET_DIR; skipping clone."
    return
  fi

  log "Cloning $REPO_URL into $TARGET_DIR"
  if [ -n "$BRANCH" ]; then
    git clone --branch "$BRANCH" --single-branch "$REPO_URL" "$TARGET_DIR"
  else
    git clone "$REPO_URL" "$TARGET_DIR"
  fi
}

install_python_deps() {
  cd "$TARGET_DIR"

  if [ ! -d "$VENV_DIR" ]; then
    log "Creating virtual environment in $VENV_DIR"
    python3 -m venv "$VENV_DIR"
  fi

  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
  log "Upgrading pip and installing Python dependencies"
  python -m pip install --upgrade pip
  python -m pip install -r requirements.txt
}

run_app() {
  cd "$TARGET_DIR"
  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
  log "Starting $APP_ENTRY"
  python "$APP_ENTRY"
}

main() {
  ensure_python
  ensure_exiftool
  clone_repo
  install_python_deps
  run_app
}

main "$@"
