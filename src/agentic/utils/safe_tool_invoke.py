"""
Safe tool invocation utility that prevents parameter errors in LLM tool calls.

This utility provides robust tool invocation with multiple fallback strategies
to handle LLM-generated parameters that tools don't expect.
"""

from typing import Any, Dict, List
from langchain_core.tools import BaseTool
from .tool_argument_filter import ToolArgumentFilter
import functools
import inspect


def create_safe_tool_wrapper(tool: BaseTool) -> BaseTool:
    """
    Create a safe wrapper for a tool that filters arguments and handles errors gracefully.
    
    Args:
        tool: The original tool to wrap
        
    Returns:
        The same tool with safe invocation behavior (modifies in place)
    """
    
    # Store original methods
    original_run = tool._run
    original_invoke = getattr(tool, 'invoke', None)
    
    def safe_run(*args, **kwargs):
        """Safe _run method with comprehensive error handling"""
        try:
            # Apply argument filtering
            filtered_kwargs = ToolArgumentFilter.filter_arguments(tool, tool.name, kwargs)
            
            # Try with filtered arguments
            return original_run(**filtered_kwargs)
            
        except TypeError as e:
            if 'unexpected keyword argument' in str(e):
                # Extract the problematic parameter from error message
                import re
                match = re.search(r"unexpected keyword argument '(\w+)'", str(e))
                if match:
                    problematic_param = match.group(1)
                    # Add to problematic params and retry
                    ToolArgumentFilter.add_problematic_params({problematic_param})
                    
                    # Re-filter and retry
                    re_filtered_kwargs = ToolArgumentFilter.filter_arguments(tool, tool.name, kwargs)
                    try:
                        return original_run(**re_filtered_kwargs)
                    except Exception:
                        pass
                
                # Fallback to essential parameters only
                return _try_essential_parameters(original_run, kwargs)
            else:
                raise
                
        except Exception as e:
            # For other exceptions, try essential parameters fallback
            return _try_essential_parameters(original_run, kwargs, str(e))
    
    # Only replace the _run method since invoke might not be modifiable
    tool._run = safe_run
    
    return tool


def _try_essential_parameters(run_method, kwargs, error_context=""):
    """Try calling the run method with only essential parameters"""
    essential_keys = [
        'query', 'search_query', 'q', 'input', 'text', 'question',
        'competitor_urls', 'niche', 'target_audience', 'content_goals',
        'max_videos', 'max_results', 'limit', 'url', 'urls'
    ]
    
    if not isinstance(kwargs, dict):
        if error_context:
            return f"Tool execution failed: {error_context}"
        else:
            return "Tool execution failed: Invalid arguments"
    
    # Try each essential parameter individually
    for key in essential_keys:
        if key in kwargs:
            try:
                return run_method(**{key: kwargs[key]})
            except Exception:
                continue
    
    # Try with first non-problematic parameter
    for key, value in kwargs.items():
        if key not in ToolArgumentFilter.PROBLEMATIC_PARAMS:
            try:
                return run_method(**{key: value})
            except Exception:
                continue
    
    # Final fallback
    problematic_params = ToolArgumentFilter.get_problematic_params_in_args(kwargs)
    if problematic_params:
        return f"Tool execution failed due to unexpected parameters: {', '.join(problematic_params)}. The tool does not accept these parameters."
    else:
        return f"Tool execution failed: {error_context}" if error_context else "Tool execution failed with provided arguments"


def _try_essential_parameters_invoke(invoke_method, input_data, error_context=""):
    """Try calling the invoke method with only essential parameters"""
    if not isinstance(input_data, dict):
        if error_context:
            return f"Tool execution failed: {error_context}"
        else:
            return "Tool execution failed: Invalid input"
    
    essential_keys = [
        'query', 'search_query', 'q', 'input', 'text', 'question',
        'competitor_urls', 'niche', 'target_audience', 'content_goals',
        'max_videos', 'max_results', 'limit', 'url', 'urls'
    ]
    
    # Try each essential parameter individually  
    for key in essential_keys:
        if key in input_data:
            try:
                return invoke_method({key: input_data[key]})
            except Exception:
                continue
    
    # Try with first non-problematic parameter
    for key, value in input_data.items():
        if key not in ToolArgumentFilter.PROBLEMATIC_PARAMS:
            try:
                return invoke_method({key: value})
            except Exception:
                continue
    
    # Final fallback
    problematic_params = ToolArgumentFilter.get_problematic_params_in_args(input_data)
    if problematic_params:
        return f"Tool execution failed due to unexpected parameters: {', '.join(problematic_params)}. The tool does not accept these parameters."
    else:
        return f"Tool execution failed: {error_context}" if error_context else "Tool execution failed with provided input"


def wrap_all_tools(tools: List[BaseTool]) -> List[BaseTool]:
    """
    Wrap all tools in a list with safe invocation behavior.
    
    Args:
        tools: List of tools to wrap
        
    Returns:
        List of wrapped tools
    """
    return [create_safe_tool_wrapper(tool) for tool in tools]


# Decorator for making individual functions safe
def safe_tool_call(func):
    """Decorator to make a function safe from unexpected keyword arguments"""
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError as e:
            if 'unexpected keyword argument' in str(e):
                # Extract function signature
                sig = inspect.signature(func)
                valid_params = set(sig.parameters.keys())
                
                # Filter kwargs to only include valid parameters
                filtered_kwargs = {k: v for k, v in kwargs.items() if k in valid_params}
                
                return func(*args, **filtered_kwargs)
            else:
                raise
    
    return wrapper