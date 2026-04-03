from pydantic import BaseModel, Field

from app.models.company import VerificationStatusEnum


class VerificationSubmitRequest(BaseModel):
    company_id: str | None = None
    profile_id: str | None = None
    documents: list["VerificationDocumentInput"]


class VerificationDocumentInput(BaseModel):
    document_type: str = Field(max_length=100)
    file_url: str = Field(max_length=500)
    file_name: str = Field(max_length=255)


class VerificationDocumentResponse(BaseModel):
    id: str
    document_type: str
    file_url: str
    file_name: str
    uploaded_at: str

    @classmethod
    def from_doc(cls, doc) -> "VerificationDocumentResponse":
        return cls(
            id=doc.id,
            document_type=doc.document_type,
            file_url=doc.file_url,
            file_name=doc.file_name,
            uploaded_at=doc.uploaded_at.isoformat(),
        )


class VerificationRequestResponse(BaseModel):
    id: str
    company_id: str | None
    profile_id: str | None
    status: VerificationStatusEnum
    submitted_at: str
    reviewed_at: str | None
    admin_notes: str | None
    documents: list[VerificationDocumentResponse]

    @classmethod
    def from_request(cls, req) -> "VerificationRequestResponse":
        return cls(
            id=req.id,
            company_id=req.company_id,
            profile_id=req.profile_id,
            status=req.status,
            submitted_at=req.submitted_at.isoformat(),
            reviewed_at=req.reviewed_at.isoformat() if req.reviewed_at else None,
            admin_notes=req.admin_notes,
            documents=[VerificationDocumentResponse.from_doc(d) for d in req.documents],
        )


class VerificationQueueResponse(BaseModel):
    items: list[VerificationRequestResponse]
    total: int
    page: int
    page_size: int


class VerificationReviewRequest(BaseModel):
    admin_notes: str | None = None


VerificationSubmitRequest.model_rebuild()
