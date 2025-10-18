#!/usr/bin/env python3
"""
Development Scripts for SSH Honeypot
"""

import subprocess
import sys


def run_tests():
    """Run all tests"""
    print("Running tests...")
    subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])


def run_linting():
    """Run linting checks"""
    print("Running linting...")
    subprocess.run([sys.executable, "-m", "ruff", "check", "."])
    subprocess.run([sys.executable, "-m", "black", "--check", "."])


def run_security_check():
    """Run security checks"""
    print("Running security checks...")
    subprocess.run([sys.executable, "-m", "bandit", "-r", "ssh_honeypot/"])


def clean_project():
    """Clean project files"""
    print("Cleaning project...")
    # Remove __pycache__ directories
    subprocess.run(
        [
            "find",
            ".",
            "-type",
            "d",
            "-name",
            "__pycache__",
            "-exec",
            "rm",
            "-rf",
            "{}",
            "+",
        ]
    )
    # Remove .pyc files
    subprocess.run(["find", ".", "-name", "*.pyc", "-delete"])


def install_deps():
    """Install dependencies"""
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    subprocess.run(
        [sys.executable, "-m", "pip", "install", "-r", "requirements-dev.txt"]
    )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/dev.py [test|lint|security|clean|install]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "test":
        run_tests()
    elif command == "lint":
        run_linting()
    elif command == "security":
        run_security_check()
    elif command == "clean":
        clean_project()
    elif command == "install":
        install_deps()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
