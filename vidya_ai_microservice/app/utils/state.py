"""Simple JSON-backed state tracking for duplicates and device usage."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional


class LocalStateStore:
    """Thread-safe helper persisting lightweight state to JSON files."""

    def __init__(self, path: Path):
        self.path = path
        self._lock = Lock()
        self._state: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if self.path.exists():
            try:
                self._state = json.loads(self.path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                self._state = {}
        else:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text("{}", encoding="utf-8")

    def _persist(self) -> None:
        self.path.write_text(json.dumps(self._state, indent=2), encoding="utf-8")

    def _applicants(self) -> Dict[str, Any]:
        return self._state.setdefault("applicants", {})

    def record_hash(self, applicant_id: str, evidence_id: str, hash_value: str, case_id: str) -> None:
        with self._lock:
            applicant = self._applicants().setdefault(applicant_id, {})
            hashes = applicant.setdefault("hashes", {})
            hashes[evidence_id] = {"hash": hash_value, "case_id": case_id}
            self._persist()

    def list_hashes(self, applicant_id: str) -> Dict[str, Dict[str, str]]:
        applicant = self._applicants().get(applicant_id, {})
        return applicant.get("hashes", {})  # type: ignore[return-value]

    def record_device_usage(self, device_id: Optional[str], timestamp: datetime, window_days: int = 7) -> int:
        if not device_id:
            return 0
        timestamp = timestamp.replace(tzinfo=None)
        with self._lock:
            devices = self._state.setdefault("devices", {})
            device_state = devices.setdefault(device_id, {"events": []})
            events: List[str] = device_state.setdefault("events", [])
            events.append(timestamp.isoformat())
            cutoff = timestamp - timedelta(days=window_days)
            device_state["events"] = [
                event for event in events if datetime.fromisoformat(event) >= cutoff
            ]
            self._persist()
            return len(device_state["events"])

    def record_case_timestamp(self, applicant_id: str, timestamp: str) -> List[str]:
        with self._lock:
            applicant = self._applicants().setdefault(applicant_id, {})
            history = applicant.setdefault("timestamps", [])
            history.append(timestamp)
            self._persist()
            return history


__all__ = ["LocalStateStore"]
