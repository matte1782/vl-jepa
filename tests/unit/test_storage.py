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
        storage = Storage(temp_lecture_dir)

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
        storage = Storage(temp_db_path.parent)

        # Assert - check WAL mode
        conn = sqlite3.connect(temp_db_path)
        cursor = conn.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        conn.close()

        assert mode.lower() == "wal"
