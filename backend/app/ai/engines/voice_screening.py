"""
AI ENGINE 6: Voice Screening
File: backend/app/ai/engines/voice_screening.py

Processes audio recordings of candidate screenings:
1. Transcribes audio using OpenAI Whisper
2. Evaluates transcript via Gemini for:
   - Communication clarity
   - Confidence level
   - Relevance of answers
   - Technical accuracy
   - Overall voice screening score
"""

import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

from app.ai.gemini_client import call_gemini_json
from app.ai.prompts.voice_evaluation import VOICE_EVALUATION_PROMPT

logger = logging.getLogger(__name__)

# Load Whisper model once at module level (avoid reloading per call)
_WHISPER_MODEL = None


def _get_whisper_model():
    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        logger.info("Loading Whisper 'base' model...")
        from faster_whisper import WhisperModel
        _WHISPER_MODEL = WhisperModel("base", device="cpu", compute_type="int8")
        logger.info("Whisper model loaded.")
    return _WHISPER_MODEL


# ---------------------------------------------------------------------------
# Transcription
# ---------------------------------------------------------------------------

SUPPORTED_AUDIO_FORMATS = {".mp3", ".mp4", ".wav", ".m4a", ".ogg", ".flac", ".webm"}


def transcribe_audio(file_path: str) -> dict:
    """
    Transcribe an audio file using OpenAI Whisper.

    Returns:
    {
        "text": str,
        "language": str,
        "duration_seconds": float,
        "segments": [{"start": float, "end": float, "text": str}],
        "word_count": int,
    }
    """
    path = Path(file_path)
    if path.suffix.lower() not in SUPPORTED_AUDIO_FORMATS:
        raise ValueError(
            f"Unsupported audio format: {path.suffix}. "
            f"Supported: {', '.join(SUPPORTED_AUDIO_FORMATS)}"
        )

    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    file_size_mb = path.stat().st_size / (1024 * 1024)
    if file_size_mb > 25:
        raise ValueError(f"Audio file too large ({file_size_mb:.1f}MB). Max 25MB.")

    logger.info(f"Transcribing audio: {file_path} ({file_size_mb:.1f}MB)")

    model = _get_whisper_model()
    segments_gen, info = model.transcribe(
        file_path,
        beam_size=5,
        language=None,      # auto-detect
        task="transcribe",
    )

    segments = []
    text_pieces = []
    for seg in segments_gen:
        segments.append({
            "start": seg.start,
            "end": seg.end,
            "text": seg.text.strip(),
        })
        text_pieces.append(seg.text)

    text = " ".join(text_pieces).strip()
    # Estimate duration from last segment end
    duration = segments[-1]["end"] if segments else 0.0

    logger.info(f"Transcription complete. {len(text)} chars, {len(segments)} segments.")

    return {
        "text": text,
        "language": info.language if info else "en",
        "duration_seconds": duration,
        "segments": segments,
        "word_count": len(text.split()),
    }


# ---------------------------------------------------------------------------
# Communication Quality Analysis (rule-based pre-check)
# ---------------------------------------------------------------------------

FILLER_WORDS = {
    "um", "uh", "like", "you know", "basically", "literally",
    "actually", "so", "right", "hmm", "er", "ah",
}


def analyze_speech_patterns(transcript: str, duration_seconds: float) -> dict:
    """
    Rule-based analysis of speech patterns from transcript text.
    Complements the AI evaluation with measurable signals.
    """
    words = transcript.lower().split()
    total_words = len(words)

    if total_words == 0:
        return {
            "words_per_minute": 0,
            "filler_word_count": 0,
            "filler_word_ratio": 0,
            "avg_sentence_length": 0,
            "vocabulary_richness": 0,
        }

    # Words per minute
    duration_minutes = max(duration_seconds / 60, 0.1)
    wpm = round(total_words / duration_minutes, 1)

    # Filler word count
    filler_count = sum(1 for w in words if w in FILLER_WORDS)
    filler_ratio = round(filler_count / total_words, 3)

    # Sentence analysis
    sentences = [s.strip() for s in transcript.replace("!", ".").replace("?", ".").split(".") if s.strip()]
    avg_sentence_len = round(total_words / max(len(sentences), 1), 1)

    # Vocabulary richness (Type-Token Ratio)
    unique_words = len(set(words))
    ttr = round(unique_words / total_words, 3)

    return {
        "words_per_minute": wpm,
        "filler_word_count": filler_count,
        "filler_word_ratio": filler_ratio,
        "avg_sentence_length": avg_sentence_len,
        "vocabulary_richness": ttr,
    }


def _speech_metrics_to_score(metrics: dict) -> float:
    """Convert speech metrics into a 0-100 communication score."""
    score = 70.0  # Base

    wpm = metrics.get("words_per_minute", 130)
    # Ideal speaking pace: 120-160 wpm
    if 120 <= wpm <= 160:
        score += 10
    elif wpm < 80 or wpm > 200:
        score -= 15
    elif wpm < 100 or wpm > 180:
        score -= 8

    filler_ratio = metrics.get("filler_word_ratio", 0.05)
    if filler_ratio < 0.03:
        score += 10
    elif filler_ratio > 0.10:
        score -= 15
    elif filler_ratio > 0.07:
        score -= 8

    ttr = metrics.get("vocabulary_richness", 0.5)
    if ttr > 0.65:
        score += 10
    elif ttr < 0.35:
        score -= 10

    return round(max(0, min(100, score)), 1)


# ---------------------------------------------------------------------------
# Main Voice Screening Function
# ---------------------------------------------------------------------------

async def process_voice_screening(
    audio_file_path: str,
    job_title: str,
    questions_asked: Optional[list[str]] = None,
    candidate_name: str = "Candidate",
) -> dict:
    """
    Full voice screening pipeline:
    1. Transcribe audio
    2. Analyze speech patterns
    3. AI evaluation of transcript content

    Returns:
    {
        "transcript": str,
        "language": str,
        "duration_seconds": float,
        "word_count": int,
        "speech_metrics": {...},
        "communication_score": float,
        "content_evaluation": {
            "relevance_score": float,
            "confidence_score": float,
            "technical_accuracy_score": float,
            "clarity_score": float,
            "overall_content_score": float,
        },
        "overall_voice_score": float,
        "strengths": [str],
        "areas_for_improvement": [str],
        "key_highlights": [str],
        "recommendation": str,
        "ai_summary": str,
    }
    """
    logger.info(f"Processing voice screening for: {candidate_name}, job: {job_title}")

    # Step 1: Transcribe
    try:
        transcription = transcribe_audio(audio_file_path)
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return _empty_screening_result(str(e))

    transcript = transcription["text"]
    if not transcript or transcription["word_count"] < 20:
        return _empty_screening_result("Transcript too short or empty. Check audio quality.")

    # Step 2: Speech pattern analysis
    speech_metrics = analyze_speech_patterns(
        transcript=transcript,
        duration_seconds=transcription["duration_seconds"],
    )
    communication_score = _speech_metrics_to_score(speech_metrics)

    # Step 3: AI content evaluation
    questions_text = "\n".join(
        f"- {q}" for q in (questions_asked or ["General screening questions"])
    )

    prompt = VOICE_EVALUATION_PROMPT.format(
        candidate_name=candidate_name,
        job_title=job_title,
        questions_asked=questions_text,
        transcript=transcript[:3000],  # Limit for Gemini free tier
        duration_seconds=transcription["duration_seconds"],
        word_count=transcription["word_count"],
        words_per_minute=speech_metrics["words_per_minute"],
        filler_ratio=speech_metrics["filler_word_ratio"],
    )

    try:
        ai_eval: dict = await call_gemini_json(prompt)
    except Exception as e:
        logger.error(f"AI voice evaluation failed: {e}")
        ai_eval = _fallback_content_eval(communication_score)

    # Extract and validate content evaluation scores
    content_eval = {
        "relevance_score": _safe_score(ai_eval.get("relevance_score", 60)),
        "confidence_score": _safe_score(ai_eval.get("confidence_score", 60)),
        "technical_accuracy_score": _safe_score(ai_eval.get("technical_accuracy_score", 60)),
        "clarity_score": _safe_score(ai_eval.get("clarity_score", communication_score)),
        "overall_content_score": _safe_score(ai_eval.get("overall_content_score", 60)),
    }

    # Weighted overall voice score
    overall = round(
        communication_score * 0.30 + content_eval["overall_content_score"] * 0.70,
        1,
    )

    recommendation = _voice_score_to_recommendation(overall)

    return {
        "transcript": transcript,
        "language": transcription["language"],
        "duration_seconds": transcription["duration_seconds"],
        "word_count": transcription["word_count"],
        "speech_metrics": speech_metrics,
        "communication_score": communication_score,
        "content_evaluation": content_eval,
        "overall_voice_score": overall,
        "strengths": ai_eval.get("strengths", []),
        "areas_for_improvement": ai_eval.get("areas_for_improvement", []),
        "key_highlights": ai_eval.get("key_highlights", []),
        "recommendation": recommendation,
        "ai_summary": ai_eval.get("ai_summary", f"{candidate_name} completed voice screening with a score of {overall:.0f}/100."),
    }


def _safe_score(value) -> float:
    try:
        return round(max(0, min(100, float(value))), 1)
    except (TypeError, ValueError):
        return 50.0


def _voice_score_to_recommendation(score: float) -> str:
    if score >= 80:
        return "STRONG_YES"
    elif score >= 65:
        return "YES"
    elif score >= 50:
        return "MAYBE"
    elif score >= 35:
        return "NO"
    return "STRONG_NO"


def _empty_screening_result(reason: str) -> dict:
    return {
        "transcript": "",
        "language": "unknown",
        "duration_seconds": 0,
        "word_count": 0,
        "speech_metrics": {},
        "communication_score": 0,
        "content_evaluation": {},
        "overall_voice_score": 0,
        "strengths": [],
        "areas_for_improvement": [reason],
        "key_highlights": [],
        "recommendation": "NO",
        "ai_summary": f"Voice screening could not be processed: {reason}",
    }


def _fallback_content_eval(communication_score: float) -> dict:
    return {
        "relevance_score": communication_score,
        "confidence_score": communication_score,
        "technical_accuracy_score": communication_score * 0.9,
        "clarity_score": communication_score,
        "overall_content_score": communication_score,
        "strengths": ["Completed the voice screening"],
        "areas_for_improvement": ["AI evaluation unavailable — manual review recommended"],
        "key_highlights": [],
        "ai_summary": "Automated content evaluation unavailable. Score based on speech metrics only.",
    }
