"""
Voice Capture Routes

Record what you learned by talking. AI transcribes and extracts priors.
Two modes:
1. Audio upload — send a WAV/MP3, Gemini transcribes + extracts in one call
2. Transcript — frontend does STT, sends text, we extract priors
"""

import base64
import json
import time

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from core.llm import complete, complete_json, parse_json
from core.storage import save_priors

router = APIRouter(prefix="/api/voice", tags=["voice"])


VOICE_EXTRACT_PROMPT = """You are an expert at helping people retain and apply what they learn.

The user just recorded themselves talking about something they recently learned.
This could be from ANY source — a book, podcast, YouTube video, conversation,
class, article, life experience, workshop, or their own reflection.

Your job:
1. Transcribe exactly what they said (if audio provided)
2. Extract actionable "priors" — principles they can practice in daily life

For each prior, provide:
- name: Short name (2-5 words)
- principle: The core insight in one sentence
- practice: A concrete way to practice this daily (specific, under 5 minutes)
- trigger: When/where in daily life to apply this (e.g., "when writing an email", "before a difficult conversation", "while reading")
- source: What they were learning from (book title, podcast name, etc.)

Return JSON:
{{
  "transcript": "exact words the user said (verbatim transcription)",
  "title": "topic or source they were talking about",
  "summary": "2-3 sentence summary of what they learned",
  "priors": [
    {{
      "name": "...",
      "principle": "...",
      "practice": "...",
      "trigger": "...",
      "source": "..."
    }}
  ]
}}

Extract 3-7 priors. Focus on what's most actionable and life-changing.
Return ONLY valid JSON."""


class VoiceTranscriptRequest(BaseModel):
    """When frontend handles STT and sends text."""
    transcript: str
    source: Optional[str] = None


@router.post("/capture/audio")
async def capture_from_audio(
    audio: UploadFile = File(...),
    source: str = Form(default=""),
):
    """
    Upload audio (WAV/MP3) of user talking about what they learned.
    Gemini transcribes and extracts priors in one call.
    """
    start_time = time.time()

    try:
        audio_bytes = await audio.read()
        audio_base64 = base64.b64encode(audio_bytes).decode("utf-8")

        # Detect content type
        content_type = audio.content_type or "audio/wav"
        audio_data_url = f"data:{content_type};base64,{audio_base64}"

        source_hint = f"\nThe user mentioned they were learning from: {source}" if source else ""

        # Build multimodal message with audio
        from litellm import acompletion
        from core.llm import _set_api_key
        from core.config import get_model

        _set_api_key()

        messages = [
            {"role": "user", "content": [
                {"type": "file", "file": {"file_data": audio_data_url}},
                {"type": "text", "text": VOICE_EXTRACT_PROMPT + source_hint},
            ]}
        ]

        model = get_model()
        # Use Gemini for audio (best multimodal support)
        if "gemini" not in model:
            model = "gemini/gemini-2.5-flash"

        response = await acompletion(
            model=model,
            messages=messages,
            temperature=0.3,
            max_tokens=4000,
        )

        result = parse_json(response.choices[0].message.content)
        priors = result.get("priors", [])
        ids = save_priors(priors, source_title=result.get("title", ""))

        elapsed_ms = (time.time() - start_time) * 1000

        return JSONResponse({
            "success": True,
            "transcript": result.get("transcript", ""),
            "title": result.get("title", ""),
            "summary": result.get("summary", ""),
            "priors_count": len(ids),
            "priors": priors,
            "ids": ids,
            "latency_ms": round(elapsed_ms),
        })

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)}, status_code=500)


@router.post("/capture/transcript")
async def capture_from_transcript(request: VoiceTranscriptRequest):
    """
    Frontend did STT already, sends us the transcript.
    We extract priors from the text.
    """
    try:
        from core.extractor import extract_priors

        result = await extract_priors(request.transcript, source_hint=request.source or "")
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
