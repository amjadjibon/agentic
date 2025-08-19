from typing import List, Dict
from langchain_core.tools import BaseTool

from agentic.tools.search import search_web
from agentic.tools.wikipedia import search_wikipedia
from agentic.tools.youtube import YOUTUBE_TOOLS
from agentic.tools.offline_competitor import OFFLINE_COMPETITOR_TOOLS
from agentic.tools.strategy_generator import STRATEGY_GENERATOR_TOOLS
from agentic.tools.crawl4ai_competitor import CRAWL4AI_COMPETITOR_TOOLS


class ToolsRegistry:
    """Registry for managing tools available to debate agents"""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """Register default tools"""
        self.register_tool("search_web", search_web)
        self.register_tool("search_wikipedia", search_wikipedia)
        
        # Register YouTube tools
        for tool in YOUTUBE_TOOLS:
            self.register_tool(tool.name, tool)
        
        # Register offline competitor tools (no internet required)
        for tool in OFFLINE_COMPETITOR_TOOLS:
            self.register_tool(tool.name, tool)
        
        # Register strategy generator tools
        for tool in STRATEGY_GENERATOR_TOOLS:
            self.register_tool(tool.name, tool)
        
        # Register Crawl4AI competitor tools (primary competitor analysis)
        for tool in CRAWL4AI_COMPETITOR_TOOLS:
            self.register_tool(tool.name, tool)

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


tools_registry = ToolsRegistry()
