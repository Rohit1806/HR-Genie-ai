RESUME_EXTRACTION_PROMPT = """
You are an expert HR AI that extracts structured information from resumes.

Extract ALL information from the resume below and return a JSON object.

Resume Text:
{resume_text}

Return ONLY a valid JSON object with this exact structure (no markdown, no backticks):
{{
  "candidate": {{
    "first_name": "string or null",
    "last_name": "string or null",
    "email": "string or null",
    "phone": "string or null",
    "linkedin_url": "string or null",
    "location": "city, country or null"
  }},
  "education": [
    {{
      "degree": "string",
      "institution": "string",
      "year": number_or_null,
      "score": "GPA or percentage or null"
    }}
  ],
  "experience": [
    {{
      "company": "string",
      "title": "string",
      "start_year": number_or_null,
      "end_year": "number or 'present'",
      "duration_months": number_or_null,
      "key_responsibilities": ["string"]
    }}
  ],
  "skills": ["skill1", "skill2"],
  "certifications": ["cert1", "cert2"],
  "summary": "2 sentence professional summary of this candidate"
}}

Rules:
- Extract ALL skills mentioned anywhere in the resume
- For experience duration_months: calculate from start/end years if given
- If a field is not found, use null
- skills should be individual items, not sentences
- Return ONLY JSON, nothing else
"""
