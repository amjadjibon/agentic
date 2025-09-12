from langchain_core.tools import BaseTool
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun
from pydantic import BaseModel, Field

wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())


class SafeWikipediaInput(BaseModel):
    """Input for safe Wikipedia search tool"""
    query: str = Field(description="The Wikipedia search query")


class SafeWikipediaTool(BaseTool):
    """Safe Wikipedia search tool that handles unexpected parameters"""
    
    name: str = "search_wikipedia" 
    description: str = "Search Wikipedia for information about the given query. This tool is useful when you need to search Wikipedia for information about the given query."
    args_schema: type = SafeWikipediaInput
    
    def _run(self, **kwargs) -> str:
        """Run the Wikipedia search with robust parameter handling"""
        print(f"🔍 DEBUG: SafeWikipediaTool._run called")
        print(f"🔍 DEBUG: kwargs: {kwargs}")
        print(f"🔍 DEBUG: kwargs keys: {list(kwargs.keys())}")
        
        try:
            # Extract query from kwargs, handling various parameter names
            query = None
            for key in ['query', 'search_query', 'q', 'input', 'text']:
                if key in kwargs and kwargs[key]:
                    query = kwargs[key]
                    break
            
            if not query:
                # Fallback: take first string value
                for key, value in kwargs.items():
                    if isinstance(value, str) and value.strip():
                        query = value
                        break
            
            if not query:
                return "Error: No Wikipedia search query provided"
            
            print(f"🔍 DEBUG: Extracted Wikipedia query: {query}")
            
            result = wikipedia.run(query)
            print(f"🔍 DEBUG: Wikipedia search successful, result length: {len(str(result))}")
            return result
            
        except Exception as e:
            print(f"🔍 DEBUG: SafeWikipediaTool error: {str(e)}")
            print(f"🔍 DEBUG: Error type: {type(e)}")
            if "unexpected keyword argument" in str(e):
                print(f"🔍 DEBUG: CAUGHT UNEXPECTED KEYWORD ERROR in Wikipedia tool!")
                return f"Wikipedia search failed due to parameter error: {str(e)}"
            else:
                return f"Wikipedia search failed: {str(e)}"


# Create the safe Wikipedia search tool instance
search_wikipedia = SafeWikipediaTool()
