from typing import Literal
from langchain_core.messages import HumanMessage
from ..state import ChatState
from ..models import initialize_models


def right_agent_response(state: ChatState, model_choice: Literal["openai", "gemini"] = "gemini") -> ChatState:
    """Right-aligned agent generates a conservative response"""
    openai_model, gemini_model = initialize_models()
    
    # Choose specific model based on user preference
    model = openai_model if model_choice == "openai" else gemini_model

    right_persona = """You are a conservative, right-leaning political commentator and advocate. Your perspective emphasizes:
    - Individual liberty, personal responsibility, and limited government
    - Free market capitalism and economic freedom
    - Traditional values, family structures, and cultural continuity
    - Strong national defense and law enforcement
    - Constitutional principles and rule of law
    - Fiscal responsibility and balanced budgets
    - Local governance and states' rights
    - Meritocracy and equal opportunity (not equal outcomes)
    - Property rights and entrepreneurship
    - Skepticism of rapid social change and government overreach
    
    Approach topics with emphasis on proven traditions, practical solutions, and individual empowerment. Value stability, order, and incremental change. Be principled but respectful in your arguments."""

    messages = state["messages"].copy()
    if len(messages) > 1:
        system_context = HumanMessage(content=right_persona)
        messages = [system_context] + messages[1:]
    elif messages and isinstance(messages[0], HumanMessage):
        messages[0] = HumanMessage(
            content=right_persona + "\n\n" + messages[0].content
        )

    response = model.invoke(messages)
    new_messages = state["messages"] + [response]

    return {
        "messages": new_messages,
        "current_speaker": "left",
        "conversation_count": state["conversation_count"] + 1,
        "max_turns": state["max_turns"],
    }


def right_agent_with_custom_persona(state: ChatState, persona: str, model_choice: Literal["openai", "gemini"] = "gemini") -> ChatState:
    """Right-aligned agent with custom persona"""
    openai_model, gemini_model = initialize_models()
    model = openai_model if model_choice == "openai" else gemini_model

    messages = state["messages"].copy()
    if len(messages) > 1:
        system_context = HumanMessage(content=persona)
        messages = [system_context] + messages[1:]
    elif messages and isinstance(messages[0], HumanMessage):
        messages[0] = HumanMessage(
            content=persona + "\n\n" + messages[0].content
        )

    response = model.invoke(messages)
    new_messages = state["messages"] + [response]

    return {
        "messages": new_messages,
        "current_speaker": "left",
        "conversation_count": state["conversation_count"] + 1,
        "max_turns": state["max_turns"],
    }
