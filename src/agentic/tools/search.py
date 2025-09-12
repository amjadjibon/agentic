from langchain_core.tools import BaseTool
from langchain_community.tools import DuckDuckGoSearchRun
from pydantic import BaseModel, Field

search = DuckDuckGoSearchRun()


class SafeSearchInput(BaseModel):
    """Input for safe web search tool"""
    query: str = Field(description="The search query")


class SafeSearchTool(BaseTool):
    """Safe web search tool that handles unexpected parameters"""
    
    name: str = "search_web"
    description: str = "Search the web for information about the given query. This tool is useful when you need to search the web for information about the given query."
    args_schema: type = SafeSearchInput
    
    def _run(self, query: str = None, **kwargs) -> str:
        """Run the search with robust parameter handling"""
        try:
            # Extract query, preferring the direct parameter first
            search_query = query
            
            if not search_query and kwargs:
                # Extract query from kwargs, handling various parameter names
                for key in ['query', 'search_query', 'q', 'input', 'text']:
                    if key in kwargs and kwargs[key]:
                        search_query = kwargs[key]
                        break
                
                if not search_query:
                    # Fallback: take first string value
                    for key, value in kwargs.items():
                        if isinstance(value, str) and value.strip():
                            search_query = value
                            break
            
            if not search_query:
                return "Error: No search query provided. Please provide a 'query' parameter."
            
            result = search.invoke(search_query)
            return result
            
        except Exception as e:
            if "unexpected keyword argument" in str(e):
                return f"Search failed due to parameter error: {str(e)}"
            else:
                return f"Search failed: {str(e)}"


# Create the safe search tool instance
search_web = SafeSearchTool()
