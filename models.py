from pydantic import BaseModel, Field
from typing import Literal, Type, TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages
from utils.file_system import get_valid_prompt
from llm_config.llm_config import (
    TITLE, 
    META_DESCRIPTION, 
    HEADLINE, 
    FULL_DESCRIPTION, 
    KEY_FEATURES, 
    SUMMARY, 
    ACTION,
    )
from validation_config.valid_config import (
    VALID_CONSISTENT,
    VALID_FEATURES,
    VALID_MISSING_FEATURES,
    VALID_INCORRECT_NUMBERS,
    VALID_WRONG_LISTING_TYPE,
    VALID_WRONG_LANGUAGE,
    VALID_OTHER_INCONSISTENCIES,
    VALID_SUMMARY,
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


class ConsistencyCheck(BaseModel):
    is_consistent: bool = Field(description=VALID_CONSISTENT)
    fabricated_features: list[str] = Field(default_factory=list, description=VALID_FEATURES)
    missing_important_features: list[str] = Field(default_factory=list, description=VALID_MISSING_FEATURES)
    incorrect_numbers: list[str] = Field(default_factory=list, description=VALID_INCORRECT_NUMBERS)
    wrong_listing_type: bool = Field(default=False, description=VALID_WRONG_LISTING_TYPE)
    wrong_language: bool = Field(default=False, description=VALID_WRONG_LANGUAGE)
    other_inconsistencies: list[str] = Field(default_factory=list, description=VALID_OTHER_INCONSISTENCIES)
    summary: str = Field(description=VALID_SUMMARY)
