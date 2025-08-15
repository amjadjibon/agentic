import os
from datetime import datetime

from typing import List, Optional, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage

from agentic.state import ChatState
from agentic.config import get_model_config


class MarkdownFormatter:
    """Formats debate conversations into markdown"""
    
    def __init__(self):
        self.output_lines = []
    
    def format_debate(
        self, 
        topic: str, 
        left_model: str, 
        right_model: str, 
        state: ChatState, 
        debate_type: str = "debate",
        tools_enabled: bool = False,
        left_persona: Optional[str] = None,
        right_persona: Optional[str] = None,
        judge_enabled: bool = False
    ) -> str:
        """Format a complete debate into markdown"""
        
        # Get model display names
        left_config = get_model_config(left_model)
        right_config = get_model_config(right_model)
        left_display = left_config.display_name if left_config else left_model
        right_display = right_config.display_name if right_config else right_model
        
        # Header
        lines = []
        lines.append(f"# Political Debate: {topic}")
        lines.append("")
        lines.append(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**Type:** {debate_type.title()}")
        lines.append(f"**Tools Enabled:** {'Yes' if tools_enabled else 'No'}")
        lines.append(f"**Judge Enabled:** {'Yes' if judge_enabled else 'No'}")
        lines.append("")
        
        # Participants
        lines.append("## Participants")
        lines.append("")
        lines.append("| Side | Model | Persona |")
        lines.append("|------|-------|---------|")
        
        left_persona_desc = "Custom Progressive" if left_persona else "Default Progressive"
        right_persona_desc = "Custom Conservative" if right_persona else "Default Conservative"
        
        lines.append(f"| 🔴 Progressive | {left_display} | {left_persona_desc} |")
        lines.append(f"| 🔵 Conservative | {right_display} | {right_persona_desc} |")
        lines.append("")
        
        # Debate content
        lines.append("## Debate Transcript")
        lines.append("")
        
        # Process messages
        messages = state["messages"]
        current_speaker = "progressive"
        turn_number = 1
        
        for i, message in enumerate(messages):
            if isinstance(message, HumanMessage) and i == 0:
                # Skip the initial system prompt
                continue
            elif isinstance(message, AIMessage):
                # Determine speaker based on turn order
                if current_speaker == "progressive":
                    speaker_icon = "🔴"
                    speaker_name = "Progressive Perspective"
                    current_speaker = "conservative"
                else:
                    speaker_icon = "🔵"
                    speaker_name = "Conservative Perspective"
                    current_speaker = "progressive"
                
                lines.append(f"### {speaker_icon} {speaker_name} - Turn {turn_number}")
                lines.append("")
                
                # Format the message content
                content = message.content.strip()
                if content:
                    lines.append(content)
                    lines.append("")
                
                # Handle tool calls if present
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    lines.append("#### 🔍 Research Used")
                    lines.append("")
                    for tool_call in message.tool_calls:
                        tool_name = getattr(tool_call, 'name', 'Unknown Tool')
                        tool_args = getattr(tool_call, 'args', {})
                        lines.append(f"- **Tool:** {tool_name}")
                        if isinstance(tool_args, dict) and 'query' in tool_args:
                            lines.append(f"- **Query:** {tool_args['query']}")
                        lines.append("")
                
                turn_number += 1
                
            elif isinstance(message, ToolMessage):
                # Tool results - these are usually followed by AI messages
                lines.append("#### 📊 Research Results")
                lines.append("")
                lines.append("```")
                lines.append(message.content[:500] + "..." if len(message.content) > 500 else message.content)
                lines.append("```")
                lines.append("")
        
        # Judge scores if available
        if 'judge_scores' in state and state['judge_scores']:
            lines.append("## Judge Evaluation")
            lines.append("")
            
            judge_data = state['judge_scores']
            
            # Individual turn scores
            if 'individual_scores' in judge_data:
                lines.append("### Turn-by-Turn Scores")
                lines.append("")
                lines.append("| Turn | Speaker | Logic | Evidence | Sources | Structure | Rebuttals | Clarity | Accuracy | Originality | Total |")
                lines.append("|------|---------|-------|----------|---------|-----------|-----------|---------|----------|-------------|-------|")
                
                for score in judge_data['individual_scores']:
                    speaker_icon = "🔴" if score['speaker'] == 'progressive' else "🔵"
                    lines.append(f"| {score['turn_number']} | {speaker_icon} {score['speaker'].title()} | {score['logic_reasoning']:.1f} | {score['evidence_quality']:.1f} | {score['source_credibility']:.1f} | {score['argument_structure']:.1f} | {score['rebuttal_effectiveness']:.1f} | {score['clarity_communication']:.1f} | {score['factual_accuracy']:.1f} | {score['originality']:.1f} | **{score['total_score']:.1f}** |")
                
                lines.append("")
                
                # Detailed feedback for each turn
                lines.append("### Detailed Judge Feedback")
                lines.append("")
                
                for score in judge_data['individual_scores']:
                    speaker_icon = "🔴" if score['speaker'] == 'progressive' else "🔵"
                    lines.append(f"#### {speaker_icon} {score['speaker'].title()} - Turn {score['turn_number']}")
                    lines.append("")
                    lines.append(f"**Strengths:** {', '.join(score['strengths'])}")
                    lines.append(f"**Weaknesses:** {', '.join(score['weaknesses'])}")
                    lines.append("")
                    lines.append(f"**Judge's Comments:** {score['specific_feedback']}")
                    lines.append("")
            
            # Final judgment
            if 'final_judgment' in judge_data and judge_data['final_judgment']:
                final = judge_data['final_judgment']
                lines.append("### Final Judgment")
                lines.append("")
                
                if final['winner'] == 'tie':
                    lines.append(f"**Result:** 🤝 **TIE** (Margin: {final['margin']:.1f} points)")
                else:
                    winner_icon = "🔴" if final['winner'] == 'progressive' else "🔵"
                    lines.append(f"**Result:** {winner_icon} **{final['winner'].upper()} WINS** by {final['margin']:.1f} points")
                
                lines.append("")
                lines.append("**Final Scores:**")
                lines.append(f"- 🔴 Progressive Total: {final['progressive_total']:.1f}")
                lines.append(f"- 🔵 Conservative Total: {final['conservative_total']:.1f}")
                lines.append("")
                
                lines.append("**Category Winners:**")
                lines.append(f"- Best Logic: {final['best_logic'].title()}")
                lines.append(f"- Best Evidence: {final['best_evidence'].title()}")
                lines.append(f"- Best Communication: {final['best_communication'].title()}")
                lines.append(f"- Best Rebuttals: {final['best_rebuttals'].title()}")
                lines.append("")
                
                lines.append(f"**Debate Quality:** {final['debate_quality'].title()}")
                lines.append("")
                
                if final['key_insights']:
                    lines.append("**Key Insights:**")
                    for insight in final['key_insights']:
                        lines.append(f"- {insight}")
                    lines.append("")
                
                lines.append("**Judge's Summary:**")
                lines.append(final['judge_summary'])
                lines.append("")
        
        # Summary
        lines.append("## Debate Summary")
        lines.append("")
        lines.append(f"- **Total Turns:** {state['conversation_count']}")
        lines.append(f"- **Max Turns:** {state['max_turns']}")
        lines.append(f"- **Completion Status:** {'Complete' if state['conversation_count'] >= state['max_turns'] else 'Incomplete'}")
        if judge_enabled and 'judge_scores' in state:
            lines.append(f"- **Judge Evaluation:** Complete")
        lines.append("")
        
        # Footer
        lines.append("---")
        lines.append("*Generated by Political Debate AI*")
        
        return "\n".join(lines)
    
    def save_debate_markdown(
        self,
        topic: str,
        left_model: str,
        right_model: str,
        state: ChatState,
        debate_type: str = "debate",
        tools_enabled: bool = False,
        left_persona: Optional[str] = None,
        right_persona: Optional[str] = None,
        output_dir: str = "debates",
        judge_enabled: bool = False
    ) -> str:
        """Save debate as markdown file and return the file path"""
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = "".join(c for c in topic if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_topic = safe_topic.replace(' ', '_')[:50]  # Limit length
        filename = f"{timestamp}_{safe_topic}_{debate_type}.md"
        filepath = os.path.join(output_dir, filename)
        
        # Generate markdown content
        markdown_content = self.format_debate(
            topic, left_model, right_model, state, debate_type,
            tools_enabled, left_persona, right_persona, judge_enabled
        )
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        return filepath
    
    def format_message_as_markdown(self, message: BaseMessage, speaker: str, turn: int) -> str:
        """Format a single message as markdown"""
        if isinstance(message, AIMessage):
            icon = "🔴" if "progressive" in speaker.lower() else "🔵"
            lines = [
                f"### {icon} {speaker} - Turn {turn}",
                "",
                message.content.strip(),
                ""
            ]
            
            # Add tool information if present
            if hasattr(message, 'tool_calls') and message.tool_calls:
                lines.extend([
                    "#### 🔍 Research Used",
                    ""
                ])
                for tool_call in message.tool_calls:
                    tool_name = getattr(tool_call, 'name', 'Unknown Tool')
                    tool_args = getattr(tool_call, 'args', {})
                    lines.append(f"- **Tool:** {tool_name}")
                    if isinstance(tool_args, dict) and 'query' in tool_args:
                        lines.append(f"- **Query:** {tool_args['query']}")
                lines.append("")
            
            return "\n".join(lines)
        
        return ""


def create_debate_summary_markdown(
    debates: List[Dict[str, Any]], 
    output_file: str = "debate_summary.md"
) -> str:
    """Create a summary markdown file of multiple debates"""
    
    lines = [
        "# Debate Session Summary",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Total Debates:** {len(debates)}",
        "",
        "## Debates Overview",
        "",
        "| # | Topic | Type | Models | Tools | Turns | Status |",
        "|---|-------|------|--------|-------|-------|--------|"
    ]
    
    for i, debate in enumerate(debates, 1):
        topic = debate.get('topic', 'Unknown')[:50]
        debate_type = debate.get('type', 'Unknown')
        left_model = debate.get('left_model', 'Unknown')
        right_model = debate.get('right_model', 'Unknown')
        tools = "Yes" if debate.get('tools_enabled', False) else "No"
        turns = f"{debate.get('turns_completed', 0)}/{debate.get('max_turns', 0)}"
        status = "Complete" if debate.get('completed', False) else "Incomplete"
        
        lines.append(f"| {i} | {topic} | {debate_type} | {left_model} vs {right_model} | {tools} | {turns} | {status} |")
    
    lines.extend([
        "",
        "## Individual Debate Files",
        ""
    ])
    
    for i, debate in enumerate(debates, 1):
        if 'file_path' in debate:
            lines.append(f"{i}. [{debate.get('topic', 'Debate ' + str(i))}]({debate['file_path']})")
    
    lines.extend([
        "",
        "---",
        "*Generated by Political Debate AI*"
    ])
    
    content = "\n".join(lines)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_file


# Utility function for quick markdown export
def export_debate_to_markdown(
    topic: str,
    left_model: str,
    right_model: str,
    state: ChatState,
    **kwargs
) -> str:
    """Quick utility function to export a debate to markdown"""
    formatter = MarkdownFormatter()
    return formatter.save_debate_markdown(
        topic, left_model, right_model, state, **kwargs
    )
