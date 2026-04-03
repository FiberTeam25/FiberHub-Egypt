from pydantic import BaseModel, Field

from app.models.review import ReviewTargetType


class ReviewCreateRequest(BaseModel):
    target_type: ReviewTargetType
    target_company_id: str | None = None
    target_profile_id: str | None = None
    rfq_id: str | None = None
    overall_rating: int = Field(..., ge=1, le=5)
    response_speed: int | None = Field(None, ge=1, le=5)
    communication: int | None = Field(None, ge=1, le=5)
    documentation: int | None = Field(None, ge=1, le=5)
    comment: str | None = None


class ReviewUpdateRequest(BaseModel):
    overall_rating: int | None = Field(None, ge=1, le=5)
    response_speed: int | None = Field(None, ge=1, le=5)
    communication: int | None = Field(None, ge=1, le=5)
    documentation: int | None = Field(None, ge=1, le=5)
    comment: str | None = None


class ReviewResponse(BaseModel):
    id: str
    reviewer_id: str
    reviewer_name: str | None = None
    target_type: ReviewTargetType
    target_company_id: str | None
    target_profile_id: str | None
    rfq_id: str | None
    overall_rating: int
    response_speed: int | None
    communication: int | None
    documentation: int | None
    comment: str | None
    is_visible: bool
    created_at: str
    updated_at: str

    @classmethod
    def from_review(cls, review) -> "ReviewResponse":
        reviewer = review.reviewer
        reviewer_name = None
        if reviewer:
            parts = [reviewer.first_name, reviewer.last_name]
            reviewer_name = " ".join(p for p in parts if p)
        return cls(
            id=review.id,
            reviewer_id=review.reviewer_id,
            reviewer_name=reviewer_name or None,
            target_type=review.target_type,
            target_company_id=review.target_company_id,
            target_profile_id=review.target_profile_id,
            rfq_id=review.rfq_id,
            overall_rating=review.overall_rating,
            response_speed=review.response_speed,
            communication=review.communication,
            documentation=review.documentation,
            comment=review.comment,
            is_visible=review.is_visible,
            created_at=review.created_at.isoformat(),
            updated_at=review.updated_at.isoformat(),
        )


class ReviewListResponse(BaseModel):
    items: list[ReviewResponse]
    total: int
    page: int
    page_size: int
    average_rating: float | None = None


class ReviewFlagRequest(BaseModel):
    reason: str = Field(..., min_length=5, max_length=1000)


class ReviewFlagResponse(BaseModel):
    id: str
    review_id: str
    reason: str
    resolved: bool
    created_at: str

    @classmethod
    def from_flag(cls, flag) -> "ReviewFlagResponse":
        return cls(
            id=flag.id,
            review_id=flag.review_id,
            reason=flag.reason,
            resolved=flag.resolved,
            created_at=flag.created_at.isoformat(),
        )
