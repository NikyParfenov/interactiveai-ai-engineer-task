import os
import json

from datetime import datetime
from pydantic import BaseModel, Field
from typing import Literal, Type, TypedDict, Annotated, Optional
from dotenv import load_dotenv
from loguru import logger

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.message import add_messages

from models import State
from utils.file_system import save_result_html
from utils.analysis import visualize_graph_html, log_validation_report
from content_generation import (
    get_structured_llm, 
    output_processing,
)
from content_validation import (
    validate_output,
    should_retry,
    retry_with_feedback,
)
from IPython.display import Image, display
from llm_config.llm_config import RETRY_COUNT

load_dotenv()
logger.add(
    "logs/{time:YYYY-MM-DD}.log",
    level="INFO",
    rotation="00:00",
    retention="30 days",
    compression="zip", 
    enqueue=True,
)

def create_graph():
    workflow = StateGraph(State)
    
    workflow.add_node("output_processing", output_processing)
    workflow.add_node("validate", validate_output)
    workflow.add_node("retry", retry_with_feedback)
    
    workflow.add_edge(START, "output_processing")
    workflow.add_edge("output_processing", "validate")

    workflow.add_conditional_edges(
        "validate",
        should_retry,
        {
            "retry": "retry",
            "end": END
        }
    )
    
    workflow.add_edge("retry", "output_processing")
    
    return workflow.compile()


def run_pipeline(input_json: dict, save_output: bool = False):

    logger.info("Starting SEO content generation pipeline")
    
    app = create_graph()
    result = app.invoke({
        "messages": [("user", json.dumps(input_json, indent=2))],
        "input_json": input_json,
        "retry_count": 0
    })

    validation = result.get("validation", {})
    logger.info(f"Final validation: passed={validation.get('passed')}, score={validation.get('score', 0):.2f}")
    
    if validation.get("issues"):
        logger.warning(f"Remaining issues: {validation['issues']}")
    
    if validation.get("warnings"):
        logger.info(f"Warnings: {validation['warnings']}")
    
    logger.info(f"Total retries: {result.get('retry_count', 0)}/{RETRY_COUNT}")

    if save_output:
        if result.get("formatted_data"):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"results/{ts}_output.html"
            save_result_html(result.get("formatted_data"), path=path)
            logger.success(f"Result saved to '{path}'")
        else:
            logger.error("No output generated")
    
    return {
        "struct_data": result.get("structured_data"),
        "formatted_data": result.get("formatted_xml"),
        "validation": validation,
        "retry_count": result.get("retry_count", 0)
    }


if __name__ == "__main__":
    with open("example/input_example.json", "r", encoding="utf-8") as f:
        input_json = json.load(f)

    result = run_pipeline(input_json, save_output=True)

    log_validation_report(result)
    # visualize_graph_html(app = create_graph())
