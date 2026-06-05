INTERVIEW_QUESTIONS_PROMPT = """
You are an expert technical recruiter. Generate tailored interview questions.

JOB DETAILS:
Title: {job_title}
Department: {department}
Experience Required: {experience_min}-{experience_max} years
Required Skills: {required_skills}
Job Description: {job_description}

Generate exactly {question_count} interview questions across these categories: {categories}

Return ONLY a valid JSON object (no markdown, no backticks):
{{
  "questions": [
    {{
      "question": "Full interview question text",
      "category": "technical|behavioral|situational|culture_fit|role_specific|general",
      "difficulty": "easy|medium|hard",
      "skill_area": "the specific skill or competency being assessed",
      "follow_up": "A follow-up question to probe deeper",
      "evaluation_criteria": "What a good answer looks like"
    }}
  ]
}}

Distribution guidelines:
- 30% technical/role_specific (test real skills)
- 25% behavioral (STAR method)
- 20% situational (problem scenarios)
- 15% culture_fit
- 10% general

Make questions specific to {job_title}, not generic HR questions.
Vary difficulty: 40% easy, 40% medium, 20% hard.
Return ONLY valid JSON.
"""
