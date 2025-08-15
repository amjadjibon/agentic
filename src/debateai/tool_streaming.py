import sys
import time
import json
from typing import Literal, Iterator
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from .state import ChatState
from .models import initialize_models
from .tools_registry import get_tools_for_agents, get_tool_descriptions


def execute_tool_call(tool_call) -> str:
    """Execute a tool call and return the result"""
    tools = get_tools_for_agents()
    tool_map = {tool.name: tool for tool in tools}
    
    # Handle different tool call formats
    if hasattr(tool_call, 'name'):
        tool_name = tool_call.name
        tool_args = tool_call.args if hasattr(tool_call, 'args') else {}
    elif isinstance(tool_call, dict):
        tool_name = tool_call.get('name', '')
        tool_args = tool_call.get('args', {})
    else:
        return f"Error: Invalid tool call format: {type(tool_call)}"
    
    if not tool_name:
        return "Error: Tool name not found in tool call"
    
    if tool_name not in tool_map:
        return f"Error: Tool '{tool_name}' not found. Available tools: {list(tool_map.keys())}"
    
    try:
        tool = tool_map[tool_name]
        result = tool.invoke(tool_args)
        return str(result)
    except Exception as e:
        return f"Error executing tool '{tool_name}': {str(e)}"


def left_agent_stream_response_with_tools(state: ChatState, model_choice: Literal["openai", "gemini"] = "openai") -> Iterator[ChatState]:
    """Left-aligned agent generates a progressive response with streaming and tool support"""
    openai_model, gemini_model = initialize_models(with_tools=True)
    
    # Choose specific model based on user preference
    model = openai_model if model_choice == "openai" else gemini_model

    left_persona = f"""You are a progressive, left-leaning political commentator and advocate. Your perspective emphasizes:
    - Social justice, equality, and human rights
    - Environmental protection and climate action
    - Economic policies that reduce inequality (progressive taxation, social safety nets)
    - Inclusive policies supporting marginalized communities
    - Government intervention to address systemic issues
    - International cooperation and diplomacy
    - Scientific consensus and evidence-based policy
    - Workers' rights and labor protections
    - Universal access to healthcare, education, and basic services
    
    Approach topics with empathy, focus on collective welfare, and advocate for systemic change to create a more equitable society. Be passionate but respectful in your arguments.
    
    You have access to the following tools to support your arguments with factual information:
    {get_tool_descriptions()}
    
    Use these tools when you need current information, statistics, or evidence to support your progressive viewpoints. Always cite your sources when using tool results."""

    messages = state["messages"].copy()
    if messages and isinstance(messages[0], HumanMessage):
        messages[0] = HumanMessage(
            content=left_persona + "\n\n" + messages[0].content
        )

    # Print speaker header
    print(f"\n🔴 Progressive Perspective:")
    
    # Stream the response
    accumulated_content = ""
    tool_calls = []
    
    try:
        for chunk in model.stream(messages):
            if hasattr(chunk, 'content') and chunk.content:
                print(chunk.content, end='', flush=True)
                accumulated_content += chunk.content
            elif hasattr(chunk, 'tool_calls') and chunk.tool_calls:
                tool_calls.extend(chunk.tool_calls)
            elif hasattr(chunk, 'additional_kwargs') and 'tool_calls' in chunk.additional_kwargs:
                tool_calls.extend(chunk.additional_kwargs['tool_calls'])
    except Exception as e:
        print(f"\n❌ Error during streaming: {str(e)}")
        accumulated_content = f"Error occurred during response generation: {str(e)}"

    # Handle tool calls if any
    new_messages = state["messages"].copy()
    
    if tool_calls:
        # Create AI message with tool calls
        ai_message = AIMessage(content=accumulated_content, tool_calls=tool_calls)
        new_messages.append(ai_message)
        
        # Execute tools and add results
        for tool_call in tool_calls:
            # Extract tool call information safely
            if hasattr(tool_call, 'name'):
                tool_name = tool_call.name
                tool_args = tool_call.args if hasattr(tool_call, 'args') else {}
                tool_id = tool_call.id if hasattr(tool_call, 'id') else f"tool_call_{len(new_messages)}"
            elif isinstance(tool_call, dict):
                tool_name = tool_call.get('name', 'unknown')
                tool_args = tool_call.get('args', {})
                tool_id = tool_call.get('id', f"tool_call_{len(new_messages)}")
            else:
                print(f"\n❌ Invalid tool call format: {type(tool_call)}")
                continue
            
            print(f"\n🔍 Using tool: {tool_name}")
            print(f"📝 Query: {tool_args}")
            
            result = execute_tool_call(tool_call)
            tool_message = ToolMessage(content=result, tool_call_id=tool_id)
            new_messages.append(tool_message)
            
            print(f"📊 Result: {result[:200]}{'...' if len(result) > 200 else ''}")
        
        # Get final response incorporating tool results
        print(f"\n🔴 Progressive Analysis (incorporating research):")
        
        final_accumulated = ""
        for chunk in model.stream(new_messages):
            if hasattr(chunk, 'content') and chunk.content:
                print(chunk.content, end='', flush=True)
                final_accumulated += chunk.content
        
        final_message = AIMessage(content=final_accumulated)
        new_messages.append(final_message)
    else:
        # No tool calls, just add the regular response
        response = AIMessage(content=accumulated_content)
        new_messages.append(response)

    print()  # New line after streaming
    print("-" * 40)

    final_state = {
        "messages": new_messages,
        "current_speaker": "right",
        "conversation_count": state["conversation_count"] + 1,
        "max_turns": state["max_turns"],
    }
    
    yield final_state


def right_agent_stream_response_with_tools(state: ChatState, model_choice: Literal["openai", "gemini"] = "gemini") -> Iterator[ChatState]:
    """Right-aligned agent generates a conservative response with streaming and tool support"""
    openai_model, gemini_model = initialize_models(with_tools=True)
    
    # Choose specific model based on user preference
    model = openai_model if model_choice == "openai" else gemini_model

    right_persona = f"""You are a conservative, right-leaning political commentator and advocate. Your perspective emphasizes:
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
    
    Approach topics with emphasis on proven traditions, practical solutions, and individual empowerment. Value stability, order, and incremental change. Be principled but respectful in your arguments.
    
    You have access to the following tools to support your arguments with factual information:
    {get_tool_descriptions()}
    
    Use these tools when you need current information, statistics, or evidence to support your conservative viewpoints. Always cite your sources when using tool results."""

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
    tool_calls = []
    
    try:
        for chunk in model.stream(messages):
            if hasattr(chunk, 'content') and chunk.content:
                print(chunk.content, end='', flush=True)
                accumulated_content += chunk.content
            elif hasattr(chunk, 'tool_calls') and chunk.tool_calls:
                tool_calls.extend(chunk.tool_calls)
            elif hasattr(chunk, 'additional_kwargs') and 'tool_calls' in chunk.additional_kwargs:
                tool_calls.extend(chunk.additional_kwargs['tool_calls'])
    except Exception as e:
        print(f"\n❌ Error during streaming: {str(e)}")
        accumulated_content = f"Error occurred during response generation: {str(e)}"

    # Handle tool calls if any
    new_messages = state["messages"].copy()
    
    if tool_calls:
        # Create AI message with tool calls
        ai_message = AIMessage(content=accumulated_content, tool_calls=tool_calls)
        new_messages.append(ai_message)
        
        # Execute tools and add results
        for tool_call in tool_calls:
            # Extract tool call information safely
            if hasattr(tool_call, 'name'):
                tool_name = tool_call.name
                tool_args = tool_call.args if hasattr(tool_call, 'args') else {}
                tool_id = tool_call.id if hasattr(tool_call, 'id') else f"tool_call_{len(new_messages)}"
            elif isinstance(tool_call, dict):
                tool_name = tool_call.get('name', 'unknown')
                tool_args = tool_call.get('args', {})
                tool_id = tool_call.get('id', f"tool_call_{len(new_messages)}")
            else:
                print(f"\n❌ Invalid tool call format: {type(tool_call)}")
                continue
            
            print(f"\n🔍 Using tool: {tool_name}")
            print(f"📝 Query: {tool_args}")
            
            result = execute_tool_call(tool_call)
            tool_message = ToolMessage(content=result, tool_call_id=tool_id)
            new_messages.append(tool_message)
            
            print(f"📊 Result: {result[:200]}{'...' if len(result) > 200 else ''}")
        
        # Get final response incorporating tool results
        print(f"\n🔵 Conservative Analysis (incorporating research):")
        
        final_accumulated = ""
        for chunk in model.stream(new_messages):
            if hasattr(chunk, 'content') and chunk.content:
                print(chunk.content, end='', flush=True)
                final_accumulated += chunk.content
        
        final_message = AIMessage(content=final_accumulated)
        new_messages.append(final_message)
    else:
        # No tool calls, just add the regular response
        response = AIMessage(content=accumulated_content)
        new_messages.append(response)

    print()  # New line after streaming
    print("-" * 40)

    final_state = {
        "messages": new_messages,
        "current_speaker": "left",
        "conversation_count": state["conversation_count"] + 1,
        "max_turns": state["max_turns"],
    }
    
    yield final_state


def run_streaming_debate_with_tools(topic: str, left_model: Literal["openai", "gemini"], right_model: Literal["openai", "gemini"], max_turns: int = 8):
    """Run a political debate with real-time streaming responses and tool support"""
    
    debate_prompt = f"""
    We're having a structured political debate on the topic: "{topic}"
    
    This will be a respectful debate between progressive (left) and conservative (right) perspectives.
    
    Each response should:
    1. Address the previous point made
    2. Present your political perspective clearly
    3. Use examples, evidence, and policy proposals
    4. Be passionate but respectful and constructive
    5. Stay true to your political alignment
    6. Use available tools to gather current facts and statistics when needed
    
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
    print("🛠️ Tools enabled: Web search available")
    print("=" * 60)

    # Show progress indicator
    print(f"📊 Progress: 0/{max_turns} turns")

    while state["conversation_count"] < max_turns:
        current_turn = state["conversation_count"] + 1
        
        if state["current_speaker"] == "left":
            # Stream left agent response with tools
            for updated_state in left_agent_stream_response_with_tools(state, left_model):
                state = updated_state
        else:
            # Stream right agent response with tools
            for updated_state in right_agent_stream_response_with_tools(state, right_model):
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


def run_streaming_discussion_with_tools(topic: str, left_model: Literal["openai", "gemini"], right_model: Literal["openai", "gemini"], max_turns: int = 6):
    """Run a political discussion with real-time streaming responses and tool support"""
    
    initial_message = HumanMessage(
        content=f"Let's have a political discussion about: {topic}. "
        f"Please share your perspectives from your political viewpoints and engage constructively. "
        f"Use available tools to gather current facts and statistics when needed."
    )

    state = {
        "messages": [initial_message],
        "current_speaker": "left",
        "conversation_count": 0,
        "max_turns": max_turns,
    }

    print(f"🏛️ Political Discussion: {topic}")
    print(f"🔴 Progressive ({left_model.upper()}) vs 🔵 Conservative ({right_model.upper()})")
    print("🛠️ Tools enabled: Web search available")
    print("=" * 60)
    print(f"🎯 Topic: {topic}")
    print("=" * 60)

    # Show progress indicator
    print(f"📊 Progress: 0/{max_turns} turns")

    while state["conversation_count"] < max_turns:
        current_turn = state["conversation_count"] + 1
        
        if state["current_speaker"] == "left":
            # Stream left agent response with tools
            for updated_state in left_agent_stream_response_with_tools(state, left_model):
                state = updated_state
        else:
            # Stream right agent response with tools
            for updated_state in right_agent_stream_response_with_tools(state, right_model):
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


def run_streaming_policy_analysis_with_tools(topic: str, left_model: Literal["openai", "gemini"], right_model: Literal["openai", "gemini"], max_turns: int = 10):
    """Run a policy analysis with real-time streaming responses and tool support"""
    
    policy_prompt = f"""
    Let's analyze the policy implications of: {topic}
    
    Please provide a thorough analysis from your political perspective, including:
    - Policy recommendations
    - Potential benefits and drawbacks
    - Implementation considerations
    - Long-term implications
    - How this aligns with your political philosophy
    - Current facts and statistics (use tools to gather recent data)
    
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
    print("🛠️ Tools enabled: Web search available")
    print("=" * 70)
    print(f"🎯 Policy Topic: {topic}")
    print("=" * 70)

    # Show progress indicator
    print(f"📊 Progress: 0/{max_turns} turns")

    while state["conversation_count"] < max_turns:
        current_turn = state["conversation_count"] + 1
        
        if state["current_speaker"] == "left":
            # Stream left agent response with tools
            for updated_state in left_agent_stream_response_with_tools(state, left_model):
                state = updated_state
        else:
            # Stream right agent response with tools
            for updated_state in right_agent_stream_response_with_tools(state, right_model):
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