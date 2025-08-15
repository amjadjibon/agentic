from abc import ABC, abstractmethod
from typing import Iterator, Optional, TYPE_CHECKING
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from ..state import ChatState
from ..models import create_model_instance
from ..tools_registry import get_tools_for_agents

if TYPE_CHECKING:
    from ..rich_ui import DebateUI


class BaseStreamingAgent(ABC):
    """Base class for streaming agents"""
    
    def __init__(self, model_name: str, persona: str, speaker_name: str, speaker_icon: str, next_speaker: str):
        self.model_name = model_name
        self.persona = persona
        self.speaker_name = speaker_name
        self.speaker_icon = speaker_icon
        self.next_speaker = next_speaker
    
    @abstractmethod
    def get_persona_with_tools(self) -> str:
        """Get persona text with tool descriptions if tools are enabled"""
        pass
    
    def execute_tool_call(self, tool_call) -> str:
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
            # Handle different argument formats - some tools expect direct args, others expect dict
            if isinstance(tool_args, dict):
                # Remove any unexpected arguments like 'index' that some models might add
                # Only keep known tool parameters
                clean_args = {k: v for k, v in tool_args.items() if k in ['query', 'input', 'text']}
                
                if len(clean_args) == 1 and 'query' in clean_args:
                    # If only query argument, pass it directly for simple tools
                    result = tool.invoke(clean_args['query'])
                elif len(clean_args) == 1 and list(clean_args.keys())[0] in ['input', 'text']:
                    # Handle other single argument tools
                    result = tool.invoke(list(clean_args.values())[0])
                else:
                    # Pass full dict for complex tools
                    result = tool.invoke(clean_args if clean_args else tool_args)
            else:
                # Direct argument
                result = tool.invoke(tool_args)
            return str(result)
        except Exception as e:
            # Provide more detailed error information
            return f"Error executing tool '{tool_name}' with args {tool_args}: {str(e)}"
    
    def stream_response(self, state: ChatState, with_tools: bool = False, ui: Optional['DebateUI'] = None) -> Iterator[ChatState]:
        """Generate streaming response"""
        try:
            model = create_model_instance(self.model_name, with_tools)
        except ValueError as e:
            error_msg = f"Error initializing model: {str(e)}"
            if ui:
                ui.console.print(f"\n[red]❌ {error_msg}[/red]")
            else:
                print(f"\n❌ {error_msg}")
            # Return error state
            error_message = AIMessage(content=f"Error: {str(e)}")
            new_messages = state["messages"] + [error_message]
            yield {
                "messages": new_messages,
                "current_speaker": self.next_speaker,
                "conversation_count": state["conversation_count"] + 1,
                "max_turns": state["max_turns"],
            }
            return
        
        # Prepare messages with persona
        messages = state["messages"].copy()
        persona_text = self.get_persona_with_tools() if with_tools else self.persona
        
        if messages and isinstance(messages[0], HumanMessage):
            if len(messages) == 1:
                # First message - add persona to the initial topic
                messages[0] = HumanMessage(
                    content=persona_text + "\n\n" + messages[0].content
                )
            else:
                # Subsequent messages - add persona as system context but keep all conversation history
                system_context = HumanMessage(content=persona_text + "\n\nPlease respond to the ongoing debate by addressing the previous points made and continuing the discussion.")
                messages = [system_context] + messages
        
        # Display speaker header
        if ui:
            from ..rich_ui import DebateUIComponents
            # We'll stream directly and create panel later
            ui.console.print(f"\n{self.speaker_icon} [bold]{self.speaker_name}:[/bold]")
        else:
            print(f"\n{self.speaker_icon} {self.speaker_name}:")
        
        # Stream the response
        accumulated_content = ""
        tool_calls = []
        
        try:
            for chunk in model.stream(messages):
                if hasattr(chunk, 'content') and chunk.content:
                    if ui:
                        ui.console.print(chunk.content, end='', style="white")
                    else:
                        print(chunk.content, end='', flush=True)
                    accumulated_content += chunk.content
                elif hasattr(chunk, 'tool_calls') and chunk.tool_calls:
                    tool_calls.extend(chunk.tool_calls)
                elif hasattr(chunk, 'additional_kwargs') and 'tool_calls' in chunk.additional_kwargs:
                    tool_calls.extend(chunk.additional_kwargs['tool_calls'])
        except Exception as e:
            error_msg = f"Error during streaming: {str(e)}"
            if ui:
                ui.console.print(f"\n[red]❌ {error_msg}[/red]")
            else:
                print(f"\n❌ {error_msg}")
            accumulated_content = f"Error occurred during response generation: {str(e)}"
        
        # Handle tool calls if any
        new_messages = state["messages"].copy()
        
        if tool_calls and with_tools:
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
                    if ui:
                        ui.console.print(f"\n[red]❌ Invalid tool call format: {type(tool_call)}[/red]")
                    else:
                        print(f"\n❌ Invalid tool call format: {type(tool_call)}")
                    continue
                
                if ui:
                    from ..rich_ui import DebateUIComponents
                    tool_panel = DebateUIComponents.create_tool_usage_panel(tool_name, str(tool_args), "Processing...")
                    ui.console.print(tool_panel)
                else:
                    print(f"\n🔍 Using tool: {tool_name}")
                    print(f"📝 Query: {tool_args}")
                
                result = self.execute_tool_call(tool_call)
                tool_message = ToolMessage(content=result, tool_call_id=tool_id)
                new_messages.append(tool_message)
                
                if ui:
                    # Update with actual result
                    result_display = result[:200] + "..." if len(result) > 200 else result
                    from ..rich_ui import DebateUIComponents
                    final_tool_panel = DebateUIComponents.create_tool_usage_panel(tool_name, str(tool_args), result_display)
                    ui.console.print(final_tool_panel)
                else:
                    print(f"📊 Result: {result[:200]}{'...' if len(result) > 200 else ''}")
            
            # Get final response incorporating tool results
            if ui:
                ui.console.print(f"\n{self.speaker_icon} [bold]{self.speaker_name} (incorporating research):[/bold]")
            else:
                print(f"\n{self.speaker_icon} {self.speaker_name} (incorporating research):")
            
            final_accumulated = ""
            try:
                for chunk in model.stream(new_messages):
                    if hasattr(chunk, 'content') and chunk.content:
                        if ui:
                            ui.console.print(chunk.content, end='', style="white")
                        else:
                            print(chunk.content, end='', flush=True)
                        final_accumulated += chunk.content
            except Exception as e:
                error_msg = f"Error during final response: {str(e)}"
                if ui:
                    ui.console.print(f"\n[red]❌ {error_msg}[/red]")
                else:
                    print(f"\n❌ {error_msg}")
                final_accumulated = f"Error occurred during final response: {str(e)}"
            
            final_message = AIMessage(content=final_accumulated)
            new_messages.append(final_message)
        else:
            # No tool calls, just add the regular response
            response = AIMessage(content=accumulated_content)
            new_messages.append(response)
        
        # Add separator
        if ui:
            ui.console.print("\n" + "-" * 50, style="dim")
        else:
            print()  # New line after streaming
            print("-" * 40)
        
        final_state = {
            "messages": new_messages,
            "current_speaker": self.next_speaker,
            "conversation_count": state["conversation_count"] + 1,
            "max_turns": state["max_turns"],
        }
        
        yield final_state
