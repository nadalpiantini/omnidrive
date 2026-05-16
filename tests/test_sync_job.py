"""Tests for the durable SyncJob in omnidrive.commands.sync."""
import json

import pytest

from omnidrive.commands.sync import (
    FileStatus,
    SyncJob,
    SyncState,
    _deserialize,
    _serialize,
)

# ── Fixtures ─────────────────────────────────────────────────────────────

@pytest.fixture
def state_dir(tmp_path):
    """Return a temporary state directory."""
    return str(tmp_path / "sync_jobs")


@pytest.fixture
def mock_files():
    """Return mock file listings for source and target."""
    source = [
        {"id": "s1", "name": "alpha.txt", "mimeType": "text/plain", "size": 100},
        {"id": "s2", "name": "beta.pdf", "mimeType": "application/pdf", "size": 200},
        {"id": "s3", "name": "gamma.jpg", "mimeType": "image/jpeg", "size": 300},
    ]
    target = [
        {"id": "t1", "name": "beta.pdf", "mimeType": "application/pdf", "size": 200},
    ]
    return source, target


def _make_get_files(source, target):
    """Return a callable that mimics _get_files_from_service."""
    calls = {"count": 0}

    def get_files(service, limit):
        calls["count"] += 1
        if service == "google":
            return source
        return target

    get_files.calls = calls
    return get_files


# ── Serialization round-trip ─────────────────────────────────────────────

class TestSerialization:
    def test_round_trip_empty(self):
        state = SyncState(job_id="abc", source="google", target="folderfort", limit=50)
        data = _serialize(state)
        restored = _deserialize(data)
        assert restored == state

    def test_round_trip_with_files(self):
        files = (
            FileStatus(name="a.txt", file_id="1", status="completed"),
            FileStatus(name="b.txt", file_id="2", status="failed", retries=3, error="boom"),
        )
        state = SyncState(job_id="xyz", source="google", target="folderfort", limit=10, files=files)
        data = _serialize(state)
        assert data["files"][1]["error"] == "boom"
        restored = _deserialize(data)
        assert restored.files[0].status == "completed"
        assert restored.files[1].retries == 3


# ── Save / Load ──────────────────────────────────────────────────────────

class TestPersistence:
    def test_save_creates_json_file(self, state_dir):
        job = SyncJob("google", "folderfort", state_dir=state_dir)
        path = job.save_state()
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["source"] == "google"
        assert data["target"] == "folderfort"

    def test_load_restores_state(self, state_dir):
        original = SyncJob("google", "folderfort", limit=42, state_dir=state_dir)
        original.save_state()

        loaded = SyncJob.load_state(original.job_id, state_dir)
        assert loaded.state.source == "google"
        assert loaded.state.limit == 42
        assert loaded.job_id == original.job_id

    def test_load_missing_raises(self, state_dir):
        with pytest.raises(FileNotFoundError):
            SyncJob.load_state("nonexistent", state_dir)

    def test_find_latest_job(self, state_dir):
        assert SyncJob.find_latest_job(state_dir) is None

        j1 = SyncJob("google", "folderfort", state_dir=state_dir)
        j1.save_state()
        assert SyncJob.find_latest_job(state_dir) == j1.job_id

        j2 = SyncJob("google", "folderfort", state_dir=state_dir)
        j2.save_state()
        assert SyncJob.find_latest_job(state_dir) == j2.job_id


# ── Run: dry-run mode ────────────────────────────────────────────────────

class TestDryRun:
    def test_dry_run_populates_files_without_syncing(self, state_dir, mock_files):
        source, target = mock_files
        sync_calls = []

        def mock_sync(file_data, src, tgt):
            sync_calls.append(file_data)

        job = SyncJob("google", "folderfort", state_dir=state_dir)
        final = job.run(
            dry_run=True,
            get_files=_make_get_files(source, target),
            sync_file=mock_sync,
        )

        assert final.dry_run is True
        assert len(final.files) == 2  # alpha.txt and gamma.jpg (beta already in target)
        assert all(f.status == "pending" for f in final.files)
        assert sync_calls == []  # nothing actually synced


# ── Run: normal mode ─────────────────────────────────────────────────────

class TestNormalRun:
    def test_syncs_all_files(self, state_dir, mock_files):
        source, target = mock_files
        synced = []

        def mock_sync(file_data, src, tgt):
            synced.append(file_data["name"])

        job = SyncJob("google", "folderfort", state_dir=state_dir)
        final = job.run(
            get_files=_make_get_files(source, target),
            sync_file=mock_sync,
        )

        assert len(final.files) == 2
        assert all(f.status == "completed" for f in final.files)
        assert set(synced) == {"alpha.txt", "gamma.jpg"}

    def test_already_in_sync(self, state_dir):
        files = [{"id": "1", "name": "same.txt"}]
        job = SyncJob("google", "folderfort", state_dir=state_dir)
        final = job.run(
            get_files=_make_get_files(files, files),
            sync_file=lambda *a: None,
        )
        assert len(final.files) == 0

    def test_state_persisted_after_run(self, state_dir, mock_files):
        source, target = mock_files
        job = SyncJob("google", "folderfort", state_dir=state_dir)
        job.run(
            get_files=_make_get_files(source, target),
            sync_file=lambda *a: None,
        )

        loaded = SyncJob.load_state(job.job_id, state_dir)
        assert len(loaded.state.files) == 2
        assert all(f.status == "completed" for f in loaded.state.files)


# ── Run: retry and failure ───────────────────────────────────────────────

class TestRetryAndFailure:
    def test_retries_on_transient_failure(self, state_dir, mock_files):
        source, target = mock_files
        attempt = {"n": 0}

        def flaky_sync(file_data, src, tgt):
            attempt["n"] += 1
            if file_data["name"] == "alpha.txt" and attempt["n"] <= 2:
                raise ConnectionError("transient")
            # succeeds on 3rd attempt for alpha, first try for gamma

        job = SyncJob("google", "folderfort", state_dir=state_dir)
        final = job.run(
            get_files=_make_get_files(source, target),
            sync_file=flaky_sync,
        )

        alpha = next(f for f in final.files if f.name == "alpha.txt")
        assert alpha.status == "completed"
        assert alpha.retries == 2  # failed twice, succeeded on 3rd

    def test_marks_failed_after_max_retries(self, state_dir, mock_files):
        source, target = mock_files

        def always_fail(file_data, src, tgt):
            raise RuntimeError("persistent error")

        job = SyncJob("google", "folderfort", state_dir=state_dir)
        final = job.run(
            get_files=_make_get_files(source, target),
            sync_file=always_fail,
        )

        assert all(f.status == "failed" for f in final.files)
        assert all(f.retries == 3 for f in final.files)
        assert all("persistent error" in f.error for f in final.files)


# ── Run: resume ──────────────────────────────────────────────────────────

class TestResume:
    def test_resume_skips_completed_files(self, state_dir, mock_files):
        source, target = mock_files
        synced = []

        def mock_sync(file_data, src, tgt):
            synced.append(file_data["name"])

        # First run: complete only alpha (simulate gamma failing)
        call_count = {"n": 0}

        def fail_gamma(file_data, src, tgt):
            call_count["n"] += 1
            if file_data["name"] == "gamma.jpg":
                raise RuntimeError("not now")
            synced.append(file_data["name"])

        job = SyncJob("google", "folderfort", state_dir=state_dir)
        final1 = job.run(
            get_files=_make_get_files(source, target),
            sync_file=fail_gamma,
        )

        assert final1.files[0].status == "completed"  # alpha
        assert final1.files[1].status == "failed"      # gamma
        assert "alpha.txt" in synced

        # Resume: load state, run again with working sync
        loaded = SyncJob.load_state(job.job_id, state_dir)
        final2 = loaded.run(
            dry_run=False,
            get_files=lambda s, l: source if s == "google" else target,
            sync_file=mock_sync,
        )

        assert all(f.status == "completed" for f in final2.files)
        # gamma should be synced now, alpha was already done
        assert "gamma.jpg" in synced


# ── CLI integration: --resume flag ───────────────────────────────────────

class TestSyncCLIResumeFlag:
    def test_sync_command_has_resume_option(self):
        from click.testing import CliRunner

        from omnidrive.cli import cli

        result = CliRunner().invoke(cli, ["sync", "--help"])
        assert result.exit_code == 0
        assert "--resume" in result.output

    def test_sync_resume_no_previous_job(self, state_dir, monkeypatch):
        from click.testing import CliRunner

        from omnidrive.cli import cli

        monkeypatch.setattr(
            "omnidrive.commands.sync.SyncJob.find_latest_job",
            classmethod(lambda cls, d=None: None),
        )

        result = CliRunner().invoke(cli, ["sync", "google", "folderfort", "--resume"])
        assert "No interrupted sync job found" in result.output
