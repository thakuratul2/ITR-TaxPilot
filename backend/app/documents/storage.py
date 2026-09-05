"""Ephemeral file storage manager with TTL lifecycle tracking and automatic cleanup."""

import time
from pathlib import Path

from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger("app.documents.storage")


class EphemeralStorageManager:
    """Manages temporary document storage with automatic TTL-based pruning."""

    def __init__(self, base_dir: str | Path = "uploads"):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def save_ephemeral_file(self, document_id: str, filename: str, file_bytes: bytes) -> str:
        """Save file bytes to ephemeral storage and return absolute path."""
        target_dir = self.base_dir / document_id
        target_dir.mkdir(parents=True, exist_ok=True)

        file_path = target_dir / filename
        with open(file_path, "wb") as f:
            f.write(file_bytes)

        logger.info("Saved ephemeral document %s to %s", document_id, str(file_path))
        return str(file_path)

    def delete_document_files(self, document_id: str) -> bool:
        """Delete all files and directory for a specific document ID."""
        target_dir = self.base_dir / document_id
        if target_dir.exists() and target_dir.is_dir():
            for child in target_dir.glob("*"):
                try:
                    child.unlink()
                except Exception as e:
                    logger.warning("Failed to unlink %s: %s", str(child), str(e))
            try:
                target_dir.rmdir()
                logger.info("Deleted ephemeral directory for document %s", document_id)
                return True
            except Exception as e:
                logger.warning("Failed to remove directory %s: %s", str(target_dir), str(e))
        return False

    def cleanup_expired_files(self, retention_minutes: int | None = None) -> int:
        """Remove document directories older than DOCUMENT_RETENTION_MINUTES (or retention_minutes override)."""
        settings = get_settings()
        mins = retention_minutes if retention_minutes is not None else settings.DOCUMENT_RETENTION_MINUTES
        retention_seconds = mins * 60
        now = time.time()
        removed_count = 0

        if not self.base_dir.exists():
            return 0

        for doc_dir in self.base_dir.iterdir():
            if doc_dir.is_dir():
                try:
                    mtime = doc_dir.stat().st_mtime
                    if now - mtime >= retention_seconds:
                        self.delete_document_files(doc_dir.name)
                        removed_count += 1
                except Exception as e:
                    logger.warning("Error evaluating directory %s for expiration: %s", str(doc_dir), str(e))

        if removed_count > 0:
            logger.info("Cleaned up %d expired document storage directories", removed_count)
        return removed_count


# Singleton instance
storage_manager = EphemeralStorageManager()
