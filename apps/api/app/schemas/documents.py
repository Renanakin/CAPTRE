from pydantic import BaseModel


class OverrideRequest(BaseModel):
    fields: dict[str, str | int | float | None]
    reason: str


class RenditionGenerateRequest(BaseModel):
    tenant_id: str
    period: str
    document_ids: list[str]
    template_version: str = "01-rendicion-gastos-2025"


class RenditionGenerateByFilterRequest(BaseModel):
    tenant_id: str
    period: str
    responsible: str | None = None
    center_cost: str | None = None
    template_version: str = "01-rendicion-gastos-2025"


class ReviewResolveRequest(BaseModel):
    decision: str
    reason: str
    reviewer_id: str = "system"
    overrides: dict[str, str | int | float | None] = {}


class ReviewActionRequest(BaseModel):
    reviewer_id: str
    reason: str
    overrides: dict[str, str | int | float | None] = {}


class ReviewOverridesRequest(BaseModel):
    reviewer_id: str
    reason: str
    overrides: dict[str, str | int | float | None]
