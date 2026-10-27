"""Thread-safe WhatsApp pairing state shared by Neonize and the web API."""

from __future__ import annotations

import io
import threading
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import segno


@dataclass(frozen=True)
class PairingSnapshot:
    status: str
    qr_png: bytes | None
    updated_at: str | None
    error: str | None


class PairingState:
    def __init__(self, qr_output_path: Path | None = None) -> None:
        self._lock = threading.RLock()
        self._qr_output_path = qr_output_path
        self._status = "starting"
        self._qr_png: bytes | None = None
        self._updated_at: str | None = None
        self._error: str | None = None

    def set_qr(self, raw_code: bytes) -> None:
        image = io.BytesIO()
        segno.make_qr(raw_code).save(image, kind="png", scale=8, border=3)
        qr_png = image.getvalue()
        with self._lock:
            self._status = "awaiting_scan"
            self._qr_png = qr_png
            self._updated_at = datetime.now(timezone.utc).isoformat()
            self._error = None
            if self._qr_output_path is not None:
                self._qr_output_path.parent.mkdir(parents=True, exist_ok=True)
                self._qr_output_path.write_bytes(qr_png)
                self._qr_output_path.chmod(0o600)

    def set_connected(self) -> None:
        with self._lock:
            self._status = "connected"
            self._qr_png = None
            self._updated_at = datetime.now(timezone.utc).isoformat()
            self._error = None
            self._remove_qr_file()

    def set_disconnected(self) -> None:
        with self._lock:
            self._status = "disconnected"
            self._updated_at = datetime.now(timezone.utc).isoformat()

    def set_error(self, message: str) -> None:
        with self._lock:
            self._status = "error"
            self._error = message
            self._updated_at = datetime.now(timezone.utc).isoformat()

    def _remove_qr_file(self) -> None:
        if self._qr_output_path is not None:
            self._qr_output_path.unlink(missing_ok=True)

    def snapshot(self) -> PairingSnapshot:
        with self._lock:
            return PairingSnapshot(
                status=self._status,
                qr_png=self._qr_png,
                updated_at=self._updated_at,
                error=self._error,
            )
