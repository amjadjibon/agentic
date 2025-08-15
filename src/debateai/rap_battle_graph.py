"""Rap battle orchestration graph"""

import time
from typing import Optional, TYPE_CHECKING

from langchain_core.messages import HumanMessage, AIMessage

from debateai.rappers import get_rapper_agent, get_available_rappers
from debateai.rappers.battle_judge import create_rap_battle_judge

if TYPE_CHECKING:
    from debateai.rich_ui import DebateUI


def run_rap_battle(
    topic: str, 
    rapper1_id: str, 
    rapper2_id: str, 
    model1: str, 
    model2: str, 
    max_rounds: int = 3, 
    with_tools: bool = False, 
    ui: Optional['DebateUI'] = None, 
    with_judge: bool = True, 
    judge_model: str = "openai-gpt4o"
):
    """Run a rap battle between two legendary rappers"""
    
    # Get rapper info
    available_rappers = get_available_rappers()
    rapper1_info = available_rappers[rapper1_id]
    rapper2_info = available_rappers[rapper2_id]
    
    # Create rapper agents
    rapper1_agent = get_rapper_agent(rapper1_id, model1)
    rapper2_agent = get_rapper_agent(rapper2_id, model2)
    judge_agent = create_rap_battle_judge(judge_model) if with_judge else None
    
    # Set up battle topic
    battle_prompt = f"""
🎤 RAP BATTLE TOPIC: "{topic}"

This is an intense rap battle between two legendary rappers. Each rapper will drop verses in alternating rounds, trying to outdo their opponent with superior bars, wordplay, and crowd appeal.

BATTLE RULES:
- Each round should be 8-16 bars
- Address your opponent directly
- Use the battle topic as inspiration but don't limit yourself
- Bring your signature style and energy
- Make it quotable and memorable
- This is competitive - hold nothing back!

ROUND FORMAT:
- Round 1: Opening statements/first verses
- Round 2: Response and escalation
- Round 3: Final round/closer (if applicable)

{rapper1_info['name']} ({rapper1_info['icon']}) vs {rapper2_info['name']} ({rapper2_info['icon']})

LET THE BATTLE BEGIN!
    """
    
    state = {
        "messages": [HumanMessage(content=battle_prompt)],
        "current_speaker": "rapper1",
        "conversation_count": 0,
        "max_turns": max_rounds * 2,  # Each rapper gets max_rounds verses
    }
    
    # Display battle header
    if ui:
        ui.show_progress(0, max_rounds * 2)
    else:
        print("🎤" * 50)
        print(f"🔥 RAP BATTLE: {topic}")
        print(f"{rapper1_info['icon']} {rapper1_info['name']} vs {rapper2_info['icon']} {rapper2_info['name']}")
        if with_tools:
            print("🛠️ Research tools enabled")
        if with_judge:
            print(f"🏆 Judge: {judge_model.upper()}")
        print("🎤" * 50)
        print(f"📊 Battle Progress: 0/{max_rounds * 2} rounds")
    
    # Track battle context for judge
    battle_context = []
    current_round = 1
    
    while state["conversation_count"] < state["max_turns"]:
        turn_number = state["conversation_count"] + 1
        
        if state["current_speaker"] == "rapper1":
            # Rapper 1's turn
            rapper1_agent.next_rapper = "rapper2"
            for updated_state in rapper1_agent.stream_response(state, with_tools, ui):
                state = updated_state
            current_rapper_name = rapper1_info['name']
            next_speaker = "rapper2"
        else:
            # Rapper 2's turn
            rapper2_agent.next_rapper = "rapper1"
            for updated_state in rapper2_agent.stream_response(state, with_tools, ui):
                state = updated_state
            current_rapper_name = rapper2_info['name']
            next_speaker = "rapper1"
        
        # Judge evaluation if enabled
        if judge_agent and state["messages"]:
            latest_message = state["messages"][-1]
            if isinstance(latest_message, AIMessage):
                # Judge evaluates the round
                judge_agent.evaluate_round(
                    verse_content=latest_message.content,
                    round_number=current_round,
                    rapper_name=current_rapper_name,
                    battle_context=battle_context,
                    ui=ui
                )
                
                # Update battle context
                battle_context.append(f"{current_rapper_name}: {latest_message.content[:150]}...")
        
        # Update round counter after both rappers have gone
        if state["current_speaker"] == "rapper2":
            current_round += 1
        
        # Update state for next turn
        state["current_speaker"] = next_speaker
        
        # Update progress
        if ui:
            ui.show_progress(turn_number, state["max_turns"])
        else:
            progress_bar = "🔥" * turn_number + "░" * (state["max_turns"] - turn_number)
            print(f"\n📊 Battle Progress: [{progress_bar}] {turn_number}/{state['max_turns']}")
        
        # Small delay between rounds
        time.sleep(0.8)
    
    # Final judge decision if enabled
    if judge_agent:
        final_judgment = judge_agent.finalize_judgment(
            rapper1_name=rapper1_info['name'],
            rapper2_name=rapper2_info['name'],
            ui=ui
        )
        # Add judge data to state for export
        state["judge_scores"] = judge_agent.get_scoreboard()
        state["rapper1_name"] = rapper1_info['name']
        state["rapper2_name"] = rapper2_info['name']
    
    # Battle completion
    if not ui:
        print("\n" + "🎤" * 50)
        print("🏁 RAP BATTLE COMPLETED!")
        print("🎤" * 50)
    
    return state


def get_rap_battle_topic_suggestions():
    """Get suggested rap battle topics"""
    return [
        "Who's the real king of hip-hop?",
        "East Coast vs West Coast supremacy",
        "Old school vs new school rap",
        "Who has the better flow?",
        "Street credibility vs commercial success", 
        "Lyrical complexity vs crowd appeal",
        "Who influenced hip-hop culture more?",
        "Best rapper alive debate",
        "Who has the better discography?",
        "Freestyle vs written bars supremacy"
    ]