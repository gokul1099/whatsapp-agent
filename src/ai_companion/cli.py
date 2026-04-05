import subprocess
import sys
from pathlib import Path

_ROOT = Path(__file__).parent.parent.parent


def run_ui():
    subprocess.run(
        ["streamlit", "run", str(_ROOT / "src/ai_companion/interfaces/streamlit/chat.py")]
        + sys.argv[1:],
        check=True,
    )


def run_server():
    subprocess.run(
        [
            "uvicorn",
            "ai_companion.interfaces.whatsapp.server:app",
            "--reload",
        ]
        + sys.argv[1:],
        check=True,
    )
