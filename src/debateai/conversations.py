from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage
from .graph import create_left_right_debate_graph, create_political_persona_graph, create_custom_political_graph


def run_political_debate(topic: str, max_turns: int = 8):
    """Run a political debate between left and right perspectives with default models"""
    return run_political_debate_with_models(topic, "openai", "gemini", max_turns)


def run_political_debate_with_models(topic: str, left_model: Literal["openai", "gemini"], right_model: Literal["openai", "gemini"], max_turns: int = 8):
    """Run a political debate between left and right perspectives with specific models"""
    app = create_left_right_debate_graph(left_model, right_model)

    debate_prompt = f"""
    We're having a structured political debate on the topic: "{topic}"
    
    This will be a respectful debate between progressive (left) and conservative (right) perspectives.
    
    Each response should:
    1. Address the previous point made
    2. Present your political perspective clearly
    3. Use examples, evidence, and policy proposals
    4. Be passionate but respectful and constructive
    5. Stay true to your political alignment
    
    Let's begin the debate!
    """

    initial_state = {
        "messages": [HumanMessage(content=debate_prompt)],
        "current_speaker": "left",
        "conversation_count": 0,
        "max_turns": max_turns,
    }

    print(f"🗳️ Political Debate Topic: {topic}")
    print(f"🔴 Progressive ({left_model.upper()}) vs 🔵 Conservative ({right_model.upper()})")
    print("=" * 60)

    final_state = app.invoke(initial_state)

    for i, message in enumerate(final_state["messages"]):
        if isinstance(message, HumanMessage) and i == 0:
            continue
        elif isinstance(message, AIMessage):
            speaker = (
                "🔴 Progressive Perspective"
                if (i - 1) % 2 == 0
                else "🔵 Conservative Perspective"
            )
            print(f"\n{speaker}:")
            print(f"{message.content}")
            print("-" * 40)

    return final_state


def run_political_discussion(initial_topic: str, max_turns: int = 6):
    """Run a general political discussion between left and right perspectives with default models"""
    return run_political_discussion_with_models(initial_topic, "openai", "gemini", max_turns)


def run_political_discussion_with_models(initial_topic: str, left_model: Literal["openai", "gemini"], right_model: Literal["openai", "gemini"], max_turns: int = 6):
    """Run a general political discussion between left and right perspectives with specific models"""
    app = create_left_right_debate_graph(left_model, right_model)

    initial_message = HumanMessage(
        content=f"Let's have a political discussion about: {initial_topic}. "
        f"Please share your perspectives from your political viewpoints and engage constructively."
    )

    initial_state = {
        "messages": [initial_message],
        "current_speaker": "left",
        "conversation_count": 0,
        "max_turns": max_turns,
    }

    print(f"🏛️ Political Discussion: {initial_topic}")
    print(f"🔴 Progressive ({left_model.upper()}) vs 🔵 Conservative ({right_model.upper()})")
    print("=" * 60)

    final_state = app.invoke(initial_state)

    for i, message in enumerate(final_state["messages"]):
        if isinstance(message, HumanMessage):
            print(f"🎯 Topic: {message.content}")
        elif isinstance(message, AIMessage):
            speaker = "🔴 Progressive" if i % 2 == 1 else "🔵 Conservative"
            print(f"\n{speaker}:")
            print(f"{message.content}")
            print("-" * 40)

    return final_state


def run_policy_analysis(policy_topic: str, max_turns: int = 10):
    """Run a policy analysis from both left and right perspectives with default models"""
    return run_policy_analysis_with_models(policy_topic, "openai", "gemini", max_turns)


def run_policy_analysis_with_models(policy_topic: str, left_model: Literal["openai", "gemini"], right_model: Literal["openai", "gemini"], max_turns: int = 10):
    """Run a policy analysis from both left and right perspectives with specific models"""
    app = create_left_right_debate_graph(left_model, right_model)

    policy_prompt = f"""
    Let's analyze the policy implications of: {policy_topic}
    
    Please provide a thorough analysis from your political perspective, including:
    - Policy recommendations
    - Potential benefits and drawbacks
    - Implementation considerations
    - Long-term implications
    - How this aligns with your political philosophy
    
    Let's have a substantive policy discussion.
    """

    initial_state = {
        "messages": [HumanMessage(content=policy_prompt)],
        "current_speaker": "left",
        "conversation_count": 0,
        "max_turns": max_turns,
    }

    print(f"📋 Policy Analysis: {policy_topic}")
    print(f"🔴 Progressive Analysis ({left_model.upper()}) vs 🔵 Conservative Analysis ({right_model.upper()})")
    print("=" * 70)

    final_state = app.invoke(initial_state)

    for i, message in enumerate(final_state["messages"]):
        if isinstance(message, HumanMessage) and i == 0:
            print(f"🎯 Policy Topic: {policy_topic}")
            print("=" * 70)
        elif isinstance(message, AIMessage):
            speaker = "🔴 Progressive Analysis" if (i - 1) % 2 == 0 else "🔵 Conservative Analysis"
            print(f"\n{speaker}:")
            print(f"{message.content}")
            print("-" * 50)

    return final_state


def create_custom_political_conversation(
    left_persona: str, right_persona: str, topic: str, max_turns: int = 6
):
    """Create a custom political conversation with specific personas for each side using default models"""
    return create_custom_political_conversation_with_models(left_persona, right_persona, topic, "openai", "gemini", max_turns)


def create_custom_political_conversation_with_models(
    left_persona: str, right_persona: str, topic: str, left_model: Literal["openai", "gemini"], right_model: Literal["openai", "gemini"], max_turns: int = 6
):
    """Create a custom political conversation with specific personas and models for each side"""
    app = create_custom_political_graph(left_persona, right_persona, left_model, right_model)

    initial_state = {
        "messages": [HumanMessage(content=f"Let's discuss: {topic}")],
        "current_speaker": "left",
        "conversation_count": 0,
        "max_turns": max_turns,
    }

    print(f"🎭 Custom Political Conversation: {topic}")
    print(f"🔴 Left ({left_model.upper()}): {left_persona[:50]}...")
    print(f"🔵 Right ({right_model.upper()}): {right_persona[:50]}...")
    print("=" * 70)

    final_state = app.invoke(initial_state)

    for i, message in enumerate(final_state["messages"]):
        if isinstance(message, HumanMessage):
            print(f"🎯 Topic: {message.content}")
        elif isinstance(message, AIMessage):
            speaker = "🔴 Left" if i % 2 == 1 else "🔵 Right"
            print(f"\n{speaker}:")
            print(f"{message.content}")
            print("-" * 50)

    return final_state
