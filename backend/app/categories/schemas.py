from pydantic import BaseModel, Field


class CategoryCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    parent_id: str | None = None
    description: str | None = None
    icon: str | None = Field(None, max_length=100)
    sort_order: int = 0


class CategoryUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=150)
    description: str | None = None
    icon: str | None = Field(None, max_length=100)
    sort_order: int | None = None
    is_active: bool | None = None


class CategoryResponse(BaseModel):
    id: str
    name: str
    slug: str
    parent_id: str | None
    description: str | None
    icon: str | None
    sort_order: int
    is_active: bool

    model_config = {"from_attributes": True}


class GovernorateResponse(BaseModel):
    id: str
    name: str
    name_ar: str | None

    model_config = {"from_attributes": True}
