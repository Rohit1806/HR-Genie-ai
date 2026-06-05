VOICE_EVALUATION_PROMPT = """
You are an expert voice screening evaluator. Analyze this candidate's responses.

SCREENING CONTEXT:
Candidate: {candidate_name}
Job Title: {job_title}
Duration: {duration_seconds:.0f} seconds
Word Count: {word_count}
Speaking Pace: {words_per_minute:.0f} words/minute
Filler Word Ratio: {filler_ratio:.1%}

QUESTIONS ASKED:
{questions_asked}

TRANSCRIPT:
{transcript}

Evaluate the candidate's voice screening performance and return ONLY valid JSON (no markdown):
{{
  "relevance_score": <0-100: how well answers addressed the questions>,
  "confidence_score": <0-100: vocal confidence and assertiveness>,
  "technical_accuracy_score": <0-100: accuracy of technical content>,
  "clarity_score": <0-100: communication clarity and structure>,
  "overall_content_score": <0-100: weighted content quality>,
  "strengths": [
    "Specific strength observed in the screening",
    "Another strength"
  ],
  "areas_for_improvement": [
    "Specific area to improve",
    "Another area"
  ],
  "key_highlights": [
    "Notable point from the transcript"
  ],
  "ai_summary": "3-4 sentence professional summary of the voice screening performance"
}}

Base your evaluation strictly on the transcript content.
Return ONLY valid JSON.
"""
