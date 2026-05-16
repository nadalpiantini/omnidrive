"""
F4-03 — Smoke E2E tests for OmniDrive CLI binary.

Runs the actual CLI via subprocess to verify the entry point, flag parsing,
and graceful error handling without network or real credentials.

All tests are marked @pytest.mark.e2e and use a 30-second timeout.
A temporary HOME is used so the real ~/.omnidrive is never touched.
"""
from __future__ import annotations

import os
import subprocess
import sys

import pytest

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CLI_CMD = [sys.executable, "-m", "omnidrive"]
TIMEOUT = 30


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def _isolated_home(tmp_path, monkeypatch):
    """Redirect HOME to a temp dir so we never touch ~/.omnidrive."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    # Also set XDG_CONFIG_HOME to avoid any system-level leaks
    monkeypatch.setenv("XDG_CONFIG_HOME", str(home / ".config"))
    # Disable any real network calls by ensuring no API keys
    monkeypatch.delenv("GOOGLE_APPLICATION_CREDENTIALS", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)
    monkeypatch.delenv("HF_TOKEN", raising=False)


def _run(args: list[str], stdin_data: str = "") -> subprocess.CompletedProcess[str]:
    """Run the CLI in a subprocess with captured output."""
    return subprocess.run(
        [*CLI_CMD, *args],
        capture_output=True,
        text=True,
        timeout=TIMEOUT,
        input=stdin_data,
        env=os.environ.copy(),  # inherits monkeypatched env
    )


# ===================================================================
# Test cases
# ===================================================================

@pytest.mark.e2e
@pytest.mark.timeout(TIMEOUT)
def test_help():
    """``omnidrive --help`` exits 0 and lists core commands."""
    r = _run(["--help"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    combined = r.stdout + r.stderr
    for keyword in ("list", "upload", "download", "sync", "search"):
        assert keyword in combined, f"Expected '{keyword}' in help output"


@pytest.mark.e2e
@pytest.mark.timeout(TIMEOUT)
def test_version():
    """``omnidrive --version`` exits 0 and shows version info."""
    r = _run(["--version"])
    assert r.returncode == 0, f"stderr: {r.stderr}"
    combined = r.stdout + r.stderr
    # Should contain either the program name or a version number pattern
    assert "omnidrive" in combined.lower() or "1.0.0" in combined, (
        f"Expected version info in output: {combined}"
    )


@pytest.mark.e2e
@pytest.mark.timeout(TIMEOUT)
def test_auth_status_runs():
    """``omnidrive auth google`` runs without crashing (prompts for creds)."""
    # The auth command is interactive (prompts for key path).
    # Sending empty stdin causes it to exit gracefully.
    r = _run(["auth", "google"], stdin_data="\n")
    assert r.returncode == 0, f"stderr: {r.stderr}"
    combined = r.stdout + r.stderr
    # Should mention authentication-related keywords
    assert any(
        kw in combined.lower() for kw in ("auth", "credential", "service account", "google")
    ), f"Expected auth-related output, got: {combined}"


@pytest.mark.e2e
@pytest.mark.timeout(TIMEOUT)
def test_list_unauthenticated_helpful_error():
    """``omnidrive list --drive google`` with no creds shows auth guidance."""
    # Send "n" to decline the interactive auth prompt
    r = _run(["list", "--drive", "google"], stdin_data="n\n")
    combined = r.stdout + r.stderr
    # The CLI should mention authentication in some form
    assert any(
        kw in combined.lower() for kw in ("auth", "authenticate", "not authenticated")
    ), f"Expected auth-related error message, got: {combined}"


@pytest.mark.e2e
@pytest.mark.timeout(TIMEOUT)
def test_search_empty_collection():
    """``omnidrive search 'nonexistent'`` exits without crashing.

    This command may attempt to load RAG models. We verify it doesn't
    hard-crash (exit code 0 or a handled error). If RAG deps are missing
    or network is unavailable, the CLI should handle it gracefully.
    """
    r = _run(["search", "nonexistent"])
    combined = r.stdout + r.stderr
    # Should not crash with a traceback (no "Traceback" in output)
    assert "Traceback" not in combined, (
        f"CLI crashed with traceback:\n{combined}"
    )
    # Exit code should be 0 (Click default — errors are caught internally)
    assert r.returncode == 0, f"Unexpected non-zero exit: {r.returncode}\n{combined}"


@pytest.mark.e2e
@pytest.mark.timeout(TIMEOUT)
def test_sync_dry_run():
    """``omnidrive sync google folderfort --dry-run --limit 1`` exits gracefully.

    Without real credentials the sync command will hit an auth error,
    but it should handle it gracefully (no traceback, exit 0).
    The test verifies the CLI parses flags correctly and runs the sync
    code path. When credentials are valid, output contains 'DRY RUN'.
    """
    r = _run(["sync", "google", "folderfort", "--dry-run", "--limit", "1"])
    combined = r.stdout + r.stderr
    # Should not crash with a traceback
    assert "Traceback" not in combined, (
        f"CLI crashed with traceback:\n{combined}"
    )
    # Exit code 0 (errors are caught internally by Click)
    assert r.returncode == 0, f"Unexpected non-zero exit: {r.returncode}\n{combined}"
    # If creds happen to be valid, we'd see DRY RUN; otherwise we see an error message
    # Either way, the command must not crash.
    has_dry_run = "DRY RUN" in combined
    has_error_msg = any(
        kw in combined.lower()
        for kw in ("error", "auth", "invalid_grant", "not authenticated")
    )
    assert has_dry_run or has_error_msg, (
        f"Expected 'DRY RUN' or an error message, got:\n{combined}"
    )
