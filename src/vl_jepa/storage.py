"""
SPEC: S009 - Storage and Crash Recovery

Persistent storage for embeddings and metadata with crash recovery.
"""

from __future__ import annotations

import logging
import shutil
import sqlite3
from pathlib import Path
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


class Storage:
    """Persistent storage for embeddings and metadata.

    IMPLEMENTS: S009
    INVARIANTS: INV015, INV016

    Features:
    - Atomic writes (temp + rename)
    - Automatic backup creation
    - Crash recovery from temp/backup files
    - SQLite with WAL mode for metadata

    Example:
        storage = Storage(Path("lecture_001"))
        storage.save_embeddings(embeddings)
        storage.save_metadata({"title": "Lecture 1"})
    """

    EMBEDDINGS_FILE = "embeddings.npy"
    EMBEDDINGS_TEMP = "embeddings.npy.tmp"
    EMBEDDINGS_BACKUP = "embeddings.npy.bak"
    METADATA_DB = "metadata.db"
    BACKUP_THRESHOLD = 100  # Create backup every N embeddings

    def __init__(self, directory: Path) -> None:
        """Initialize storage in directory.

        INVARIANT: INV016 - SQLite WAL mode enabled

        Args:
            directory: Directory to store data
        """
        self._directory = Path(directory)
        self._directory.mkdir(parents=True, exist_ok=True)

        # Attempt crash recovery
        self._recover_if_needed()

        # Initialize SQLite with WAL mode
        self._init_database()

    def _init_database(self) -> None:
        """Initialize SQLite database with WAL mode.

        INVARIANT: INV016
        """
        db_path = self._directory / self.METADATA_DB
        conn = sqlite3.connect(db_path)

        # Enable WAL mode (INV016)
        conn.execute("PRAGMA journal_mode=WAL")

        # Create tables
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                timestamp REAL,
                confidence REAL,
                summary TEXT
            )
        """
        )

        conn.commit()
        conn.close()

    def _recover_if_needed(self) -> None:
        """Attempt recovery from crash state.

        INVARIANT: INV016 - Recover from temp/backup files
        EDGE_CASE: EC043
        """
        embeddings_path = self._directory / self.EMBEDDINGS_FILE
        temp_path = self._directory / self.EMBEDDINGS_TEMP
        temp_path_new = self._directory / "embeddings_temp.npy"
        backup_path = self._directory / self.EMBEDDINGS_BACKUP

        # Check both old and new temp file patterns
        actual_temp = None
        if temp_path.exists():
            actual_temp = temp_path
        elif temp_path_new.exists():
            actual_temp = temp_path_new

        # Case 1: Temp file exists but final doesn't - crashed during write
        if actual_temp and not embeddings_path.exists():
            logger.warning("Recovering from temp file")
            shutil.move(actual_temp, embeddings_path)

        # Case 2: Both temp and final exist - crashed after write before cleanup
        elif actual_temp and embeddings_path.exists():
            logger.warning("Removing orphaned temp file")
            actual_temp.unlink()

        # Case 3: Only backup exists - use backup
        elif backup_path.exists() and not embeddings_path.exists():
            logger.warning("Recovering from backup file")
            shutil.copy(backup_path, embeddings_path)

    def save_embeddings(
        self,
        embeddings: np.ndarray,
        create_backup: bool = True,
    ) -> None:
        """Save embeddings atomically.

        INVARIANT: INV015 - Atomic write (temp + rename)

        Args:
            embeddings: Embeddings array (N, 768)
            create_backup: Whether to create backup of existing file
        """
        embeddings_path = self._directory / self.EMBEDDINGS_FILE
        # np.save adds .npy if not present, so use path without extension for temp
        temp_base = self._directory / "embeddings_temp"
        temp_path_with_ext = self._directory / "embeddings_temp.npy"
        backup_path = self._directory / self.EMBEDDINGS_BACKUP

        # Create backup if threshold reached
        if create_backup and embeddings_path.exists():
            existing = np.load(embeddings_path)
            if len(embeddings) - len(existing) >= self.BACKUP_THRESHOLD:
                shutil.copy(embeddings_path, backup_path)
                logger.info("Created backup file")

        # Atomic write: save to temp, then rename
        # np.save automatically adds .npy extension
        np.save(temp_base, embeddings)

        # Rename (atomic on POSIX, best-effort on Windows)
        shutil.move(temp_path_with_ext, embeddings_path)

        logger.debug(f"Saved {len(embeddings)} embeddings")

    def load_embeddings(self) -> np.ndarray | None:
        """Load embeddings from storage.

        Returns:
            Embeddings array or None if not found
        """
        embeddings_path = self._directory / self.EMBEDDINGS_FILE

        if not embeddings_path.exists():
            return None

        result: np.ndarray = np.load(embeddings_path)
        return result

    def append_embeddings(self, new_embeddings: np.ndarray) -> None:
        """Append new embeddings to existing.

        Args:
            new_embeddings: New embeddings to append
        """
        existing = self.load_embeddings()

        if existing is None:
            self.save_embeddings(new_embeddings)
        else:
            combined = np.concatenate([existing, new_embeddings], axis=0)
            self.save_embeddings(combined)

    def save_event(
        self,
        timestamp: float,
        confidence: float,
        summary: str,
    ) -> int:
        """Save an event to the database.

        Args:
            timestamp: Event timestamp in seconds
            confidence: Detection confidence [0, 1]
            summary: Generated summary text

        Returns:
            Event ID
        """
        db_path = self._directory / self.METADATA_DB
        conn = sqlite3.connect(db_path)

        cursor = conn.execute(
            "INSERT INTO events (timestamp, confidence, summary) VALUES (?, ?, ?)",
            (timestamp, confidence, summary),
        )

        event_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return event_id if event_id else 0

    def get_events(self) -> list[dict[str, Any]]:
        """Get all events from database.

        Returns:
            List of event dictionaries
        """
        db_path = self._directory / self.METADATA_DB
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row

        cursor = conn.execute(
            "SELECT id, timestamp, confidence, summary FROM events ORDER BY timestamp"
        )

        events = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return events

    def set_metadata(self, key: str, value: str) -> None:
        """Set a metadata value.

        Args:
            key: Metadata key
            value: Metadata value
        """
        db_path = self._directory / self.METADATA_DB
        conn = sqlite3.connect(db_path)

        conn.execute(
            "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
            (key, value),
        )

        conn.commit()
        conn.close()

    def get_metadata(self, key: str) -> str | None:
        """Get a metadata value.

        Args:
            key: Metadata key

        Returns:
            Value or None if not found
        """
        db_path = self._directory / self.METADATA_DB
        conn = sqlite3.connect(db_path)

        cursor = conn.execute("SELECT value FROM metadata WHERE key = ?", (key,))
        row = cursor.fetchone()
        conn.close()

        return row[0] if row else None
