"""
AI ENGINE 7: HR Copilot
File: backend/app/ai/engines/hr_copilot.py

Conversational AI assistant for HR operations.
Handles multi-turn conversations with context awareness.
Supports quick actions: draft emails, summarize teams,
generate offer letters, attrition risk summaries.

Uses Gemini with a structured system prompt that
enforces HR domain focus and professional tone.
"""

import logging
from enum import Enum
from typing import AsyncGenerator, Optional

import google.generativeai as genai

from app.config import settings
from app.ai.prompts.hr_copilot_system import (
    HR_COPILOT_SYSTEM_PROMPT,
    QUICK_ACTION_PROMPTS,
)

logger = logging.getLogger(__name__)


class QuickAction(str, Enum):
    DRAFT_REJECTION = "draft_rejection_email"
    SUMMARIZE_TEAM = "summarize_my_team"
    ATTRITION_RISKS = "attrition_risks"
    GENERATE_OFFER = "generate_offer_letter"
    PERFORMANCE_SUMMARY = "performance_summary"
    LEAVE_POLICY_QUERY = "leave_policy_query"


# ---------------------------------------------------------------------------
# Context Builder
# ---------------------------------------------------------------------------

def build_context_block(context: dict) -> str:
    """
    Build a structured context string to inject into the system prompt.
    Context dict can contain: user_name, user_role, company_name,
    current_page, team_size, open_positions, pending_approvals, etc.
    """
    if not context:
        return ""

    lines = ["[Current Context]"]
    if context.get("user_name"):
        lines.append(f"User: {context['user_name']} ({context.get('user_role', 'HR')})")
    if context.get("company_name"):
        lines.append(f"Company: {context['company_name']}")
    if context.get("current_page"):
        lines.append(f"Current Module: {context['current_page']}")
    if context.get("team_size"):
        lines.append(f"Team Size: {context['team_size']}")
    if context.get("open_positions"):
        lines.append(f"Open Positions: {context['open_positions']}")
    if context.get("pending_approvals"):
        lines.append(f"Pending Approvals: {context['pending_approvals']}")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Message History Management
# ---------------------------------------------------------------------------

def prepare_conversation_history(
    messages: list[dict],
    max_turns: int = 10,
) -> list[dict]:
    """
    Prepare conversation history for Gemini API.
    Trims to last N turns to manage token limits.
    Each message: {"role": "user"|"model", "parts": [{"text": str}]}
    """
    # Keep only last max_turns messages
    if len(messages) > max_turns * 2:
        messages = messages[-(max_turns * 2):]

    # Ensure alternating roles (Gemini requires user/model alternation)
    cleaned = []
    last_role = None
    for msg in messages:
        role = msg.get("role")
        if role == last_role:
            # Merge consecutive same-role messages
            if cleaned:
                prev_text = cleaned[-1]["parts"][0]["text"]
                new_text = msg["parts"][0]["text"] if isinstance(msg["parts"], list) else msg["parts"]
                cleaned[-1]["parts"][0]["text"] = f"{prev_text}\n{new_text}"
        else:
            if isinstance(msg.get("parts"), list):
                cleaned.append(msg)
            else:
                cleaned.append({
                    "role": role,
                    "parts": [{"text": str(msg.get("parts", msg.get("content", "")))}],
                })
            last_role = role

    return cleaned


# ---------------------------------------------------------------------------
# Core Chat Function (streaming)
# ---------------------------------------------------------------------------

async def stream_copilot_response(
    user_message: str,
    conversation_history: list[dict],
    context: dict | None = None,
) -> AsyncGenerator[str, None]:
    """
    Stream HR Copilot response token by token.
    Used for SSE (Server-Sent Events) streaming to frontend.

    Yields text chunks as they arrive from Gemini.
    """
    context_block = build_context_block(context or {})
    system = HR_COPILOT_SYSTEM_PROMPT
    if context_block:
        system = f"{system}\n\n{context_block}"

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL,
        system_instruction=system,
    )

    history = prepare_conversation_history(conversation_history)

    chat = model.start_chat(history=history)

    try:
        response = chat.send_message(
            user_message,
            stream=True,
        )
        for chunk in response:
            if chunk.text:
                yield chunk.text
    except Exception as e:
        logger.error(f"HR Copilot streaming error: {e}")
        yield f"\n\n⚠️ I encountered an error processing your request. Please try again."


# ---------------------------------------------------------------------------
# Core Chat Function (non-streaming)
# ---------------------------------------------------------------------------

async def get_copilot_response(
    user_message: str,
    conversation_history: list[dict],
    context: dict | None = None,
) -> dict:
    """
    Get a complete (non-streaming) HR Copilot response.

    Returns:
    {
        "response": str,
        "tokens_used": int | None,
        "suggested_actions": [str],  # follow-up quick actions
        "intent_detected": str,      # what the user was trying to do
    }
    """
    context_block = build_context_block(context or {})
    system = HR_COPILOT_SYSTEM_PROMPT
    if context_block:
        system = f"{system}\n\n{context_block}"

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL,
        system_instruction=system,
    )

    history = prepare_conversation_history(conversation_history)
    chat = model.start_chat(history=history)

    try:
        response = chat.send_message(user_message)
        response_text = response.text.strip()

        return {
            "response": response_text,
            "tokens_used": None,  # Gemini free tier doesn't expose token counts easily
            "suggested_actions": _detect_follow_up_actions(user_message, response_text),
            "intent_detected": _detect_intent(user_message),
        }
    except Exception as e:
        logger.error(f"HR Copilot error: {e}")
        return {
            "response": "I'm having trouble processing that right now. Please try rephrasing or try again in a moment.",
            "tokens_used": None,
            "suggested_actions": [],
            "intent_detected": "unknown",
        }


# ---------------------------------------------------------------------------
# Quick Actions
# ---------------------------------------------------------------------------

async def execute_quick_action(
    action: QuickAction,
    params: dict,
    context: dict | None = None,
) -> dict:
    """
    Execute a predefined quick action with structured parameters.

    Params depend on action type:
    - draft_rejection: candidate_name, job_title, reason (optional)
    - summarize_team: team_members list, dept_name
    - attrition_risks: employees list with risk scores
    - generate_offer: candidate_name, job_title, salary, joining_date
    - performance_summary: employee list with scores

    Returns:
    {
        "action": str,
        "result": str,
        "formatted_output": str,
    }
    """
    logger.info(f"Executing quick action: {action.value}")

    prompt_template = QUICK_ACTION_PROMPTS.get(action.value)
    if not prompt_template:
        return {
            "action": action.value,
            "result": f"Quick action '{action.value}' not configured.",
            "formatted_output": "",
        }

    try:
        prompt = prompt_template.format(**params)
    except KeyError as e:
        return {
            "action": action.value,
            "result": f"Missing required parameter: {e}",
            "formatted_output": "",
        }

    genai.configure(api_key=settings.GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name=settings.GEMINI_MODEL,
        system_instruction=HR_COPILOT_SYSTEM_PROMPT,
    )

    try:
        response = model.generate_content(prompt)
        result_text = response.text.strip()
        return {
            "action": action.value,
            "result": result_text,
            "formatted_output": result_text,
        }
    except Exception as e:
        logger.error(f"Quick action '{action.value}' failed: {e}")
        return {
            "action": action.value,
            "result": "Could not complete this action. Please try again.",
            "formatted_output": "",
        }


# ---------------------------------------------------------------------------
# Intent Detection (lightweight, rule-based)
# ---------------------------------------------------------------------------

INTENT_KEYWORDS = {
    "draft_email": ["email", "write", "draft", "compose", "rejection", "offer letter"],
    "summarize": ["summarize", "summary", "overview", "how is", "how are"],
    "attrition": ["attrition", "risk", "leaving", "resign", "turnover", "quit"],
    "performance": ["performance", "review", "score", "rating", "appraisal"],
    "leave": ["leave", "time off", "vacation", "absence", "holiday"],
    "payroll": ["payroll", "salary", "pay", "compensation", "ctc"],
    "recruitment": ["candidate", "applicant", "hiring", "interview", "job posting"],
    "general_query": [],
}


def _detect_intent(message: str) -> str:
    message_lower = message.lower()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in message_lower for kw in keywords):
            return intent
    return "general_query"


def _detect_follow_up_actions(user_message: str, response: str) -> list[str]:
    """Suggest relevant follow-up quick actions based on conversation."""
    suggestions = []
    combined = (user_message + " " + response).lower()

    if any(w in combined for w in ["candidate", "applicant", "reject"]):
        suggestions.append("Draft rejection email")
    if any(w in combined for w in ["team", "department", "members"]):
        suggestions.append("Summarize my team")
    if any(w in combined for w in ["risk", "attrition", "leaving"]):
        suggestions.append("View attrition risks")
    if any(w in combined for w in ["offer", "join", "hired", "selected"]):
        suggestions.append("Generate offer letter")

    return suggestions[:3]


# ---------------------------------------------------------------------------
# Engine wrapper class and instance export
# ---------------------------------------------------------------------------

import uuid
from app.database import AsyncSessionLocal

class HRCopilotEngine:
    async def chat(
        self,
        message: str,
        session_id: str | None,
        user_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> dict:
        if not session_id:
            session_id = "default_session"
        
        if not hasattr(self, "_histories"):
            self._histories = {}
        history = self._histories.get(session_id, [])

        context = {}
        try:
            from app.models.auth import User
            from app.models.employee import Employee
            from sqlalchemy import select
            async with AsyncSessionLocal() as db:
                stmt = select(User).where(User.id == user_id)
                user = (await db.execute(stmt)).scalar_one_or_none()
                if user:
                    context["user_role"] = user.role.value if hasattr(user.role, "value") else str(user.role)
                    
                    emp_stmt = select(Employee).where(Employee.user_id == user_id)
                    emp = (await db.execute(emp_stmt)).scalar_one_or_none()
                    if emp:
                        context["user_name"] = f"{emp.first_name or ''} {emp.last_name or ''}".strip()
                    else:
                        context["user_name"] = user.email
        except Exception as e:
            logger.error(f"Failed to fetch user context for chat: {e}")

        res = await get_copilot_response(message, history, context)
        
        history.append({"role": "user", "parts": [{"text": message}]})
        history.append({"role": "model", "parts": [{"text": res.get("response", "")}]})
        self._histories[session_id] = history

        return res

    async def execute_action(
        self,
        action: str,
        params: dict,
        user_id: uuid.UUID,
        company_id: uuid.UUID,
    ) -> dict:
        try:
            quick_action = QuickAction(action)
        except ValueError:
            return {
                "action": action,
                "result": f"Action '{action}' is not supported.",
                "formatted_output": "",
            }
        
        context = {}
        try:
            from app.models.auth import User
            from app.models.employee import Employee
            from sqlalchemy import select
            async with AsyncSessionLocal() as db:
                stmt = select(User).where(User.id == user_id)
                user = (await db.execute(stmt)).scalar_one_or_none()
                if user:
                    context["user_role"] = user.role.value if hasattr(user.role, "value") else str(user.role)
                    
                    emp_stmt = select(Employee).where(Employee.user_id == user_id)
                    emp = (await db.execute(emp_stmt)).scalar_one_or_none()
                    if emp:
                        context["user_name"] = f"{emp.first_name or ''} {emp.last_name or ''}".strip()
                    else:
                        context["user_name"] = user.email
        except Exception as e:
            logger.error(f"Failed to fetch user context for quick action: {e}")

        return await execute_quick_action(quick_action, params, context)


hr_copilot_engine = HRCopilotEngine()

