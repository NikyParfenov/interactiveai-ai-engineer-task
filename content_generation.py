import os

from models import SEODescription, ValidationResult, State
from loguru import logger
from langchain_openai import ChatOpenAI
from jinja2 import Template

from llm_config.output_template import HTML_TEMPLATE
from utils.file_system import get_system_prompt
from llm_config.llm_config import (
    MODEL, 
    TEMPERATURE,
    MAX_HISTORY,
    MODEL_TONE,
    )


def get_structured_llm(model: str=MODEL, temp: float=TEMPERATURE):
    llm = ChatOpenAI(model=model, temperature=temp)
    return llm.with_structured_output(SEODescription)


def output_processing(state: State):
    logger.info("Starting output processing...")
    try:
        structured_llm = get_structured_llm()
        system_prompt = get_system_prompt().format(llm_tone=MODEL_TONE)
        recent_messages = state["messages"][-MAX_HISTORY:] if state["messages"] else []
        
        logger.info(f"Sending {len(recent_messages)}/{len(state['messages'])} messages to LLM (MAX_HISTORY={MAX_HISTORY})")
        result = structured_llm.invoke([
            ("system", system_prompt),
            *recent_messages
        ])

        logger.success("Content generation completed")
        
        template = Template(HTML_TEMPLATE)
        formatted_html = template.render(
            title=result.title,
            headline=result.headline,
            meta_description=result.meta_description,
            full_description=result.full_description,
            key_features=result.key_features,
            summary=result.summary,
            action=result.action,
        )

        return {
            "structured_data": result.model_dump(),
            "formatted_xml": formatted_html,
            "generation_error": None
        }
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        return {
            "structured_data": None,
            "formatted_xml": None,
            "generation_error": str(e)
        }
