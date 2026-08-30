"""Document schemas for upload and retrieval."""

from datetime import datetime

from pydantic import BaseModel, Field


class DocumentResponse(BaseModel):
    """Document metadata response."""
    id: str = Field(..., description="Unique document ID")
    filename: str = Field(..., description="Sanitized stored filename")
    original_filename: str = Field(..., description="Original upload filename")
    content_type: str = Field(..., description="MIME content type")
    file_size_bytes: int = Field(..., description="File size in bytes")
    status: str = Field(..., description="Document lifecycle status")
    created_at: datetime = Field(..., description="Upload timestamp")


class DocumentUploadPayload(BaseModel):
    """Upload acknowledgement data containing document and job IDs."""
    document_id: str = Field(..., description="Uploaded document identifier")
    job_id: str = Field(..., description="Asynchronous processing job identifier")
    status: str = Field(default="pending", description="Initial job status")
    message: str = Field(default="Form 16 uploaded successfully and queued for processing", description="Status message")
