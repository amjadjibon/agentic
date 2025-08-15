import sys
import time
from typing import Iterator, Optional, TYPE_CHECKING
from langchain_core.messages import HumanMessage
from .state import ChatState
from .agents.left_agent import create_left_agent
from .agents.right_agent import create_right_agent

if TYPE_CHECKING:
    from .rich_ui import DebateUI


def should_continue_streaming(state: ChatState) -> str:
    """Determine if the conversation should continue in streaming mode"""
    if state["conversation_count"] >= state["max_turns"]:
        return "end"
    else:
        return state["current_speaker"]


def run_streaming_debate(topic: str, left_model: str, right_model: str, max_turns: int = 8, with_tools: bool = False, debate_type: str = "debate", ui: Optional['DebateUI'] = None):
    """Run a political debate with real-time streaming responses"""
    
    # Create agents
    left_agent = create_left_agent(left_model)
    right_agent = create_right_agent(right_model)
    
    # Set up initial prompt based on debate type
    if debate_type == "debate":
        initial_prompt = f"""
Topic for debate: "{topic}"

This is a structured political debate between progressive and conservative perspectives. The goal is to engage in substantive, respectful argumentation where each side:

1. Directly responds to and addresses the opponent's specific arguments
2. Presents clear evidence, examples, and reasoning to support their position
3. Challenges the opposing viewpoint with concrete counter-arguments
4. Builds a coherent case throughout the debate
5. Maintains respectful but passionate discourse
{'6. Uses web search tools to find current facts and statistics when needed' if with_tools else ''}

Progressive participant: Begin by presenting your opening argument on this topic, including specific policy positions and evidence.
        """
        header = f"🗳️ Political Debate Topic: {topic}"
    elif debate_type == "discussion":
        initial_prompt = f"Let's have a political discussion about: {topic}. Please share your perspectives from your political viewpoints and engage constructively.{'Use available tools to gather current facts and statistics when needed.' if with_tools else ''}"
        header = f"🏛️ Political Discussion: {topic}"
    else:  # policy analysis
        initial_prompt = f"""
Let's analyze the policy implications of: {topic}

Please provide a thorough analysis from your political perspective, including:
- Policy recommendations
- Potential benefits and drawbacks
- Implementation considerations
- Long-term implications
- How this aligns with your political philosophy
{'- Current facts and statistics (use tools to gather recent data)' if with_tools else ''}

Let's have a substantive policy discussion.
        """
        header = f"📋 Policy Analysis: {topic}"
    
    state = {
        "messages": [HumanMessage(content=initial_prompt)],
        "current_speaker": "left",
        "conversation_count": 0,
        "max_turns": max_turns,
    }
    
    # Display header - handled by UI in main function
    if ui:
        ui.show_progress(0, max_turns)
    else:
        print(header)
        print(f"🔴 Progressive ({left_model.upper()}) vs 🔵 Conservative ({right_model.upper()})")
        if with_tools:
            print("🛠️ Tools enabled: Web search available")
        print("=" * 70)
        print(f"📊 Progress: 0/{max_turns} turns")
    
    while state["conversation_count"] < max_turns:
        current_turn = state["conversation_count"] + 1
        
        if state["current_speaker"] == "left":
            # Stream left agent response
            for updated_state in left_agent.stream_response(state, with_tools, ui):
                state = updated_state
        else:
            # Stream right agent response  
            for updated_state in right_agent.stream_response(state, with_tools, ui):
                state = updated_state
        
        # Update progress
        if ui:
            ui.show_progress(current_turn, max_turns)
        else:
            progress_bar = "█" * current_turn + "░" * (max_turns - current_turn)
            print(f"\n📊 Progress: [{progress_bar}] {current_turn}/{max_turns}")
        
        # Small delay between turns for readability
        time.sleep(0.5)
    
    # Completion message handled by UI in main function
    if not ui:
        print("\n" + "=" * 70)
        if debate_type == "debate":
            print("🏁 Debate completed!")
        elif debate_type == "discussion":
            print("🏁 Discussion completed!")
        else:
            print("🏁 Policy analysis completed!")
        print("=" * 70)
    
    return state


def run_custom_streaming_debate(topic: str, left_model: str, right_model: str, left_persona: str, right_persona: str, max_turns: int = 8, with_tools: bool = False, ui: Optional['DebateUI'] = None):
    """Run a custom political debate with specific personas"""
    
    # Create custom agents
    left_agent = create_left_agent(left_model, left_persona)
    right_agent = create_right_agent(right_model, right_persona)
    
    initial_prompt = f"""
We're having a political debate on the topic: "{topic}"

This will be a respectful debate between the specified perspectives.

Each response should:
1. Address the previous point made
2. Present your assigned perspective clearly
3. Use examples, evidence, and policy proposals
4. Be passionate but respectful and constructive
5. Stay true to your assigned alignment
{'6. Use available tools to gather current facts and statistics when needed' if with_tools else ''}

Let's begin the debate!
    """
    
    state = {
        "messages": [HumanMessage(content=initial_prompt)],
        "current_speaker": "left",
        "conversation_count": 0,
        "max_turns": max_turns,
    }
    
    # Display header - handled by UI in main function  
    if ui:
        ui.show_progress(0, max_turns)
    else:
        print(f"🗳️ Custom Political Debate: {topic}")
        print(f"🔴 Left Perspective ({left_model.upper()}) vs 🔵 Right Perspective ({right_model.upper()})")
        if with_tools:
            print("🛠️ Tools enabled: Web search available")
        print("=" * 70)
        print(f"📊 Progress: 0/{max_turns} turns")
    
    while state["conversation_count"] < max_turns:
        current_turn = state["conversation_count"] + 1
        
        if state["current_speaker"] == "left":
            # Stream left agent response
            for updated_state in left_agent.stream_response(state, with_tools, ui):
                state = updated_state
        else:
            # Stream right agent response  
            for updated_state in right_agent.stream_response(state, with_tools, ui):
                state = updated_state
        
        # Update progress
        if ui:
            ui.show_progress(current_turn, max_turns)
        else:
            progress_bar = "█" * current_turn + "░" * (max_turns - current_turn)
            print(f"\n📊 Progress: [{progress_bar}] {current_turn}/{max_turns}")
        
        # Small delay between turns for readability
        time.sleep(0.5)
    
    # Completion message handled by UI in main function
    if not ui:
        print("\n" + "=" * 70)
        print("🏁 Custom debate completed!")
        print("=" * 70)
    
    return state
