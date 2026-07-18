import subprocess
from pathlib import Path

import pytest

SERVER_DIR = Path(__file__).resolve().parent.parent
IMAGE_TAG = "photo-server-scripts-import-check:test"


@pytest.mark.docker
def test_built_image_can_import_scripts_create_account():
    """Guards against server/Dockerfile silently dropping scripts/ again -
    see documentation/bugs/solved/2026-07-17-dockerfile-missing-scripts-directory-SOLVED.md."""
    subprocess.run(
        ["docker", "build", "-f", str(SERVER_DIR / "Dockerfile"), "-t", IMAGE_TAG, str(SERVER_DIR)],
        check=True,
    )
    try:
        result = subprocess.run(
            ["docker", "run", "--rm", IMAGE_TAG, "python", "-c", "import scripts.create_account"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
    finally:
        subprocess.run(["docker", "rmi", "-f", IMAGE_TAG], check=False)
