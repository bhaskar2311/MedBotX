"""
MedBotX - Chatbot Service (LangChain + OpenAI)
Developed by Bhaskar Shivaji Kumbhar

Orchestrates:
  - LangChain conversation chain with memory context
  - OpenAI GPT-4o for response generation
  - Medical system prompt for safe, accurate responses
"""
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.config import settings
from app.core.logging_config import get_logger
from app.memory import memory_manager
from app.db.models import MemoryRecord

logger = get_logger("chatbot_service")

MEDICAL_SYSTEM_PROMPT = """You are MedBotX, an advanced AI-powered medical information assistant developed by Bhaskar Shivaji Kumbhar.

Your role:
- Provide accurate, evidence-based medical information to help users understand health topics
- Explain symptoms, conditions, medications, and general wellness advice clearly
- Always maintain a compassionate, professional, and reassuring tone
- Remember the user's medical context (allergies, conditions, medications) from memory

CRITICAL SAFETY RULES (follow strictly):
1. NEVER provide a diagnosis — always recommend consulting a licensed healthcare professional
2. NEVER recommend specific prescription dosages without noting a doctor must confirm
3. NEVER advise users to stop prescribed medications without medical guidance
4. For any emergency symptoms (chest pain, difficulty breathing, stroke signs), IMMEDIATELY advise calling emergency services (911 or local equivalent)
5. Always end responses with a reminder to consult a doctor for personal medical decisions

You have memory of past conversations and can reference the user's health context when relevant.
Developed by: Bhaskar Shivaji Kumbhar"""


class ChatbotService:
    def __init__(self):
        self._llm: Optional[ChatOpenAI] = None

    @property
    def llm(self) -> ChatOpenAI:
        if self._llm is None:
            self._llm = ChatOpenAI(
                model=settings.OPENAI_MODEL,
                temperature=settings.OPENAI_TEMPERATURE,
                max_tokens=settings.OPENAI_MAX_TOKENS,
                api_key=settings.OPENAI_API_KEY,
            )
        return self._llm

    def _build_messages(
        self,
        user_message: str,
        history: List[Dict[str, Any]],
        medical_context: Optional[Dict[str, Any]] = None,
    ) -> List:
        system_content = MEDICAL_SYSTEM_PROMPT
        if medical_context:
            context_parts = []
            if medical_context.get("allergies"):
                context_parts.append(f"Known allergies: {', '.join(medical_context['allergies'])}")
            if medical_context.get("conditions"):
                context_parts.append(f"Medical conditions: {', '.join(medical_context['conditions'])}")
            if medical_context.get("medications"):
                context_parts.append(f"Current medications: {', '.join(medical_context['medications'])}")
            if medical_context.get("age"):
                context_parts.append(f"Age: {medical_context['age']}")
            if medical_context.get("blood_type"):
                context_parts.append(f"Blood type: {medical_context['blood_type']}")
            if context_parts:
                system_content += "\n\nUser Medical Context:\n" + "\n".join(context_parts)

        messages = [SystemMessage(content=system_content)]

        for msg in history:
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "human":
                messages.append(HumanMessage(content=content))
            elif role == "ai":
                messages.append(AIMessage(content=content))

        messages.append(HumanMessage(content=user_message))
        return messages

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def _invoke_llm(self, messages: List) -> str:
        response = await self.llm.ainvoke(messages)
        return response.content

    async def get_response(
        self,
        user_message: str,
        session_id: str,
        permanent_memory: Optional[MemoryRecord] = None,
    ) -> Dict[str, Any]:
        temp_history = memory_manager.get_temp_memory(session_id)
        medical_context = permanent_memory.medical_context if permanent_memory else {}

        merged_history = memory_manager.merge_memories(permanent_memory, temp_history)

        messages = self._build_messages(user_message, merged_history, medical_context)

        logger.info(
            f"Sending request to OpenAI | session={session_id} | "
            f"history_len={len(merged_history)} | model={settings.OPENAI_MODEL}"
        )

        try:
            ai_response = await self._invoke_llm(messages)
        except Exception as exc:
            logger.error(f"OpenAI API error: {exc}")
            ai_response = (
                "I'm sorry, I'm experiencing technical difficulties right now. "
                "Please try again in a moment. If this is urgent, please contact a healthcare provider."
            )

        # Update temporary memory
        memory_manager.add_to_temp_memory(session_id, "human", user_message)
        memory_manager.add_to_temp_memory(session_id, "ai", ai_response)

        logger.info(f"Response generated successfully | session={session_id}")

        return {
            "response": ai_response,
            "session_id": session_id,
            "timestamp": datetime.now(timezone.utc),
            "model": settings.OPENAI_MODEL,
        }


chatbot_service = ChatbotService()
