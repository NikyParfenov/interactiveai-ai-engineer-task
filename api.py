from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict
from loguru import logger
from main import run_pipeline

from datetime import datetime
from utils.file_system import save_result_html


app = FastAPI(title="InteractiveAI SEO Generator")


class GenerateRequest(BaseModel):
    input_json: Dict[str, Any]


class GenerateResponse(BaseModel):
    html: str
    validation: Dict[str, Any]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/generate", response_model=GenerateResponse)
def generate(req: GenerateRequest):
    try:
        logger.info("Received /generate request")
        result = run_pipeline(req.input_json)

        html = result.get("formatted_data")
        validation = result.get("validation", {})

        if not html:
            raise HTTPException(status_code=500, detail="No HTML generated")

        if result.get("formatted_data"):
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = f"results/{ts}_output.html"
            save_result_html(result.get("formatted_data"), path=path)
            logger.success(f"Result saved to '{path}'")
        else:
            logger.error("No output generated")
        
        return GenerateResponse(html=html, validation=validation)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error in /generate")
        raise HTTPException(status_code=500, detail=str(e))
        