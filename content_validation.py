import re
import json
from pydantic import BaseModel, Field
from loguru import logger
from typing import Literal, Type, TypedDict, Annotated, Optional
from collections import Counter
from models import SEODescription, ValidationResult, State, ConsistencyCheck
from langchain_openai import ChatOpenAI
from utils.file_system import get_valid_prompt
from validation_config.valid_lang_phrases import LLM_PHRASES, CTA_PATTERNS, PROPERTY_TYPES
from validation_config.valid_config import (
    VALID_MODEL, 
    VALID_TEMPERATURE,
    )
from llm_config.llm_config import RETRY_COUNT


class LLMConsistencyValidator:
    """LLM-based validator of consistency between content and JSON data"""
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0):
        self.llm = ChatOpenAI(model=model, temperature=temperature)
        self.structured_llm = self.llm.with_structured_output(ConsistencyCheck)
    
    def validate(self, result, input_json: dict) -> ConsistencyCheck:
        """Validation of consistency through LLM"""

        full_content = f"""
        Title: {result.title}
        Meta Description: {result.meta_description}
        Headline: {result.headline}
        Full Description: {result.full_description}
        Key Features: {', '.join(result.key_features)}
        Summary: {result.summary}
        Action: {result.action}
        """
        prompt = get_valid_prompt().format(
            input_json=json.dumps(input_json, indent=2, ensure_ascii=False), 
            full_content=full_content)

        try:
            result = self.structured_llm.invoke([("user", prompt)])
            logger.info(f"LLM consistency check completed: consistent={result.is_consistent}")
            return result

        except Exception as e:
            logger.error(f"LLM consistency check failed: {e}")
            # Fallback - consider it OK if LLM is unavailable
            return ConsistencyCheck(
                is_consistent=True,
                summary="LLM validation unavailable - skipped"
            )


class QualityValidator:
    
    @staticmethod
    def check_structural_constraints(result: SEODescription) -> tuple[bool, list[str], list[str], float]:
        issues = []
        warnings = []
        score = 1.0
        
        # Check title length
        title_len = len(result.title)
        if title_len > 60:
            issues.append(f"Title too long: {title_len}/60 chars")
            score -= 0.31
        elif title_len > 55:
            warnings.append(f"Title close to limit: {title_len}/60 chars")
            score -= 0.1
        elif title_len < 10:
            warnings.append(f"Title too short: {title_len} chars (min 10)")
            score -= 0.1
        
        # Check meta-description length
        desc_len = len(result.meta_description)
        if desc_len > 155:
            issues.append(f"Meta description too long: {desc_len}/155 chars")
            score -= 0.31
        elif desc_len > 150:
            warnings.append(f"Meta description close to limit: {desc_len}/155 chars")
            score -= 0.1
        elif desc_len < 50:
            warnings.append(f"Meta description too short: {desc_len} chars (recommended min 50)")
            score -= 0.1
        
        # Check full_description
        full_desc_len = len(result.full_description)
        if 700 < full_desc_len:
            issues.append(f"Full description too long: {full_desc_len}/(500-700 characters). Make it SHORTER: write 600-650 characters")
            score -= 0.31
        elif full_desc_len < 500:
            issues.append(f"Full description too short: {full_desc_len}/(500-700 characters). Make it LONGER: write 600-650 characters")
            score -= 0.31
        elif full_desc_len < 520 or full_desc_len > 680:
            warnings.append(f"Full description length {full_desc_len} near boundary")
            score -= 0.1
        
        # Check amount of key_features
        features_count = len(result.key_features)
        if features_count == 0:
            issues.append("No key features provided")
            score -= 0.31
        elif not (3 <= features_count <= 5):
            warnings.append(f"Key features amount {features_count} not in range 3-5")
            score -= 0.2
        
        # Check for empty fields
        for field_name in ['title', 'meta_description', 'headline', 'full_description', 'summary', 'action']:
            field_value = getattr(result, field_name)
            if not field_value or field_value.strip() == "" or field_value.lower() == "null":
                issues.append(f"Field '{field_name}' is empty or null")
                score -= 0.31
        
        # Check for HTML/XML tags
        html_pattern = r'<[^>]+>'
        for field_name in ['title', 'meta_description', 'headline', 'full_description', 'summary', 'action']:
            field_value = str(getattr(result, field_name))
            if re.search(html_pattern, field_value):
                issues.append(f"{field_name} contains HTML/XML tags")
                score -= 0.31
        
        return max(0.0, score), issues, warnings

    @staticmethod
    def check_linguistic_quality(result: SEODescription, language: str = 'en') -> tuple[float, list[str], list[str]]:
        issues = []
        warnings = []
        score = 1.0
        
        full_text = f"{result.title} {result.full_description} {result.summary}"
        
        # Check for repetitions (n-gram analysis)
        repetition_score = QualityValidator._check_repetitions(full_text)
        
        if repetition_score < 0.5:
            issues.append(f"Very high repetition detected (score: {repetition_score:.2f})")
            score -= 0.31
        elif repetition_score < 0.7:
            warnings.append(f"High repetition detected (score: {repetition_score:.2f})")
            score -= 0.2
        
        # Check for LLM-typical phrases
        llm_phrases = LLM_PHRASES.get(language, None)

        if llm_phrases:
            llm_count = sum(1 for phrase in llm_phrases if phrase in full_text.lower())
            
            logger.debug(f"LLM typical phrases check for '{language}': found {llm_count} phrases")
            
            if llm_count > 3:
                issues.append(f"Contains {llm_count} LLM-typical phrases")
                score -= 0.31
            elif llm_count > 1:
                warnings.append(f"Contains {llm_count} LLM-typical phrases")
                score -= 0.1
        else:
            logger.debug(f"LLM phrases check skipped: no phrase list for language '{language}'")
        
        # Check for capitalization (no ALL CAPS)
        caps_words = [word for word in full_text.split() if word.isupper() and len(word) > 3]
        if len(caps_words) > 2:
            warnings.append(f"Contains {len(caps_words)} words in ALL CAPS")
            score -= 0.1
        
        # Check for very short sentences (may indicate poor quality)
        sentences = re.split(r'[.!?]+', result.full_description)
        short_sentences = [s for s in sentences if len(s.strip().split()) < 5 and len(s.strip()) > 0]
        if len(short_sentences) > 2:
            warnings.append(f"Contains {len(short_sentences)} very short sentences")
            score -= 0.1
        
        return max(0.0, score), issues, warnings
    
    @staticmethod
    def _check_repetitions(text: str, ngram_size: int = 3) -> float:
        words = text.lower().split()
        
        if len(words) < ngram_size:
            return 1.0
        
        # Create n-grams
        ngrams = [' '.join(words[i:i+ngram_size]) for i in range(len(words) - ngram_size + 1)]
        
        if not ngrams:
            return 1.0

        # Count uniqueness
        unique_ratio = len(set(ngrams)) / len(ngrams)
        
        # Check for frequent repetitions
        counter = Counter(ngrams)
        most_common_freq = counter.most_common(1)[0][1] if counter else 1
        
        logger.info("Repeated n-grams (top): {}", [f"{ng} ({f}x)" for ng, f in counter.most_common(10) if f > 1])

        # Penalty for frequent repetitions
        repetition_penalty = min(most_common_freq / 3, 1.0)
        
        return unique_ratio * (1 - repetition_penalty * 0.5)

    @staticmethod
    def check_seo_effectiveness(result: SEODescription, input_json: dict, language: str = 'en') -> tuple[float, list[str], list[str]]:
        issues = []
        warnings = []
        score = 1.0
        
        full_text = " ".join([
            result.full_description,
            result.summary,
            " ".join(result.key_features or []),
            ]).lower()
        
        # Check for keyword stuffing
        words = full_text.split()
        word_freq = Counter(words)
        
        # If some word appears > 5% of the total amount
        for word, count in word_freq.most_common(10):
            if len(word) > 3 and count / len(words) > 0.05:
                issues.append(f"Possible keyword stuffing: '{word}' appears {count} times ({count/len(words)*100:.1f}%)")
                score -= 0.31
                break
        
        # Check for presence of CTA
        cta_patterns = CTA_PATTERNS.get(language, None)

        if cta_patterns:
            has_cta = any(
                re.search(pattern, result.action.lower()) 
                for pattern in cta_patterns
            )
            
            if not has_cta:
                warnings.append(f"No clear call-to-action detected in '{language}' language")
                score -= 0.2
            else:
                logger.debug(f"CTA detected for language '{language}'")
        else:
            logger.debug(f"CTA check skipped: no patterns for language '{language}'")

        # Check for property type in title
        title_text = (result.title or "").lower()
        property_types = PROPERTY_TYPES.get(language, None)

        if property_types:
            has_property_type = any(
                re.search(rf'\b{ptype}\b', title_text) 
                for ptype in property_types
            )
            
            if not has_property_type:
                warnings.append(f"Title missing property type keyword  for '{language}'")
                score -= 0.1
            else:
                logger.debug(f"Property type keyword found in title for '{language}'")
        else:
            logger.debug(f"Property type check skipped: no types for language '{language}'")

        # Check for location in title
        title_text = (result.title or "").lower()

        location = input_json.get("location", {}) 
        city = location.get("city")
        neighborhood = location.get("neighborhood")

        if city:
            city_low = city.lower()
            if city_low not in title_text:
                warnings.append(f"Title missing city keyword from input_json: '{city}'")
                score -= 0.1

        if neighborhood:
            neigh_low = neighborhood.lower()
            if neigh_low not in title_text:
                warnings.append(f"Title missing neighborhood keyword from input_json: '{neighborhood}'")
                score -= 0.1
        
        return max(0.0, score), issues, warnings

    @staticmethod
    def check_content_vs_json(result, input_json: dict) -> tuple[float, list[str], list[str]]:
        """Validation of consistency between content and JSON data through LLM"""
        issues = []
        warnings = []
        score = 1.0
        
        if not input_json:
            warnings.append("No input JSON provided for validation")
            return 0.8, [], warnings
        
        logger.info("Starting LLM-based JSON consistency check...")
        
        try:
            validator = LLMConsistencyValidator(model=VALID_MODEL, temperature=VALID_TEMPERATURE)
            check_result = validator.validate(result, input_json)

            # Always evaluate lists regardless of is_consistent flag
            has_fabrications = len(check_result.fabricated_features) > 0
            has_wrong_numbers = len(check_result.incorrect_numbers) > 0
            has_wrong_listing = check_result.wrong_listing_type
            has_wrong_language = check_result.wrong_language

            # CRITICAL ERRORS
            if has_fabrications:
                for f in check_result.fabricated_features:
                    issues.append(f"Fabricated feature: {f}")
                score -= 0.31 * min(len(check_result.fabricated_features), 4)

            if has_wrong_numbers:
                for n in check_result.incorrect_numbers:
                    issues.append(f"Incorrect number: {n}")
                score -= 0.31 * min(len(check_result.incorrect_numbers), 4)

            if has_wrong_listing:
                issues.append("Wrong listing type (sale vs rent mismatch)")
                score -= 0.31

            if has_wrong_language:
                issues.append("Wrong language according to JSON")
                score -= 0.31

            # WARNINGS
            if check_result.missing_important_features:
                for m in check_result.missing_important_features:
                    warnings.append(f"Missing important feature: {m}")
                score -= 0.1 * len(check_result.missing_important_features)

            if check_result.other_inconsistencies:
                for inc in check_result.other_inconsistencies:
                    warnings.append(f"Inconsistency: {inc}")
                score -= 0.1 * len(check_result.other_inconsistencies)

            # If there were fabricated or incorrect items, force consistency to false
            if has_fabrications or has_wrong_numbers or has_wrong_listing or has_wrong_language:
                logger.warning(f"JSON consistency issues found: {check_result.summary}")
            else:
                logger.info("JSON consistency check passed cleanly")

        except Exception as e:
            logger.error(f"JSON consistency validation failed: {e}")
            warnings.append("JSON consistency check unavailable")
            score = 0.8

        return max(0.0, score), issues, warnings


def validate_output(state: State):
    logger.info("Starting validation...")

    if state.get("generation_error"):
        logger.error(f"Cannot validate: generation error - {state['generation_error']}")
        validation: ValidationResult = {
            "passed": False,
            "score": 0.0,
            "issues": [f"Generation error: {state['generation_error']}"],
            "warnings": [],
            "category_scores": {}
        }
        return {"validation": validation}
    
    if not state.get("structured_data"):
        logger.error("Cannot validate: no structured data")
        validation: ValidationResult = {
            "passed": False,
            "score": 0.0,
            "issues": ["No structured data to validate"],
            "warnings": [],
            "category_scores": {}
        }
        return {"validation": validation}

    try:
        result = SEODescription(**state["structured_data"])
        input_json = state.get("input_json") or {}

        language = input_json.get('language', 'en')
        logger.debug(f"Content language: {language}")

        validator = QualityValidator()

        struct_score, struct_issues, struct_warnings = validator.check_structural_constraints(result)
        logger.info(f"Structural validation: score={struct_score:.2f}, issues={len(struct_issues)}")

        ling_score, ling_issues, ling_warnings = validator.check_linguistic_quality(result, language)
        logger.info(f"Linguistic validation: score={ling_score:.2f}, issues={len(ling_issues)}")
        
        seo_score, seo_issues, seo_warnings = validator.check_seo_effectiveness(result, input_json, language)
        logger.info(f"SEO validation: score={seo_score:.2f}, issues={len(seo_issues)}")
        
        json_score, json_issues, json_warnings = validator.check_content_vs_json(result, input_json)
        logger.info(f"JSON consistency validation: score={json_score:.2f}, issues={len(json_issues)}")

        all_issues = struct_issues + ling_issues + seo_issues + json_issues
        all_warnings = struct_warnings + ling_warnings + seo_warnings + json_warnings
        

        scores = {
            "structural": struct_score,
            "linguistic": ling_score,
            "seo": seo_score,
            "json_consistency": json_score
        } 
        
        weights = {
            "structural": 0.25,
            "linguistic": 0.25,
            "seo": 0.25,
            "json_consistency": 0.25
        }

        overall_score = sum(scores[k] * weights[k] for k in scores)
        passed = overall_score >= 0.7 and len(all_issues) == 0
        
        logger.info(f"Overall validation: passed={passed}, score={overall_score:.2f}")
        validation: ValidationResult = {
            "passed": passed,
            "score": overall_score,
            "issues": all_issues,
            "warnings": all_warnings,
            "category_scores": scores
        }

        return {"validation": validation}

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        validation: ValidationResult = {
            "passed": False,
            "score": 0.0,
            "issues": [f"Validation error: {str(e)}"],
            "warnings": [],
            "category_scores": {}
        }
        return {"validation": validation}

def should_retry(state: State) -> Literal["retry", "end"]:

    validation = state.get("validation", {})
    retry_count = state.get("retry_count", 0)
    
    # If validation passed or retries exhausted
    if validation.get("passed", True):
        logger.success("Validation passed, ending")
        return "end"
    
    if retry_count >= RETRY_COUNT:
        logger.warning(f"Max retries ({RETRY_COUNT}) reached, ending")
        return "end"
    
    # If score is too low and there are retries
    score = validation.get("score", 0)
    critical_issues = validation.get("issues", [])

    if (score < 0.7) or (len(critical_issues) > 0):
        logger.warning(f"Score {score:.2f} < 0.7 or critical issues {len(critical_issues)} > 0, retrying (attempt {retry_count + 1}/{RETRY_COUNT})")
        if len(critical_issues) > 0:
            logger.warning(f"Critical issues: {critical_issues}")
        return "retry"
    
    logger.info("Score acceptable but has warnings, ending")
    return "end"


def retry_with_feedback(state: State):

    validation = state.get("validation", {})
    issues = validation.get("issues", [])
    warnings = validation.get("warnings", [])
    retry_count = state.get("retry_count", 0)
    
    logger.info(f"Preparing retry {retry_count + 1} with {len(issues)} issues and {len(warnings)} warnings")
    
    original_message = state["messages"][0] if state["messages"] else ("user", "{}")

    # Prepare feedback for LLM
    feedback_parts = ["The previous attempt had quality issues. Please regenerate addressing the following:\n"]
    
    if issues:
        feedback_parts.append("CRITICAL ISSUES (must fix):")
        for issue in issues:
            feedback_parts.append(f"- {issue}")
    
    if warnings:
        feedback_parts.append("\nWARNINGS (should improve):")
        for warning in warnings:
            feedback_parts.append(f"- {warning}")
    
    feedback_parts.append("\nPlease regenerate the complete property listing with these improvements.")
    
    feedback_message = "\n".join(feedback_parts)
    
    return {
        "messages": [original_message, ("user", feedback_message)],
        "retry_count": retry_count + 1
    }
