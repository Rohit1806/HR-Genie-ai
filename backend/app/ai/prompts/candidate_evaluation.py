CANDIDATE_EVALUATION_PROMPT = """
You are a senior HR analyst evaluating a job candidate. Provide a structured assessment.

CANDIDATE PROFILE:
Name: {candidate_name}
Skills: {candidate_skills}
Total Experience: {candidate_experience_years} years
Education: {education_summary}
Resume Summary: {resume_summary}

JOB REQUIREMENTS:
Title: {job_title}
Description: {job_description}
Required Skills: {required_skills}
Experience Required: {experience_min}-{experience_max} years

MATCH DATA:
Overall Match Score: {match_score}/100
Matched Skills: {matched_skills}
Missing Skills: {missing_skills}

Evaluate this candidate thoroughly across 6 dimensions and return ONLY a valid JSON object (no markdown):

{{
  "dimension_scores": {{
    "technical_skills": <0-100>,
    "experience_relevance": <0-100>,
    "education_fit": <0-100>,
    "communication_indicators": <0-100>,
    "cultural_potential": <0-100>,
    "growth_trajectory": <0-100>
  }},
  "overall_score": <0-100 weighted average>,
  "strengths": [
    "Specific strength 1 with evidence from profile",
    "Specific strength 2",
    "Specific strength 3"
  ],
  "weaknesses": [
    "Specific gap 1 relevant to this role",
    "Specific gap 2"
  ],
  "ai_summary": "3-4 sentence professional evaluation summary",
  "recommendation": "STRONG_YES or YES or MAYBE or NO or STRONG_NO",
  "confidence": <0.0-1.0>,
  "red_flags": ["any serious concerns, or empty array"]
}}

Be objective, specific, and base assessment on the actual data provided.
Return ONLY valid JSON.
"""
