from typing import Literal
from langgraph.graph import StateGraph, END
from .state import ChatState
from .agents.left_agent import left_agent_response, left_agent_with_custom_persona
from .agents.right_agent import right_agent_response, right_agent_with_custom_persona


def should_continue(state: ChatState) -> str:
    """Determine if the conversation should continue"""
    if state["conversation_count"] >= state["max_turns"]:
        return "end"
    else:
        return state["current_speaker"]


def create_left_right_debate_graph(left_model: Literal["openai", "gemini"] = "openai", right_model: Literal["openai", "gemini"] = "gemini"):
    """Create and configure the LangGraph for Left vs Right political debate with specific models"""
    def left_wrapper(state: ChatState) -> ChatState:
        return left_agent_response(state, left_model)
    
    def right_wrapper(state: ChatState) -> ChatState:
        return right_agent_response(state, right_model)

    workflow = StateGraph(ChatState)

    workflow.add_node("left", left_wrapper)
    workflow.add_node("right", right_wrapper)

    workflow.set_entry_point("left")

    workflow.add_conditional_edges(
        "left", should_continue, {"right": "right", "end": END}
    )

    workflow.add_conditional_edges(
        "right", should_continue, {"left": "left", "end": END}
    )

    app = workflow.compile()
    return app


def create_political_persona_graph(left_model: Literal["openai", "gemini"] = "openai", right_model: Literal["openai", "gemini"] = "gemini"):
    """Create a political debate with default left/right personas and specific models"""
    def left_wrapper(state: ChatState) -> ChatState:
        return left_agent_response(state, left_model)
    
    def right_wrapper(state: ChatState) -> ChatState:
        return right_agent_response(state, right_model)

    workflow = StateGraph(ChatState)
    workflow.add_node("left", left_wrapper)
    workflow.add_node("right", right_wrapper)
    workflow.set_entry_point("left")

    workflow.add_conditional_edges(
        "left", should_continue, {"right": "right", "end": END}
    )

    workflow.add_conditional_edges(
        "right", should_continue, {"left": "left", "end": END}
    )

    return workflow.compile()


def create_custom_political_graph(left_persona: str, right_persona: str, left_model: Literal["openai", "gemini"] = "openai", right_model: Literal["openai", "gemini"] = "gemini"):
    """Create a custom political debate with specific personas and models for each side"""
    def custom_left_response(state: ChatState) -> ChatState:
        return left_agent_with_custom_persona(state, left_persona, left_model)

    def custom_right_response(state: ChatState) -> ChatState:
        return right_agent_with_custom_persona(state, right_persona, right_model)

    workflow = StateGraph(ChatState)
    workflow.add_node("left", custom_left_response)
    workflow.add_node("right", custom_right_response)
    workflow.set_entry_point("left")

    workflow.add_conditional_edges(
        "left", should_continue, {"right": "right", "end": END}
    )

    workflow.add_conditional_edges(
        "right", should_continue, {"left": "left", "end": END}
    )

    return workflow.compile()
