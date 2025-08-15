import sys
import time
from typing import Literal, Iterator, Any
from langchain_core.messages import HumanMessage, AIMessage
from .state import ChatState
from .models import initialize_models


def stream_text(text: str, delay: float = 0.01):
    """Stream text to terminal with typing effect"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)


def left_agent_stream_response(state: ChatState, model_choice: Literal["openai", "gemini"] = "openai") -> Iterator[ChatState]:
    """Left-aligned agent generates a progressive response with streaming"""
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

    # Print speaker header
    print(f"\n🔴 Progressive Perspective:")
    
    # Stream the response
    accumulated_content = ""
    for chunk in model.stream(messages):
        if hasattr(chunk, 'content') and chunk.content:
            print(chunk.content, end='', flush=True)
            accumulated_content += chunk.content

    print()  # New line after streaming
    print("-" * 40)

    # Create the final AIMessage with accumulated content
    response = AIMessage(content=accumulated_content)
    new_messages = state["messages"] + [response]

    final_state = {
        "messages": new_messages,
        "current_speaker": "right",
        "conversation_count": state["conversation_count"] + 1,
        "max_turns": state["max_turns"],
    }
    
    yield final_state


def right_agent_stream_response(state: ChatState, model_choice: Literal["openai", "gemini"] = "gemini") -> Iterator[ChatState]:
    """Right-aligned agent generates a conservative response with streaming"""
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

    # Print speaker header
    print(f"\n🔵 Conservative Perspective:")
    
    # Stream the response
    accumulated_content = ""
    for chunk in model.stream(messages):
        if hasattr(chunk, 'content') and chunk.content:
            print(chunk.content, end='', flush=True)
            accumulated_content += chunk.content

    print()  # New line after streaming
    print("-" * 40)

    # Create the final AIMessage with accumulated content
    response = AIMessage(content=accumulated_content)
    new_messages = state["messages"] + [response]

    final_state = {
        "messages": new_messages,
        "current_speaker": "left",
        "conversation_count": state["conversation_count"] + 1,
        "max_turns": state["max_turns"],
    }
    
    yield final_state


def should_continue_streaming(state: ChatState) -> str:
    """Determine if the conversation should continue in streaming mode"""
    if state["conversation_count"] >= state["max_turns"]:
        return "end"
    else:
        return state["current_speaker"]


def run_streaming_debate(topic: str, left_model: Literal["openai", "gemini"], right_model: Literal["openai", "gemini"], max_turns: int = 8):
    """Run a political debate with real-time streaming responses"""
    
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

    state = {
        "messages": [HumanMessage(content=debate_prompt)],
        "current_speaker": "left",
        "conversation_count": 0,
        "max_turns": max_turns,
    }

    print(f"🗳️ Political Debate Topic: {topic}")
    print(f"🔴 Progressive ({left_model.upper()}) vs 🔵 Conservative ({right_model.upper()})")
    print("=" * 60)

    # Show progress indicator
    print(f"📊 Progress: 0/{max_turns} turns")

    while state["conversation_count"] < max_turns:
        current_turn = state["conversation_count"] + 1
        
        if state["current_speaker"] == "left":
            # Stream left agent response
            for updated_state in left_agent_stream_response(state, left_model):
                state = updated_state
        else:
            # Stream right agent response  
            for updated_state in right_agent_stream_response(state, right_model):
                state = updated_state

        # Update progress
        progress_bar = "█" * current_turn + "░" * (max_turns - current_turn)
        print(f"\n📊 Progress: [{progress_bar}] {current_turn}/{max_turns}")
        
        # Small delay between turns for readability
        time.sleep(0.5)

    print("\n" + "=" * 70)
    print("🏁 Debate completed!")
    print("=" * 70)
    
    return state


def run_streaming_discussion(topic: str, left_model: Literal["openai", "gemini"], right_model: Literal["openai", "gemini"], max_turns: int = 6):
    """Run a political discussion with real-time streaming responses"""
    
    initial_message = HumanMessage(
        content=f"Let's have a political discussion about: {topic}. "
        f"Please share your perspectives from your political viewpoints and engage constructively."
    )

    state = {
        "messages": [initial_message],
        "current_speaker": "left",
        "conversation_count": 0,
        "max_turns": max_turns,
    }

    print(f"🏛️ Political Discussion: {topic}")
    print(f"🔴 Progressive ({left_model.upper()}) vs 🔵 Conservative ({right_model.upper()})")
    print("=" * 60)
    print(f"🎯 Topic: {topic}")
    print("=" * 60)

    # Show progress indicator
    print(f"📊 Progress: 0/{max_turns} turns")

    while state["conversation_count"] < max_turns:
        current_turn = state["conversation_count"] + 1
        
        if state["current_speaker"] == "left":
            # Stream left agent response
            for updated_state in left_agent_stream_response(state, left_model):
                state = updated_state
        else:
            # Stream right agent response  
            for updated_state in right_agent_stream_response(state, right_model):
                state = updated_state

        # Update progress
        progress_bar = "█" * current_turn + "░" * (max_turns - current_turn)
        print(f"\n📊 Progress: [{progress_bar}] {current_turn}/{max_turns}")
        
        # Small delay between turns for readability
        time.sleep(0.5)

    print("\n" + "=" * 70)
    print("🏁 Discussion completed!")
    print("=" * 70)
    
    return state


def run_streaming_policy_analysis(topic: str, left_model: Literal["openai", "gemini"], right_model: Literal["openai", "gemini"], max_turns: int = 10):
    """Run a policy analysis with real-time streaming responses"""
    
    policy_prompt = f"""
    Let's analyze the policy implications of: {topic}
    
    Please provide a thorough analysis from your political perspective, including:
    - Policy recommendations
    - Potential benefits and drawbacks
    - Implementation considerations
    - Long-term implications
    - How this aligns with your political philosophy
    
    Let's have a substantive policy discussion.
    """

    state = {
        "messages": [HumanMessage(content=policy_prompt)],
        "current_speaker": "left",
        "conversation_count": 0,
        "max_turns": max_turns,
    }

    print(f"📋 Policy Analysis: {topic}")
    print(f"🔴 Progressive Analysis ({left_model.upper()}) vs 🔵 Conservative Analysis ({right_model.upper()})")
    print("=" * 70)
    print(f"🎯 Policy Topic: {topic}")
    print("=" * 70)

    # Show progress indicator
    print(f"📊 Progress: 0/{max_turns} turns")

    while state["conversation_count"] < max_turns:
        current_turn = state["conversation_count"] + 1
        
        if state["current_speaker"] == "left":
            # Stream left agent response
            for updated_state in left_agent_stream_response(state, left_model):
                state = updated_state
        else:
            # Stream right agent response  
            for updated_state in right_agent_stream_response(state, right_model):
                state = updated_state

        # Update progress
        progress_bar = "█" * current_turn + "░" * (max_turns - current_turn)
        print(f"\n📊 Progress: [{progress_bar}] {current_turn}/{max_turns}")
        
        # Small delay between turns for readability
        time.sleep(0.5)

    print("\n" + "=" * 70)
    print("🏁 Policy analysis completed!")
    print("=" * 70)
    
    return state