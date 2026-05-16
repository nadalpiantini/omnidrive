"""Project-wide pytest fixtures.

Defensive isolation: every test gets a tmp HOME so no test can leak state
into the developer's real ~/.omnidrive (sync_jobs/, oauth/, vector_db/, etc).

Discovered 2026-05-15 stress-testing F3-03: SyncJob defaults state_dir to
"~/.omnidrive/sync_jobs", and tests in test_cli_integration.py invoke the
real CLI in-process via Click's CliRunner without HOME isolation, so dry-run
sync produced 21 stale .json files in the user's home before this fixture.
"""
from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _isolated_home(tmp_path, monkeypatch):
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))
    yield home
