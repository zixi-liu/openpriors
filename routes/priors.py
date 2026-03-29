"""
Prior Capture Routes

Two ways to capture:
1. Upload content (URL or PDF text)
2. Direct text input (notes, quotes, ideas)
"""

from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional

from core.extractor import extract_priors, extract_from_url
from core.storage import save_priors, get_all_priors, search_priors, get_prior

router = APIRouter(prefix="/api/priors", tags=["priors"])


class CaptureFromTextRequest(BaseModel):
    content: str
    source: Optional[str] = None


class CaptureFromURLRequest(BaseModel):
    url: str


class SearchRequest(BaseModel):
    query: str
    limit: int = 10


@router.post("/capture/text")
async def capture_from_text(request: CaptureFromTextRequest):
    """Extract priors from text (notes, book highlights, ideas)."""
    try:
        result = await extract_priors(request.content, source_hint=request.source or "")
        priors = result.get("priors", [])
        ids = save_priors(priors, source_title=result.get("title", ""))

        return JSONResponse({
            "success": True,
            "title": result.get("title", ""),
            "summary": result.get("summary", ""),
            "priors_count": len(ids),
            "priors": priors,
            "ids": ids,
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@router.post("/capture/url")
async def capture_from_url(request: CaptureFromURLRequest):
    """Extract priors from a URL (article, blog, video)."""
    try:
        extracted = await extract_from_url(request.url)
        content = extracted.get("content", "")
        if not content:
            return JSONResponse({"success": False, "error": "Could not extract content from URL"})

        result = await extract_priors(content, source_hint=request.url)
        priors = result.get("priors", [])
        ids = save_priors(priors, source_title=result.get("title", ""))

        return JSONResponse({
            "success": True,
            "title": result.get("title", ""),
            "summary": result.get("summary", ""),
            "priors_count": len(ids),
            "priors": priors,
            "ids": ids,
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@router.post("/capture/pdf")
async def capture_from_pdf(file: UploadFile = File(...)):
    """Extract priors from an uploaded PDF."""
    try:
        content = await file.read()
        text = content.decode("utf-8", errors="ignore")

        result = await extract_priors(text, source_hint=file.filename or "uploaded PDF")
        priors = result.get("priors", [])
        ids = save_priors(priors, source_title=result.get("title", ""))

        return JSONResponse({
            "success": True,
            "title": result.get("title", ""),
            "summary": result.get("summary", ""),
            "priors_count": len(ids),
            "priors": priors,
            "ids": ids,
        })
    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@router.get("")
async def list_priors():
    """List all active priors."""
    priors = get_all_priors()
    return JSONResponse({"success": True, "priors": priors, "count": len(priors)})


@router.get("/{prior_id}")
async def get_prior_detail(prior_id: str):
    """Get a single prior by ID."""
    prior = get_prior(prior_id)
    if not prior:
        return JSONResponse({"success": False, "error": "Prior not found"}, status_code=404)
    return JSONResponse({"success": True, "prior": prior})


@router.post("/search")
async def search(request: SearchRequest):
    """Full-text search across priors."""
    results = search_priors(request.query, request.limit)
    return JSONResponse({"success": True, "results": results, "count": len(results)})
