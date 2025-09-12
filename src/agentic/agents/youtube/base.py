from abc import ABC, abstractmethod
from typing import Iterator, Optional, TYPE_CHECKING
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from agentic.state import ChatState
from agentic.llm import create_model_instance
from agentic.tools import get_tools_for_agents
from agentic.utils.tool_argument_filter import ToolArgumentFilter
from agentic.utils.safe_tool_invoke import wrap_all_tools
from agentic.utils.phoenix_tracing import setup_phoenix_tracing, is_tracing_enabled
import functools

if TYPE_CHECKING:
    from agentic.tui.rich_ui import DebateUI


class BaseYouTubeAgent(ABC):
    """Base class for YouTube automation agents with Phoenix tracing support"""
    
    def __init__(self, model_name: str, persona: str, agent_name: str, agent_icon: str):
        self.model_name = model_name
        self.persona = persona
        self.agent_name = agent_name
        self.agent_icon = agent_icon
        
        # Initialize Phoenix tracing if not already done
        self._ensure_tracing_setup()
    
    def _ensure_tracing_setup(self):
        """Ensure Phoenix tracing is set up for this agent session"""
        if not is_tracing_enabled():
            setup_phoenix_tracing("http://localhost:6006")
    
    @abstractmethod
    def get_persona_with_tools(self) -> str:
        """Get persona text with tool descriptions if tools are enabled"""
        pass
    
    def execute_tool_call(self, tool_call) -> str:
        """Execute a tool call and return the result with robust argument filtering"""
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
            
            # Apply comprehensive argument filtering
            clean_args = self._filter_tool_arguments(tool, tool_name, tool_args)
            
            # Check for problematic parameters and log if found
            if isinstance(tool_args, dict):
                problematic_found = ToolArgumentFilter.get_problematic_params_in_args(tool_args)
                if problematic_found:
                    print(f"🔧 Filtered out problematic params: {', '.join(problematic_found)}")
            
            # Invoke the tool with cleaned arguments
            result = self._invoke_tool_safely(tool, tool_name, clean_args, tool_args)
            
            return str(result)
            
        except TypeError as e:
            if 'unexpected keyword argument' in str(e):
                # Extract the problematic parameter
                import re
                match = re.search(r"unexpected keyword argument '(\w+)'", str(e))
                problem_param = match.group(1) if match else 'unknown'
                print(f"❌ Tool '{tool_name}' rejected parameter: '{problem_param}'")
                
                # Return detailed error for debugging
                error_msg = f"Tool execution failed: unexpected parameter '{problem_param}' in {tool_name}"
                return error_msg
            else:
                print(f"❌ TypeError in tool '{tool_name}': {str(e)}")
                raise
                
        except Exception as e:
            # Provide concise error information
            error_msg = f"Error executing tool '{tool_name}': {str(e)}"
            if isinstance(tool_args, dict):
                problematic_found = ToolArgumentFilter.get_problematic_params_in_args(tool_args)
                if problematic_found:
                    error_msg += f" (Filtered: {', '.join(problematic_found)})"
            return error_msg
    
    def _filter_tool_arguments(self, tool, tool_name: str, tool_args) -> dict:
        """Comprehensive argument filtering to prevent tool call errors"""
        return ToolArgumentFilter.filter_arguments(tool, tool_name, tool_args)
    
    
    def _invoke_tool_safely(self, tool, tool_name: str, clean_args, original_args):
        """Safely invoke tool with multiple fallback strategies"""
        # Strategy 1: Try with cleaned arguments
        try:
            if isinstance(clean_args, dict):
                if len(clean_args) == 1:
                    # Single parameter - try direct value passing for simple tools
                    param_name = list(clean_args.keys())[0]
                    param_value = clean_args[param_name]
                    
                    # Special handling for search tools that expect string input
                    if tool_name in {'search_web', 'search_wikipedia'} and param_name in {'query', 'search_query', 'q'}:
                        return tool.invoke({'query': param_value})
                    else:
                        # Try as dict parameter first
                        try:
                            return tool.invoke({param_name: param_value})
                        except (TypeError, ValueError):
                            return tool.invoke(clean_args)
                elif len(clean_args) == 0:
                    # No clean arguments, try with empty dict or string conversion
                    if isinstance(original_args, str):
                        return tool.invoke({'query': original_args})
                    else:
                        # Try to extract a reasonable string value from original args
                        for key in ['query', 'search_query', 'q', 'input', 'text']:
                            if isinstance(original_args, dict) and key in original_args:
                                return tool.invoke({'query': original_args[key]})
                        # Last resort: pass empty dict
                        return tool.invoke({})
                else:
                    # Multiple parameters - pass as dictionary
                    return tool.invoke(clean_args)
            else:
                # Non-dict argument - convert to proper dict format
                if isinstance(clean_args, str):
                    return tool.invoke({'query': clean_args})
                else:
                    return tool.invoke({'input': str(clean_args)})
                
        except Exception as e:
            # Strategy 2: Fallback with minimal args if cleaning was too aggressive
            if isinstance(original_args, dict):
                # Try with just the most essential parameter
                essential_keys = ['query', 'search_query', 'competitor_urls', 'niche', 'input', 'text']
                for key in essential_keys:
                    if key in original_args:
                        try:
                            return tool.invoke({key: original_args[key]})
                        except Exception:
                            continue
            
            # Strategy 3: Final fallback - re-raise the original exception with context
            raise Exception(f"Tool invocation failed after argument filtering. Original error: {str(e)}")
    
    def _wrap_tools_with_filtering(self, tools):
        """Wrap all tools with argument filtering to prevent parameter errors"""
        wrapped_tools = []
        
        for tool in tools:
            # Create a wrapper function for the tool's _run method
            original_run = tool._run
            
            @functools.wraps(original_run)
            def filtered_run(*args, tool_instance=tool, original_method=original_run, **kwargs):
                """Wrapped _run method with argument filtering"""
                try:
                    # Apply comprehensive filtering to kwargs
                    filtered_kwargs = ToolArgumentFilter.filter_arguments(tool_instance, tool_instance.name, kwargs)
                    
                    # Call original method with filtered arguments
                    return original_method(**filtered_kwargs)
                    
                except Exception as e:
                    # If the filtered call fails, try with essential parameters only
                    if isinstance(kwargs, dict) and kwargs:
                        essential_keys = ['query', 'search_query', 'competitor_urls', 'niche', 'target_audience', 'input', 'text']
                        essential_kwargs = {k: v for k, v in kwargs.items() if k in essential_keys}
                        
                        if essential_kwargs:
                            try:
                                return original_method(**essential_kwargs)
                            except Exception:
                                pass
                    
                    # As a last resort, provide a helpful error message
                    problematic_params = ToolArgumentFilter.get_problematic_params_in_args(kwargs)
                    if problematic_params:
                        return f"Tool execution failed due to unexpected parameters: {', '.join(problematic_params)}. Please try again without these parameters."
                    else:
                        return f"Tool execution failed: {str(e)}"
            
            # Replace the tool's _run method with our wrapped version
            tool._run = filtered_run
            wrapped_tools.append(tool)
        
        return wrapped_tools

    def stream_response(self, state: ChatState, with_tools: bool = False, ui: Optional['DebateUI'] = None) -> Iterator[ChatState]:
        """Generate streaming response"""
        try:
            model = create_model_instance(self.model_name, with_tools)
            
            # If tools are enabled, wrap them with comprehensive safety measures
            if with_tools:
                tools = get_tools_for_agents()
                if tools:
                    print(f"🔍 DEBUG: Wrapping {len(tools)} tools for safety")
                    # Apply comprehensive safety wrapping
                    safe_tools = wrap_all_tools(tools)
                    print(f"🔍 DEBUG: Successfully wrapped {len(safe_tools)} tools")
                    for tool in safe_tools:
                        print(f"🔍 DEBUG: Safe tool: {tool.name}")
                    
                    # Bind the safe tools to the model
                    model = model.bind_tools(safe_tools)
                    print(f"🔍 DEBUG: Tools bound to model successfully")
                    
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
                "current_speaker": "system",
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
                system_context = HumanMessage(content=persona_text + "\n\nPlease respond based on your specialized YouTube automation expertise.")
                messages = [system_context] + messages
        
        # Display agent header
        if ui:
            ui.console.print(f"\n{self.agent_icon} [bold]{self.agent_name}:[/bold]")
        else:
            print(f"\n{self.agent_icon} {self.agent_name}:")
        
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
            print(f"🔍 DEBUG: Processing {len(tool_calls)} tool calls...")
            
            # Filter and repair tool calls to handle LLM-generated malformed calls
            cleaned_tool_calls = []
            valid_tool_calls = []
            
            for i, tool_call in enumerate(tool_calls):
                print(f"🔍 DEBUG: Processing tool call {i}: {tool_call}")
                
                # Skip obviously invalid tool calls
                if isinstance(tool_call, dict):
                    name = tool_call.get('name', '')
                    args = tool_call.get('args', {})
                    tool_id = tool_call.get('id')
                    
                    # Skip empty or fragmented tool calls
                    if not name or name == '' or not tool_id:
                        print(f"🔍 DEBUG: Skipping invalid tool call {i}: missing name or id")
                        continue
                    
                    # Clean the tool call structure
                    cleaned_call = {
                        'name': name,
                        'args': args,
                        'id': tool_id,
                        'type': 'tool_call'  # Ensure proper type
                    }
                    
                    # Remove problematic parameters from args
                    if isinstance(args, dict):
                        cleaned_args = {k: v for k, v in args.items() if k not in ToolArgumentFilter.PROBLEMATIC_PARAMS}
                        cleaned_call['args'] = cleaned_args
                    
                    print(f"🔍 DEBUG: Cleaned tool call {i}: {cleaned_call}")
                    cleaned_tool_calls.append(cleaned_call)
                    valid_tool_calls.append(tool_call)  # Keep original for execution
                else:
                    print(f"🔍 DEBUG: Skipping non-dict tool call {i}: {type(tool_call)}")
            
            print(f"🔍 DEBUG: Kept {len(cleaned_tool_calls)} valid tool calls out of {len(tool_calls)}")
            
            print(f"🔍 DEBUG: Creating AIMessage with {len(cleaned_tool_calls)} cleaned tool calls...")
            
            # Create AI message with cleaned tool calls
            try:
                ai_message = AIMessage(content=accumulated_content, tool_calls=cleaned_tool_calls)
                print("🔍 DEBUG: AIMessage created successfully!")
            except Exception as e:
                print(f"🔍 DEBUG: AIMessage creation failed: {str(e)}")
                # Fallback: create AIMessage without tool calls
                ai_message = AIMessage(content=accumulated_content + f"\\n\\nNote: Tool calls were attempted but failed due to: {str(e)}")
                cleaned_tool_calls = []  # Clear tool calls since we can't process them
            new_messages.append(ai_message)
            
            # Execute tools and add results - use valid_tool_calls for execution
            for tool_call in valid_tool_calls:
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
                    
                except Exception as e:
                    if ui:
                        ui.console.print(f"\n[red]❌ Error processing tool call: {str(e)}[/red]")
                    else:
                        print(f"\n❌ Error processing tool call: {str(e)}")
                    continue
                
                # Display tool usage with sanitized arguments for UI
                display_args = self._sanitize_args_for_display(tool_args)
                
                if ui:
                    from ...tui.rich_ui import DebateUIComponents
                    tool_panel = DebateUIComponents.create_tool_usage_panel(tool_name, str(display_args), "Processing...")
                    ui.console.print(tool_panel)
                else:
                    print(f"\n🔍 Using tool: {tool_name}")
                    print(f"📝 Query: {display_args}")
                
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
                    # Update with actual result
                    result_content = tool_message.content
                    result_display = result_content[:200] + "..." if len(result_content) > 200 else result_content
                    from ...tui.rich_ui import DebateUIComponents
                    final_tool_panel = DebateUIComponents.create_tool_usage_panel(tool_name, str(display_args), result_display)
                    ui.console.print(final_tool_panel)
                else:
                    result_content = tool_message.content
                    print(f"📊 Result: {result_content[:200]}{'...' if len(result_content) > 200 else ''}")
            
            # Get final response incorporating tool results
            if ui:
                ui.console.print(f"\n{self.agent_icon} [bold]{self.agent_name} (incorporating research):[/bold]")
            else:
                print(f"\n{self.agent_icon} {self.agent_name} (incorporating research):")
            
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
            "current_speaker": "system",
            "conversation_count": state["conversation_count"] + 1,
            "max_turns": state["max_turns"],
        }
        
        yield final_state
    
    def _sanitize_args_for_display(self, args) -> dict:
        """Sanitize arguments for display purposes, removing problematic parameters"""
        if not isinstance(args, dict):
            return args
        
        # Remove problematic parameters for cleaner display
        display_args = {k: v for k, v in args.items() if k not in ToolArgumentFilter.PROBLEMATIC_PARAMS}
        
        # If we filtered out everything, show a simplified version
        if not display_args and args:
            # Show just the first non-problematic key-value pair or a summary
            for k, v in args.items():
                if k not in ToolArgumentFilter.PROBLEMATIC_PARAMS:
                    display_args[k] = v
                    break
            
            if not display_args:
                # All parameters were problematic, show a generic message
                return {"cleaned_parameters": f"{len(args)} parameters filtered"}
        
        return display_args