"""Durable sync job with state persistence and retry/backoff."""
from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable

MAX_RETRIES = 3
BACKOFF_BASE = 2.0  # seconds → delays of 2, 4, 8


@dataclass(frozen=True)
class FileStatus:
    name: str
    file_id: str
    status: str = "pending"  # pending | completed | failed
    retries: int = 0
    error: str = ""


@dataclass(frozen=True)
class SyncState:
    job_id: str
    source: str
    target: str
    limit: int
    files: tuple[FileStatus, ...] = ()
    dry_run: bool = False


def _serialize(state: SyncState) -> dict[str, Any]:
    return {
        "job_id": state.job_id,
        "source": state.source,
        "target": state.target,
        "limit": state.limit,
        "dry_run": state.dry_run,
        "files": [asdict(f) for f in state.files],
    }


def _deserialize(data: dict[str, Any]) -> SyncState:
    files = tuple(FileStatus(**f) for f in data.get("files", []))
    return SyncState(
        job_id=data["job_id"], source=data["source"], target=data["target"],
        limit=data["limit"], dry_run=data.get("dry_run", False), files=files,
    )


def _state_path(state_dir: Path, job_id: str) -> Path:
    return state_dir / f"{job_id}.json"


class SyncJob:
    """A durable, resumable sync operation between two drives."""

    def __init__(self, source: str, target: str, limit: int = 100,
                 state_dir: str = "~/.omnidrive/sync_jobs") -> None:
        self._state_dir = Path(os.path.expanduser(state_dir))
        self._state_dir.mkdir(parents=True, exist_ok=True)
        self._state = SyncState(job_id=uuid.uuid4().hex[:12], source=source,
                                target=target, limit=limit)

    @property
    def job_id(self) -> str:
        return self._state.job_id

    @property
    def state(self) -> SyncState:
        return self._state

    # ── Persistence ──────────────────────────────────────────────────

    def save_state(self) -> Path:
        """Write current state to disk (atomic via tmp+rename)."""
        path = _state_path(self._state_dir, self._state.job_id)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(_serialize(self._state), indent=2))
        tmp.replace(path)
        return path

    @classmethod
    def load_state(cls, job_id: str, state_dir: str = "~/.omnidrive/sync_jobs") -> SyncJob:
        """Restore from a previously saved state file."""
        sdir = Path(os.path.expanduser(state_dir))
        data = json.loads(_state_path(sdir, job_id).read_text())
        loaded = _deserialize(data)
        job = cls.__new__(cls)
        job._state_dir = sdir
        job._state_dir.mkdir(parents=True, exist_ok=True)
        job._state = loaded
        return job

    @classmethod
    def find_latest_job(cls, state_dir: str = "~/.omnidrive/sync_jobs") -> str | None:
        """Return the job_id of the most recently modified state file, or None."""
        sdir = Path(os.path.expanduser(state_dir))
        if not sdir.exists():
            return None
        files = sorted(sdir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        return files[0].stem if files else None

    # ── Immutable state transitions ──────────────────────────────────

    def _clone(self, **overrides: Any) -> SyncJob:
        """Return a new SyncJob with merged state fields."""
        merged = {**asdict(self._state), **overrides}
        # asdict converts FileStatus to dicts — restore them
        if "files" in merged and not isinstance(merged["files"], tuple):
            merged["files"] = tuple(merged["files"])
        if merged.get("files") and not isinstance(merged["files"][0], FileStatus):
            merged["files"] = tuple(FileStatus(**f) if isinstance(f, dict) else f
                                    for f in merged["files"])
        new_state = SyncState(**merged)
        job = SyncJob.__new__(SyncJob)
        job._state_dir = self._state_dir
        job._state = new_state
        return job

    def _update_file(self, index: int, **overrides: Any) -> SyncJob:
        old = self._state.files[index]
        new_f = FileStatus(**{**asdict(old), **overrides})
        files = tuple(new_f if i == index else f for i, f in enumerate(self._state.files))
        return self._clone(files=files)

    # ── Execution ────────────────────────────────────────────────────

    def run(self, dry_run: bool = False,
            get_files: Callable | None = None,
            sync_file: Callable | None = None) -> SyncState:
        """Execute the sync.  Returns the final immutable state."""
        if get_files is None:
            from omnidrive.cli import _get_files_from_service as get_files
        if sync_file is None:
            from omnidrive.cli import _sync_file as sync_file

        self = self._clone(dry_run=dry_run)

        # Populate files on first run (skip when resuming)
        if not self._state.files:
            src = get_files(self._state.source, self._state.limit)
            tgt = get_files(self._state.target, self._state.limit)
            tgt_names = {f.get("name") for f in tgt}
            statuses = tuple(
                FileStatus(name=f.get("name", ""), file_id=f.get("id", ""))
                for f in src if f.get("name") not in tgt_names
            )
            self = self._clone(files=statuses)
            self.save_state()

        if dry_run or not self._state.files:
            return self._state

        # Sync each pending file with exponential backoff
        for idx, fs in enumerate(self._state.files):
            if fs.status == "completed":
                continue
            file_data = {"id": fs.file_id, "name": fs.name}
            last_err = ""
            for attempt in range(MAX_RETRIES):
                try:
                    sync_file(file_data, self._state.source, self._state.target)
                    self = self._update_file(idx, status="completed", retries=attempt, error="")
                    break
                except Exception as exc:  # noqa: BLE001
                    last_err = str(exc)
                    if attempt < MAX_RETRIES - 1:
                        time.sleep(BACKOFF_BASE ** (attempt + 1))
            if self._state.files[idx].status != "completed":
                self = self._update_file(idx, status="failed", retries=MAX_RETRIES, error=last_err)
            self.save_state()

        return self._state
