from pydantic import BaseModel, Field

from app.models.rfq import RFQResponseStatus, RFQStatus


class RFQCreateRequest(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    request_type: str = Field(max_length=100)  # 'product', 'service', 'both'
    category_id: str | None = None
    category_type: str | None = None  # 'product' or 'service'
    description: str = Field(min_length=10)
    location: str | None = Field(None, max_length=255)
    governorate: str | None = Field(None, max_length=100)
    quantity_scope: str | None = None
    timeline: str | None = Field(None, max_length=255)
    deadline: str  # ISO datetime
    notes: str | None = None


class RFQUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=3, max_length=255)
    request_type: str | None = Field(None, max_length=100)
    category_id: str | None = None
    category_type: str | None = None
    description: str | None = Field(None, min_length=10)
    location: str | None = Field(None, max_length=255)
    governorate: str | None = Field(None, max_length=100)
    quantity_scope: str | None = None
    timeline: str | None = Field(None, max_length=255)
    deadline: str | None = None
    notes: str | None = None


class RFQInviteRequest(BaseModel):
    company_ids: list[str]


class RFQAwardRequest(BaseModel):
    company_id: str


class RFQResponseCreateRequest(BaseModel):
    cover_note: str | None = None
    quoted_amount: float | None = Field(None, ge=0)
    currency: str = "EGP"
    delivery_time: str | None = Field(None, max_length=255)
    notes: str | None = None
    file_url: str | None = Field(None, max_length=500)
    file_name: str | None = Field(None, max_length=255)


class RFQResponseUpdateRequest(BaseModel):
    cover_note: str | None = None
    quoted_amount: float | None = Field(None, ge=0)
    delivery_time: str | None = Field(None, max_length=255)
    notes: str | None = None
    file_url: str | None = Field(None, max_length=500)
    file_name: str | None = Field(None, max_length=255)


class RFQAttachmentResponse(BaseModel):
    id: str
    file_url: str
    file_name: str
    file_size: int | None
    uploaded_at: str

    @classmethod
    def from_attachment(cls, att) -> "RFQAttachmentResponse":
        return cls(
            id=att.id,
            file_url=att.file_url,
            file_name=att.file_name,
            file_size=att.file_size,
            uploaded_at=att.uploaded_at.isoformat(),
        )


class RFQInvitationResponse(BaseModel):
    id: str
    company_id: str
    company_name: str | None = None
    status: RFQResponseStatus
    invited_at: str
    viewed_at: str | None

    @classmethod
    def from_invitation(cls, inv) -> "RFQInvitationResponse":
        return cls(
            id=inv.id,
            company_id=inv.company_id,
            company_name=inv.company.name if inv.company else None,
            status=inv.status,
            invited_at=inv.invited_at.isoformat(),
            viewed_at=inv.viewed_at.isoformat() if inv.viewed_at else None,
        )


class RFQResponseResponse(BaseModel):
    id: str
    rfq_id: str
    company_id: str
    company_name: str | None = None
    submitted_by: str
    cover_note: str | None
    quoted_amount: float | None
    currency: str
    delivery_time: str | None
    notes: str | None
    file_url: str | None
    file_name: str | None
    status: RFQResponseStatus
    submitted_at: str
    updated_at: str

    @classmethod
    def from_response(cls, resp) -> "RFQResponseResponse":
        return cls(
            id=resp.id,
            rfq_id=resp.rfq_id,
            company_id=resp.company_id,
            company_name=resp.company.name if resp.company else None,
            submitted_by=resp.submitted_by,
            cover_note=resp.cover_note,
            quoted_amount=float(resp.quoted_amount) if resp.quoted_amount else None,
            currency=resp.currency,
            delivery_time=resp.delivery_time,
            notes=resp.notes,
            file_url=resp.file_url,
            file_name=resp.file_name,
            status=resp.status,
            submitted_at=resp.submitted_at.isoformat(),
            updated_at=resp.updated_at.isoformat(),
        )


class RFQDetailResponse(BaseModel):
    id: str
    company_id: str
    company_name: str | None = None
    created_by: str
    title: str
    request_type: str
    category_id: str | None
    category_type: str | None
    description: str
    location: str | None
    governorate: str | None
    quantity_scope: str | None
    timeline: str | None
    deadline: str
    notes: str | None
    status: RFQStatus
    awarded_to: str | None
    attachments: list[RFQAttachmentResponse]
    invitations: list[RFQInvitationResponse]
    created_at: str
    updated_at: str

    @classmethod
    def from_rfq(cls, rfq) -> "RFQDetailResponse":
        return cls(
            id=rfq.id,
            company_id=rfq.company_id,
            company_name=rfq.buyer_company.name if rfq.buyer_company else None,
            created_by=rfq.created_by,
            title=rfq.title,
            request_type=rfq.request_type,
            category_id=rfq.category_id,
            category_type=rfq.category_type,
            description=rfq.description,
            location=rfq.location,
            governorate=rfq.governorate,
            quantity_scope=rfq.quantity_scope,
            timeline=rfq.timeline,
            deadline=rfq.deadline.isoformat(),
            notes=rfq.notes,
            status=rfq.status,
            awarded_to=rfq.awarded_to,
            attachments=[RFQAttachmentResponse.from_attachment(a) for a in (rfq.attachments or [])],
            invitations=[RFQInvitationResponse.from_invitation(i) for i in (rfq.invitations or [])],
            created_at=rfq.created_at.isoformat(),
            updated_at=rfq.updated_at.isoformat(),
        )


class RFQSummaryResponse(BaseModel):
    id: str
    title: str
    request_type: str
    status: RFQStatus
    deadline: str
    company_name: str | None = None
    invitations_count: int = 0
    responses_count: int = 0
    created_at: str

    @classmethod
    def from_rfq(cls, rfq, responses_count: int = 0) -> "RFQSummaryResponse":
        return cls(
            id=rfq.id,
            title=rfq.title,
            request_type=rfq.request_type,
            status=rfq.status,
            deadline=rfq.deadline.isoformat(),
            company_name=rfq.buyer_company.name if rfq.buyer_company else None,
            invitations_count=len(rfq.invitations) if rfq.invitations else 0,
            responses_count=responses_count,
            created_at=rfq.created_at.isoformat(),
        )


class RFQListResponse(BaseModel):
    items: list[RFQSummaryResponse]
    total: int
    page: int
    page_size: int
