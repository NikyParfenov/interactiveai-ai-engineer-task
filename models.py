from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal, Type, TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages
from llm_config.llm_config import (
    TITLE, 
    META_DESCRIPTION, 
    HEADLINE, 
    FULL_DESCRIPTION, 
    KEY_FEATURES, 
    SUMMARY, 
    ACTION,
    )


class SEODescription(BaseModel):
    title: str = Field(description=TITLE)
    meta_description: str = Field(description=META_DESCRIPTION)
    headline: str = Field(description=HEADLINE)
    full_description: str = Field(description=FULL_DESCRIPTION)
    key_features: list[str] = Field(default_factory=list, description=KEY_FEATURES)
    summary: str = Field(description=SUMMARY)
    action: str = Field(description=ACTION)


class ValidationResult(TypedDict):
    passed: bool
    score: float
    issues: list[str]
    warnings: list[str]
    category_scores: dict[str, float]


class State(TypedDict):
    messages: Annotated[list, add_messages]
    input_json: Optional[dict]
    structured_data: Optional[dict]
    formatted_xml: Optional[str]
    validation: Optional[ValidationResult]
    retry_count: int
    generation_error: Optional[str]
