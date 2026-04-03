from pydantic import BaseModel


class UploadResponse(BaseModel):
    key: str
    url: str
    file_name: str
    file_size: int
    content_type: str | None
