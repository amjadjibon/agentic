from typing import Literal
from langchain_core.messages import HumanMessage
from ..state import ChatState
from ..models import initialize_models


def left_agent_response(state: ChatState, model_choice: Literal["openai", "gemini"] = "openai") -> ChatState:
    """Left-aligned agent generates a progressive response"""
    openai_model, gemini_model = initialize_models()
    
    # Choose specific model based on user preference
    model = openai_model if model_choice == "openai" else gemini_model

    left_persona = """You are a progressive, left-leaning political commentator and advocate. Your perspective emphasizes:
    - Social justice, equality, and human rights
    - Environmental protection and climate action
    - Economic policies that reduce inequality (progressive taxation, social safety nets)
    - Inclusive policies supporting marginalized communities
    - Government intervention to address systemic issues
    - International cooperation and diplomacy
    - Scientific consensus and evidence-based policy
    - Workers' rights and labor protections
    - Universal access to healthcare, education, and basic services
    
    Approach topics with empathy, focus on collective welfare, and advocate for systemic change to create a more equitable society. Be passionate but respectful in your arguments."""

    messages = state["messages"].copy()
    if messages and isinstance(messages[0], HumanMessage):
        messages[0] = HumanMessage(
            content=left_persona + "\n\n" + messages[0].content
        )

    response = model.invoke(messages)
    new_messages = state["messages"] + [response]

    return {
        "messages": new_messages,
        "current_speaker": "right",
        "conversation_count": state["conversation_count"] + 1,
        "max_turns": state["max_turns"],
    }


def left_agent_with_custom_persona(state: ChatState, persona: str, model_choice: Literal["openai", "gemini"] = "openai") -> ChatState:
    """Left-aligned agent with custom persona"""
    openai_model, gemini_model = initialize_models()
    model = openai_model if model_choice == "openai" else gemini_model

    messages = state["messages"].copy()
    if messages and isinstance(messages[0], HumanMessage):
        messages[0] = HumanMessage(
            content=persona + "\n\n" + messages[0].content
        )

    response = model.invoke(messages)
    new_messages = state["messages"] + [response]

    return {
        "messages": new_messages,
        "current_speaker": "right",
        "conversation_count": state["conversation_count"] + 1,
        "max_turns": state["max_turns"],
    }
