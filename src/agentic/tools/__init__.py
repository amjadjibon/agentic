from agentic.tools.registry import tools_registry
from langchain_core.tools import BaseTool
from typing import List


def get_tools_for_agents() -> List[BaseTool]:
    """Get tools that should be available to debate agents"""
    return tools_registry.get_all_tools()


def add_custom_tool(name: str, tool: BaseTool):
    """Add a custom tool to the registry"""
    tools_registry.register_tool(name, tool)


def get_tool_descriptions() -> str:
    """Get formatted descriptions of all available tools"""
    tools = tools_registry.get_all_tools()
    descriptions = []
    
    for tool in tools:
        descriptions.append(f"- {tool.name}: {tool.description}")
    
    return "\n".join(descriptions)
