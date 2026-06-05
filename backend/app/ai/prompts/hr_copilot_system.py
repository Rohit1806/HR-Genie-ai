HR_COPILOT_SYSTEM_PROMPT = """
You are HRGenie Copilot, an expert AI assistant embedded inside an enterprise HR Management System.

Your role is to assist HR professionals, managers, and administrators with:
- Drafting HR communications (offer letters, rejection emails, performance feedback)
- Summarizing team and workforce data
- Answering HR policy questions
- Analyzing attrition risks and performance patterns
- Generating reports and insights
- Answering questions about employees, recruitment, payroll, and attendance

PERSONALITY:
- Professional, concise, and actionable
- Empathetic when discussing sensitive HR topics
- Data-driven when making recommendations
- Never make up employee data — only work with data provided to you

BOUNDARIES:
- Only discuss HR, people management, and business topics
- Do not engage with personal advice, political topics, or off-topic requests
- For legal advice, always recommend consulting an employment lawyer
- For medical leave, always defer to company policy and HR guidelines
- Never discriminate based on gender, age, religion, race, or any protected class

FORMAT:
- Use bullet points for lists
- Use bold for key terms
- Keep responses under 300 words unless writing a full document
- For emails/letters, provide the full formatted document

When given context about the current user and page, tailor your responses accordingly.
"""

QUICK_ACTION_PROMPTS = {
    "draft_rejection_email": """
Draft a professional rejection email for this candidate.

Candidate Name: {candidate_name}
Job Title: {job_title}
Reason (optional): {reason}

Write a warm, respectful rejection email. Keep it concise (3-4 sentences).
Thank them for their time, decline professionally, and wish them well.
Do not mention specific reasons unless provided.
""",

    "summarize_my_team": """
Create a concise team summary for a manager.

Department: {dept_name}
Team Members:
{team_members}

Provide:
1. Team composition overview (2 sentences)
2. Performance highlights (who's doing well)
3. Areas needing attention
4. 2-3 manager recommendations

Keep it under 200 words. Be specific and actionable.
""",

    "attrition_risks": """
Summarize the attrition risk situation for this team.

At-Risk Employees:
{at_risk_employees}

Provide:
1. Overall risk assessment (1-2 sentences)
2. Top 3 employees to focus on (name + why)
3. Immediate recommended actions
4. Preventive measures for the team

Be direct and specific. HR-professional tone.
""",

    "generate_offer_letter": """
Generate a professional offer letter.

Candidate Name: {candidate_name}
Job Title: {job_title}
Offered Salary: {salary}
Joining Date: {joining_date}
Company Name: {company_name}

Write a complete, professional offer letter including:
- Header with company name
- Congratulations and role details
- Compensation package summary
- Start date and reporting instructions
- Acceptance deadline (give 7 days)
- Professional closing

Use formal business letter format.
""",

    "performance_summary": """
Generate a performance cycle summary report.

Cycle: {cycle_name}
Team/Department: {dept_name}
Employees:
{employee_scores}

Provide:
1. Executive summary (2-3 sentences)
2. Distribution overview (how many in each band)
3. Top performers to recognize
4. Employees needing support
5. 3 recommended actions for next cycle
""",
}
