"""Domain models and Pydantic schemas for the Ad Copy Grader."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

Language = Literal["en", "pt"]
FieldType = Literal["headline", "description", "path1", "path2", "final_url"]
Severity = Literal["error", "warning"]
IssueSource = Literal["code", "llm"]


class Location(BaseModel):
    """Specific field and optional index location of an ad issue."""

    field: FieldType
    index: int | None = None


class Issue(BaseModel):
    """An issue identified in an ad, produced by code or LLM."""

    rule_id: str
    severity: Severity
    message: str
    location: Location | None = None
    source: IssueSource


class Suggestion(BaseModel):
    """A rewrite suggestion for a specific ad asset."""

    location: Location
    original: str
    suggested: str
    reason: str


class AdInput(BaseModel):
    """Input payload representing a Responsive Search Ad and context."""

    headlines: list[str] = Field(max_length=30)
    descriptions: list[str] = Field(max_length=8)
    path1: str | None = Field(default=None, max_length=30)
    path2: str | None = Field(default=None, max_length=30)
    final_url: str = Field(max_length=500)
    primary_service: str = Field(min_length=1, max_length=120)
    lp_context: str = ""
    lang: Language = "en"

    @field_validator("headlines")
    @classmethod
    def validate_headlines(cls, v: list[str]) -> list[str]:
        """Validate each headline does not exceed schema upper limit."""
        for idx, headline in enumerate(v):
            if len(headline) > 60:
                raise ValueError(f"Headline at index {idx} exceeds schema limit of 60 characters.")
        return v

    @field_validator("descriptions")
    @classmethod
    def validate_descriptions(cls, v: list[str]) -> list[str]:
        """Validate each description does not exceed schema upper limit."""
        for idx, desc in enumerate(v):
            if len(desc) > 180:
                raise ValueError(
                    f"Description at index {idx} exceeds schema limit of 180 characters."
                )
        return v

    @field_validator("lp_context", mode="after")
    @classmethod
    def truncate_lp_context(cls, v: str) -> str:
        """Truncate landing page context exceeding 1200 characters."""
        if len(v) > 1200:
            return v[:1200]
        return v


class GradeResult(BaseModel):
    """Grading evaluation output for an ad."""

    score: int = Field(ge=0, le=100)
    grade_10: float = Field(ge=0.0, le=10.0)
    passed: bool
    issues: list[Issue]
    suggestions: list[Suggestion] = Field(default_factory=list)
    discarded_suggestions_count: int = 0
    rules_checked: list[str]
    model: str | None = None
    degraded_reason: str | None = None


__all__ = [
    "AdInput",
    "FieldType",
    "GradeResult",
    "Issue",
    "IssueSource",
    "Language",
    "Location",
    "Severity",
    "Suggestion",
]
