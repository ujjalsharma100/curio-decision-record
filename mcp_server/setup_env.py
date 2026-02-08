#!/usr/bin/env python3
"""
Setup script for Curio Decision Record MCP Server.

Creates a virtual environment and installs dependencies so the server
works without requiring global Python packages. Run this once after
downloading, then use the printed config in Cursor.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
VENV_DIR = ROOT / ".venv"
REQUIREMENTS = ROOT / "requirements.txt"
MAIN_PY = ROOT / "main.py"


def main():
    print("Setting up Curio Decision Record MCP Server...")
    print(f"  Root: {ROOT}")
    print(f"  Venv: {VENV_DIR}")

    # Create venv
    print("\n1. Creating virtual environment...")
    result = subprocess.run(
        [sys.executable, "-m", "venv", str(VENV_DIR)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"   Failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    print("   Done.")

    # Install dependencies
    if sys.platform == "win32":
        pip = VENV_DIR / "Scripts" / "pip.exe"
        python = VENV_DIR / "Scripts" / "python.exe"
    else:
        pip = VENV_DIR / "bin" / "pip"
        python = VENV_DIR / "bin" / "python"
    print("\n2. Installing dependencies...")
    result = subprocess.run(
        [str(pip), "install", "-r", str(REQUIREMENTS)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"   Failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)
    print("   Done.")

    # Print config
    config = {
        "mcpServers": {
            "curio-decision-record": {
                "command": str(python.absolute()),
                "args": [str(MAIN_PY)],
                "env": {
                    "CURIO_DECISION_SERVICE_URL": "http://localhost:5000"
                }
            }
        }
    }
    print("\n3. Setup complete!")
    print("\n" + "=" * 60)
    print("Add this to your Cursor MCP config (~/.cursor/mcp.json):")
    print("=" * 60)
    print(json.dumps(config, indent=2))
    print("=" * 60)
    print("\nThe 'command' points to the venv Python - no global deps needed.")
    print("Adjust CURIO_DECISION_SERVICE_URL if your service runs elsewhere.")


if __name__ == "__main__":
    main()
