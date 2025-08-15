from abc import ABC, abstractmethod

from typing import Iterator, Optional, TYPE_CHECKING
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from debateai.state import ChatState
from debateai.models import create_model_instance
from debateai.tools import get_tools_for_agents

if TYPE_CHECKING:
    from debateai.rich_ui import DebateUI


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
            
            # Get the tool's expected parameters from its schema
            expected_params = set()
            if hasattr(tool, 'args_schema') and tool.args_schema:
                if hasattr(tool.args_schema, 'model_fields'):
                    expected_params = set(tool.args_schema.model_fields.keys())
                elif hasattr(tool.args_schema, '__fields__'):
                    expected_params = set(tool.args_schema.__fields__.keys())
            
            # Handle different argument formats
            if isinstance(tool_args, dict):
                # Filter out any unexpected arguments that LLMs might add
                if expected_params:
                    clean_args = {k: v for k, v in tool_args.items() if k in expected_params}
                else:
                    # Fallback: only keep common parameter names if we can't introspect the tool
                    common_params = {'query', 'input', 'text', 'question', 'search_query'}
                    clean_args = {k: v for k, v in tool_args.items() if k in common_params}
                
                # Special handling for single-parameter tools
                if len(clean_args) == 1:
                    param_name = list(clean_args.keys())[0]
                    param_value = clean_args[param_name]
                    
                    # For search_web tool specifically, it expects just the query string
                    if tool_name == 'search_web' and param_name in {'query', 'search_query'}:
                        result = tool.invoke(param_value)
                    else:
                        # Try to invoke with the parameter value directly
                        try:
                            result = tool.invoke(param_value)
                        except TypeError:
                            # If direct invocation fails, try with the dict
                            result = tool.invoke(clean_args)
                elif len(clean_args) == 0:
                    # No valid arguments found, try with original args as fallback
                    if isinstance(tool_args, str):
                        result = tool.invoke(tool_args)
                    else:
                        result = tool.invoke(tool_args)
                else:
                    # Multiple parameters - pass as dict
                    result = tool.invoke(clean_args)
            else:
                # Direct argument (string, etc.)
                result = tool.invoke(tool_args)
            
            return str(result)
        except Exception as e:
            # Provide more detailed error information for debugging
            error_msg = f"Error executing tool '{tool_name}': {str(e)}"
            if isinstance(tool_args, dict) and 'index' in tool_args:
                error_msg += f" (Note: Removed unexpected 'index' parameter from tool call)"
            return error_msg
    
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
                # Extract tool call information safely with better error handling
                try:
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
                    
                    # Log tool call details for debugging
                    if isinstance(tool_args, dict) and any(key not in {'query', 'input', 'text', 'question', 'search_query'} for key in tool_args.keys()):
                        filtered_args = {k: v for k, v in tool_args.items() if k in {'query', 'input', 'text', 'question', 'search_query'}}
                        if ui:
                            ui.console.print(f"[dim]🔧 Filtered tool args: {tool_args} -> {filtered_args}[/dim]")
                        
                except Exception as e:
                    if ui:
                        ui.console.print(f"\n[red]❌ Error processing tool call: {str(e)}[/red]")
                    else:
                        print(f"\n❌ Error processing tool call: {str(e)}")
                    continue
                
                if ui:
                    from ..rich_ui import DebateUIComponents
                    tool_panel = DebateUIComponents.create_tool_usage_panel(tool_name, str(tool_args), "Processing...")
                    ui.console.print(tool_panel)
                else:
                    print(f"\n🔍 Using tool: {tool_name}")
                    print(f"📝 Query: {tool_args}")
                
                # Execute tool with comprehensive error handling
                try:
                    result = self.execute_tool_call(tool_call)
                    tool_message = ToolMessage(content=result, tool_call_id=tool_id)
                    new_messages.append(tool_message)
                except Exception as e:
                    error_result = f"Error executing tool '{tool_name}': {str(e)}"
                    if ui:
                        ui.console.print(f"\n[red]❌ Tool execution failed: {str(e)}[/red]")
                    else:
                        print(f"\n❌ Tool execution failed: {str(e)}")
                    tool_message = ToolMessage(content=error_result, tool_call_id=tool_id)
                    new_messages.append(tool_message)
                
                if ui:
                    # Update with actual result (use the content from tool_message)
                    result_content = tool_message.content
                    result_display = result_content[:200] + "..." if len(result_content) > 200 else result_content
                    from ..rich_ui import DebateUIComponents
                    final_tool_panel = DebateUIComponents.create_tool_usage_panel(tool_name, str(tool_args), result_display)
                    ui.console.print(final_tool_panel)
                else:
                    result_content = tool_message.content
                    print(f"📊 Result: {result_content[:200]}{'...' if len(result_content) > 200 else ''}")
            
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
