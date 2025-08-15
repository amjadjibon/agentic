from typing import List, Dict
from langchain_core.tools import BaseTool
from .tools.search import search_web


class ToolsRegistry:
    """Registry for managing tools available to debate agents"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools"""
        self.register_tool("search_web", search_web)
    
    def register_tool(self, name: str, tool: BaseTool):
        """Register a tool with the registry"""
        self._tools[name] = tool
    
    def get_tool(self, name: str) -> BaseTool:
        """Get a tool by name"""
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' not found in registry")
        return self._tools[name]
    
    def get_all_tools(self) -> List[BaseTool]:
        """Get all registered tools"""
        return list(self._tools.values())
    
    def get_tool_names(self) -> List[str]:
        """Get names of all registered tools"""
        return list(self._tools.keys())
    
    def has_tool(self, name: str) -> bool:
        """Check if a tool is registered"""
        return name in self._tools


# Global tools registry instance
tools_registry = ToolsRegistry()


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