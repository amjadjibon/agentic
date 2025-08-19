"""
Utility module for filtering LLM-generated tool arguments to prevent execution errors.

This module provides robust filtering capabilities to handle the common issue where
LLMs add unexpected parameters like 'index', 'step', 'order', etc. to tool calls,
which can cause tool execution failures.
"""

from typing import Dict, Any, Set
from langchain_core.tools import BaseTool


class ToolArgumentFilter:
    """Comprehensive tool argument filtering system"""
    
    # Parameters that LLMs commonly add but tools don't expect
    PROBLEMATIC_PARAMS = {
        'index', 'step', 'order', 'position', 'id', 'number', 'sequence', 
        'count', 'rank', 'priority', 'level', 'stage', 'phase', 'iteration',
        'turn', 'round', 'cycle', 'attempt', 'try', 'run', 'execution',
        'call_id', 'request_id', 'session_id', 'timestamp', 'time',
        'task_id', 'process_id', 'batch_id', 'job_id', 'thread_id'
    }
    
    # Tool-specific parameter mappings
    TOOL_SPECIFIC_PARAMS = {
        'search_web': {'query', 'search_query', 'q', 'input', 'text'},
        'search_wikipedia': {'query', 'search_query', 'q', 'input', 'text'},
        'crawl4ai_competitor_analysis': {'competitor_urls', 'niche', 'extract_social_media', 'extract_content_themes'},
        'offline_competitor_analysis': {'competitor_urls', 'niche'},
        'strategy_generator': {'niche', 'target_audience', 'content_goals'},
    }
    
    # Common parameters that appear across many tools
    COMMON_PARAMS = {
        'query', 'input', 'text', 'question', 'search_query', 'q',
        'competitor_urls', 'niche', 'target_audience', 'content_goals',
        'extract_social_media', 'extract_content_themes', 
        'max_results', 'limit', 'url', 'urls', 'data'
    }
    
    @classmethod
    def filter_arguments(cls, tool: BaseTool, tool_name: str, tool_args: Any) -> Dict[str, Any]:
        """
        Filter tool arguments to remove problematic parameters.
        
        Args:
            tool: The tool instance
            tool_name: Name of the tool
            tool_args: Arguments to filter (dict, string, or other)
            
        Returns:
            Cleaned arguments dictionary
        """
        if not isinstance(tool_args, dict):
            return tool_args
        
        # Step 1: Remove obviously problematic parameters
        filtered_args = {
            k: v for k, v in tool_args.items() 
            if k not in cls.PROBLEMATIC_PARAMS
        }
        
        # Step 2: Get expected parameters from tool schema
        expected_params = cls._get_expected_parameters(tool)
        
        # Step 3: Apply filtering strategy based on available information
        if expected_params:
            # Use schema-defined parameters (most reliable)
            clean_args = {
                k: v for k, v in filtered_args.items() 
                if k in expected_params
            }
        else:
            # Fallback: Use tool-specific or common parameters
            allowed_params = cls.TOOL_SPECIFIC_PARAMS.get(tool_name, cls.COMMON_PARAMS)
            clean_args = {
                k: v for k, v in filtered_args.items() 
                if k in allowed_params
            }
        
        # Step 4: Safety fallback if filtering was too aggressive
        if not clean_args and filtered_args:
            # Keep parameters that look reasonable (not IDs, not too short, alphabetic)
            clean_args = {
                k: v for k, v in filtered_args.items() 
                if cls._is_reasonable_parameter(k)
            }
        
        return clean_args
    
    @classmethod
    def _get_expected_parameters(cls, tool: BaseTool) -> Set[str]:
        """Extract expected parameters from tool schema"""
        expected_params = set()
        
        if hasattr(tool, 'args_schema') and tool.args_schema:
            # Pydantic v2 style (preferred)
            if hasattr(tool.args_schema, 'model_fields'):
                expected_params = set(tool.args_schema.model_fields.keys())
            # Try to get from annotations
            elif hasattr(tool.args_schema, '__annotations__'):
                expected_params = set(tool.args_schema.__annotations__.keys())
            # Pydantic v1 style (deprecated but still supported for compatibility)
            elif hasattr(tool.args_schema, '__fields__'):
                # Using getattr to avoid deprecation warning
                fields = getattr(tool.args_schema, '__fields__', {})
                expected_params = set(fields.keys())
        
        return expected_params
    
    @classmethod
    def _is_reasonable_parameter(cls, param_name: str) -> bool:
        """Check if a parameter name looks reasonable (not an ID or generated param)"""
        if len(param_name) < 2:
            return False
        if param_name.lower().endswith('_id'):
            return False
        if not param_name.replace('_', '').isalpha():
            return False
        if param_name.lower() in {'temp', 'tmp', 'debug', 'test'}:
            return False
        return True
    
    @classmethod
    def get_problematic_params_in_args(cls, args: Dict[str, Any]) -> Set[str]:
        """Return set of problematic parameters found in arguments"""
        if not isinstance(args, dict):
            return set()
        
        return {k for k in args.keys() if k in cls.PROBLEMATIC_PARAMS}
    
    @classmethod
    def add_tool_specific_params(cls, tool_name: str, params: Set[str]) -> None:
        """Add tool-specific parameters to the registry"""
        if tool_name in cls.TOOL_SPECIFIC_PARAMS:
            cls.TOOL_SPECIFIC_PARAMS[tool_name].update(params)
        else:
            cls.TOOL_SPECIFIC_PARAMS[tool_name] = set(params)
    
    @classmethod
    def add_problematic_params(cls, params: Set[str]) -> None:
        """Add new problematic parameters to filter out"""
        cls.PROBLEMATIC_PARAMS.update(params)


# Convenience function for direct usage
def filter_tool_arguments(tool: BaseTool, tool_name: str, tool_args: Any) -> Dict[str, Any]:
    """Convenience function to filter tool arguments"""
    return ToolArgumentFilter.filter_arguments(tool, tool_name, tool_args)