from pydantic import BaseModel, Field

class Source(BaseModel):
    record_id: str
    workbook: str
    sheet: str
    category: str | None = None
    cell_range: str | None = None
    rows: str | None = None
    excerpt: str

class ChatRequest(BaseModel):
    question: str = Field(min_length=2, max_length=5000)
    chat_id: int | None = None

class ChatResponse(BaseModel):
    answer: str
    finding: str | None = None
    category: str | None = None
    subcategory: str | None = None
    score_impact: str | None = None
    critical: bool | None = None
    confidence: float
    confidence_label: str
    coaching: str | None = None
    matrix_rule: str | None = None
    sources: list[Source]
    chat_id: int | None = None

class LoginRequest(BaseModel):
    email: str
    password: str = Field(min_length=8, max_length=256)
