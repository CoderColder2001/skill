#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_NAME="$(basename "$SCRIPT_DIR")"

CLIENT="trae"
SCOPE="global"
WORKSPACE_DIR=""
DEST_DIR=""
MODE="copy"
FORCE="0"

usage() {
  cat <<EOF
Usage: ./install.sh [options]

Options:
  --client trae|codex|generic   Target skill host. Default: trae
  --scope global|workspace      Install scope. Default: global
  --workspace PATH              Workspace root for workspace install
  --dest PATH                   Override target skills directory
  --mode copy|symlink           Install mode. Default: copy
  --force                       Replace existing installed skill
  -h, --help                    Show this help

Examples:
  ./install.sh --client trae --scope global
  ./install.sh --client trae --scope workspace --workspace /path/to/project
  ./install.sh --client codex --scope global
  ./install.sh --client codex --scope workspace --workspace /path/to/project
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --client)
      CLIENT="${2:?missing value for --client}"
      shift 2
      ;;
    --scope)
      SCOPE="${2:?missing value for --scope}"
      shift 2
      ;;
    --workspace)
      WORKSPACE_DIR="${2:?missing value for --workspace}"
      shift 2
      ;;
    --dest)
      DEST_DIR="${2:?missing value for --dest}"
      shift 2
      ;;
    --mode)
      MODE="${2:?missing value for --mode}"
      shift 2
      ;;
    --force)
      FORCE="1"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$CLIENT" in
  trae|codex|generic) ;;
  *)
    echo "Unsupported --client: $CLIENT" >&2
    exit 2
    ;;
esac

case "$SCOPE" in
  global|workspace) ;;
  *)
    echo "Unsupported --scope: $SCOPE" >&2
    exit 2
    ;;
esac

case "$MODE" in
  copy|symlink) ;;
  *)
    echo "Unsupported --mode: $MODE" >&2
    exit 2
    ;;
esac

default_global_dir() {
  case "$CLIENT" in
    trae)
      if [[ -n "${TRAE_SKILLS_DIR:-}" ]]; then
        printf '%s\n' "$TRAE_SKILLS_DIR"
      elif [[ -d "$HOME/.trae-cn/skills" ]]; then
        printf '%s\n' "$HOME/.trae-cn/skills"
      else
        printf '%s\n' "$HOME/.trae/skills"
      fi
      ;;
    codex)
      if [[ -n "${CODEX_SKILLS_DIR:-}" ]]; then
        printf '%s\n' "$CODEX_SKILLS_DIR"
      elif [[ -n "${CODEX_HOME:-}" ]]; then
        printf '%s\n' "$CODEX_HOME/skills"
      else
        printf '%s\n' "$HOME/.codex/skills"
      fi
      ;;
    generic)
      printf '%s\n' "${SKILLS_DIR:-$HOME/.agents/skills}"
      ;;
  esac
}

default_workspace_dir() {
  local root="$1"
  case "$CLIENT" in
    trae) printf '%s\n' "$root/.trae/skills" ;;
    codex) printf '%s\n' "$root/.codex/skills" ;;
    generic) printf '%s\n' "$root/skills" ;;
  esac
}

if [[ -z "$DEST_DIR" ]]; then
  if [[ "$SCOPE" == "global" ]]; then
    DEST_DIR="$(default_global_dir)"
  else
    if [[ -z "$WORKSPACE_DIR" ]]; then
      WORKSPACE_DIR="$(pwd)"
    fi
    WORKSPACE_DIR="$(cd "$WORKSPACE_DIR" && pwd)"
    DEST_DIR="$(default_workspace_dir "$WORKSPACE_DIR")"
  fi
fi

mkdir -p "$DEST_DIR"
DEST_DIR="$(cd "$DEST_DIR" && pwd)"
TARGET_DIR="$DEST_DIR/$SKILL_NAME"

if [[ "$TARGET_DIR" == "$SCRIPT_DIR" ]]; then
  echo "Refusing to install $SKILL_NAME onto its own source directory: $TARGET_DIR" >&2
  exit 1
fi

if [[ -e "$TARGET_DIR" || -L "$TARGET_DIR" ]]; then
  if [[ "$FORCE" != "1" ]]; then
    echo "Refusing to overwrite existing skill: $TARGET_DIR" >&2
    echo "Re-run with --force to replace it." >&2
    exit 1
  fi
  rm -rf "$TARGET_DIR"
fi

if [[ "$MODE" == "symlink" ]]; then
  ln -s "$SCRIPT_DIR" "$TARGET_DIR"
else
  if command -v rsync >/dev/null 2>&1; then
    rsync -a \
      --exclude '.git/' \
      --exclude '.pytest_cache/' \
      --exclude '__pycache__/' \
      --exclude '*.pyc' \
      "$SCRIPT_DIR/" "$TARGET_DIR/"
  else
    cp -R "$SCRIPT_DIR" "$TARGET_DIR"
  fi
fi

echo "Installed $SKILL_NAME to $TARGET_DIR"
