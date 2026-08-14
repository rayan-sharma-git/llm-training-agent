"""
Copies the Python backend into the extension folder so that
`vsce package` produces a self-contained .vsix.

The extension's BackendManager looks for backend/main.py:
  1. inside the extension folder (packaged .vsix)
  2. next to the extension folder (dev checkout)

Run this BEFORE `vsce package` / `npm run package`.
"""
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
BACKEND_SRC = REPO_ROOT / "PROJECT_TEMPLATE" / "backend"
EXTENSION_DIR = REPO_ROOT / "PROJECT_TEMPLATE" / "extension"
BACKEND_DEST = EXTENSION_DIR / "backend"

EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", "tests"}


def main() -> None:
    if not BACKEND_SRC.exists():
        raise SystemExit(f"Backend source not found: {BACKEND_SRC}")

    print(f"Copying backend:\n  {BACKEND_SRC}\n  -> {BACKEND_DEST}")
    if BACKEND_DEST.exists():
        shutil.rmtree(BACKEND_DEST)

    shutil.copytree(
        BACKEND_SRC,
        BACKEND_DEST,
        ignore=shutil.ignore_patterns(*EXCLUDE_DIRS),
    )
    print("Backend copied into extension folder. Ready for `vsce package`.")


if __name__ == "__main__":
    main()