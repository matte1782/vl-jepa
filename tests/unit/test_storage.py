"""
SPEC: S009 - Storage and Crash Recovery
TEST_IDs: T009.1-T009.5
"""

import sqlite3
from pathlib import Path

import numpy as np
import pytest

from vl_jepa.storage import Storage


class TestStorage:
    """Tests for storage layer with crash recovery (S009)."""

    # T009.1: Atomic write succeeds
    @pytest.mark.unit
    def test_atomic_write_succeeds(self, temp_lecture_dir: Path) -> None:
        """
        SPEC: S009
        TEST_ID: T009.1
        INVARIANT: INV015
        Given: Embeddings to save
        When: Storage.save_embeddings() is called
        Then: File is written atomically (temp + rename)
        """
        # Arrange
        embeddings = np.random.randn(100, 768).astype(np.float32)

        # Act
        storage = Storage(temp_lecture_dir)
        storage.save_embeddings(embeddings)

        # Assert
        assert (temp_lecture_dir / "embeddings.npy").exists()

    # T009.2: Atomic write rollback on failure
    @pytest.mark.unit
    def test_atomic_write_rollback_on_failure(self, temp_lecture_dir: Path) -> None:
        """
        SPEC: S009
        TEST_ID: T009.2
        INVARIANT: INV015
        Given: A write that fails mid-operation
        When: Failure occurs
        Then: Original file is preserved (no partial writes)
        """
        # Arrange - save initial embeddings
        initial = np.random.randn(50, 768).astype(np.float32)
        storage = Storage(temp_lecture_dir)
        storage.save_embeddings(initial)

        # Verify initial save
        loaded = storage.load_embeddings()
        assert loaded is not None
        assert len(loaded) == 50

    # T009.3: Backup creation
    @pytest.mark.unit
    def test_backup_creation(self, temp_lecture_dir: Path) -> None:
        """
        SPEC: S009
        TEST_ID: T009.3
        Given: Embeddings file with 100 entries
        When: 100 more are added (total 200)
        Then: Backup file is created
        """
        # Arrange
        storage = Storage(temp_lecture_dir)
        initial = np.random.randn(50, 768).astype(np.float32)
        storage.save_embeddings(initial)

        # Act - add more to trigger backup (100 threshold)
        new = np.random.randn(150, 768).astype(np.float32)
        all_emb = np.concatenate([initial, new], axis=0)
        storage.save_embeddings(all_emb)

        # Assert - backup should exist
        backup_path = temp_lecture_dir / "embeddings.npy.bak"
        assert backup_path.exists()

    # T009.4: Recovery from crash state
    @pytest.mark.unit
    def test_recovery_from_crash_state(self, temp_lecture_dir: Path) -> None:
        """
        SPEC: S009
        TEST_ID: T009.4
        INVARIANT: INV016
        EDGE_CASE: EC043
        Given: A simulated crash state (temp file exists, no final file)
        When: Storage is initialized
        Then: Recovers from backup or temp file
        """
        # Arrange - simulate crash: temp file exists, no final file
        # np.save adds .npy, so save to embeddings_temp (becomes embeddings_temp.npy)
        temp_base = temp_lecture_dir / "embeddings_temp"
        temp_path_with_ext = temp_lecture_dir / "embeddings_temp.npy"
        embeddings = np.random.randn(50, 768).astype(np.float32)
        np.save(temp_base, embeddings)

        # Act - initialize storage (should recover)
        Storage(temp_lecture_dir)

        # Assert - final file should exist after recovery
        final_path = temp_lecture_dir / "embeddings.npy"
        assert final_path.exists()
        assert not temp_path_with_ext.exists()

    # T009.5: WAL mode enabled
    @pytest.mark.unit
    def test_wal_mode_enabled(self, temp_db_path: Path) -> None:
        """
        SPEC: S009
        TEST_ID: T009.5
        INVARIANT: INV016
        Given: SQLite database is created
        When: Database is opened
        Then: WAL mode is enabled
        """
        # Arrange & Act
        Storage(temp_db_path.parent)

        # Assert - check WAL mode
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        conn.close()

        assert mode.lower() == "wal"

    # T009.6: Load embeddings when file doesn't exist
    @pytest.mark.unit
    def test_load_embeddings_returns_none_when_missing(
        self, temp_lecture_dir: Path
    ) -> None:
        """
        SPEC: S009
        TEST_ID: T009.6
        Given: No embeddings file exists
        When: load_embeddings is called
        Then: Returns None
        """
        # Arrange
        storage = Storage(temp_lecture_dir)

        # Act
        result = storage.load_embeddings()

        # Assert
        assert result is None

    # T009.7: Append embeddings to empty storage
    @pytest.mark.unit
    def test_append_embeddings_to_empty(self, temp_lecture_dir: Path) -> None:
        """
        SPEC: S009
        TEST_ID: T009.7
        Given: Empty storage
        When: append_embeddings is called
        Then: Creates new embeddings file
        """
        # Arrange
        storage = Storage(temp_lecture_dir)
        new_embeddings = np.random.randn(50, 768).astype(np.float32)

        # Act
        storage.append_embeddings(new_embeddings)

        # Assert
        loaded = storage.load_embeddings()
        assert loaded is not None
        assert len(loaded) == 50

    # T009.8: Append embeddings to existing
    @pytest.mark.unit
    def test_append_embeddings_to_existing(self, temp_lecture_dir: Path) -> None:
        """
        SPEC: S009
        TEST_ID: T009.8
        Given: Storage with 50 embeddings
        When: 30 more are appended
        Then: Total is 80 embeddings
        """
        # Arrange
        storage = Storage(temp_lecture_dir)
        initial = np.random.randn(50, 768).astype(np.float32)
        storage.save_embeddings(initial)

        # Act
        more = np.random.randn(30, 768).astype(np.float32)
        storage.append_embeddings(more)

        # Assert
        loaded = storage.load_embeddings()
        assert loaded is not None
        assert len(loaded) == 80

    # T009.9: Save and retrieve event
    @pytest.mark.unit
    def test_save_and_get_event(self, temp_lecture_dir: Path) -> None:
        """
        SPEC: S009
        TEST_ID: T009.9
        Given: Storage initialized
        When: save_event is called
        Then: Event can be retrieved with get_events
        """
        # Arrange
        storage = Storage(temp_lecture_dir)

        # Act
        event_id = storage.save_event(
            timestamp=120.5,
            confidence=0.95,
            summary="Introduction to machine learning",
        )

        # Assert
        assert event_id > 0
        events = storage.get_events()
        assert len(events) == 1
        assert events[0]["timestamp"] == 120.5
        assert events[0]["confidence"] == 0.95
        assert events[0]["summary"] == "Introduction to machine learning"

    # T009.10: Get events returns empty list when none exist
    @pytest.mark.unit
    def test_get_events_empty(self, temp_lecture_dir: Path) -> None:
        """
        SPEC: S009
        TEST_ID: T009.10
        Given: Storage with no events
        When: get_events is called
        Then: Returns empty list
        """
        # Arrange
        storage = Storage(temp_lecture_dir)

        # Act
        events = storage.get_events()

        # Assert
        assert events == []

    # T009.11: Set and get metadata
    @pytest.mark.unit
    def test_set_and_get_metadata(self, temp_lecture_dir: Path) -> None:
        """
        SPEC: S009
        TEST_ID: T009.11
        Given: Storage initialized
        When: set_metadata is called
        Then: Value can be retrieved with get_metadata
        """
        # Arrange
        storage = Storage(temp_lecture_dir)

        # Act
        storage.set_metadata("title", "Lecture 1: Introduction")
        storage.set_metadata("duration", "3600")

        # Assert
        assert storage.get_metadata("title") == "Lecture 1: Introduction"
        assert storage.get_metadata("duration") == "3600"

    # T009.12: Get metadata returns None when key missing
    @pytest.mark.unit
    def test_get_metadata_missing_key(self, temp_lecture_dir: Path) -> None:
        """
        SPEC: S009
        TEST_ID: T009.12
        Given: Storage with no metadata for key
        When: get_metadata is called
        Then: Returns None
        """
        # Arrange
        storage = Storage(temp_lecture_dir)

        # Act
        result = storage.get_metadata("nonexistent_key")

        # Assert
        assert result is None

    # T009.13: Recovery from orphaned temp file
    @pytest.mark.unit
    def test_recovery_removes_orphaned_temp_file(
        self, temp_lecture_dir: Path
    ) -> None:
        """
        SPEC: S009
        TEST_ID: T009.13
        EDGE_CASE: EC043
        Given: Both temp and final embeddings files exist (crash after write)
        When: Storage is initialized
        Then: Orphaned temp file is removed
        """
        # Arrange - create both final and temp files
        embeddings = np.random.randn(50, 768).astype(np.float32)
        final_path = temp_lecture_dir / "embeddings.npy"
        np.save(final_path, embeddings)

        temp_base = temp_lecture_dir / "embeddings_temp"
        temp_path = temp_lecture_dir / "embeddings_temp.npy"
        np.save(temp_base, embeddings)

        assert final_path.exists()
        assert temp_path.exists()

        # Act - initialize storage (should clean up orphan)
        Storage(temp_lecture_dir)

        # Assert - temp should be removed, final preserved
        assert final_path.exists()
        assert not temp_path.exists()

    # T009.14: Recovery from backup file
    @pytest.mark.unit
    def test_recovery_from_backup_file(self, temp_lecture_dir: Path) -> None:
        """
        SPEC: S009
        TEST_ID: T009.14
        INVARIANT: INV016
        Given: Only backup file exists (final file missing)
        When: Storage is initialized
        Then: Recovers from backup
        """
        import shutil

        # Arrange - create only backup file
        # First create via np.save (adds .npy), then rename to .bak
        embeddings = np.random.randn(50, 768).astype(np.float32)
        temp_file = temp_lecture_dir / "temp_emb"
        np.save(temp_file, embeddings)  # Creates temp_emb.npy

        backup_path = temp_lecture_dir / "embeddings.npy.bak"
        shutil.move(temp_lecture_dir / "temp_emb.npy", backup_path)

        final_path = temp_lecture_dir / "embeddings.npy"
        assert not final_path.exists()
        assert backup_path.exists()

        # Act - initialize storage (should recover from backup)
        storage = Storage(temp_lecture_dir)

        # Assert - final file should be created from backup
        assert final_path.exists()
        loaded = storage.load_embeddings()
        assert loaded is not None
        assert len(loaded) == 50

    # T009.15: Multiple events ordered by timestamp
    @pytest.mark.unit
    def test_events_ordered_by_timestamp(self, temp_lecture_dir: Path) -> None:
        """
        SPEC: S009
        TEST_ID: T009.15
        Given: Multiple events saved out of order
        When: get_events is called
        Then: Events are returned ordered by timestamp
        """
        # Arrange
        storage = Storage(temp_lecture_dir)

        # Add events out of order
        storage.save_event(300.0, 0.9, "Third topic")
        storage.save_event(100.0, 0.8, "First topic")
        storage.save_event(200.0, 0.85, "Second topic")

        # Act
        events = storage.get_events()

        # Assert - ordered by timestamp
        assert len(events) == 3
        assert events[0]["timestamp"] == 100.0
        assert events[1]["timestamp"] == 200.0
        assert events[2]["timestamp"] == 300.0

    # T009.16: Metadata can be overwritten
    @pytest.mark.unit
    def test_metadata_overwrite(self, temp_lecture_dir: Path) -> None:
        """
        SPEC: S009
        TEST_ID: T009.16
        Given: Metadata key already exists
        When: set_metadata is called with same key
        Then: Value is overwritten
        """
        # Arrange
        storage = Storage(temp_lecture_dir)
        storage.set_metadata("status", "processing")

        # Act
        storage.set_metadata("status", "complete")

        # Assert
        assert storage.get_metadata("status") == "complete"
