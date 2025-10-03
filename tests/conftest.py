"""Pytest configuration for all tests."""
import os
from pathlib import Path

import pytest


def pytest_configure(config):
    """Load .env file before running tests."""
    # Load .env if exists (for E2E tests with real API keys)
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    key, _, value = line.partition("=")
                    os.environ[key.strip()] = value.strip()

    # Register custom markers
    config.addinivalue_line(
        "markers", "e2e: marks tests as E2E (requires real API keys)"
    )
    config.addinivalue_line(
        "markers", "slow: marks tests as slow running"
    )
