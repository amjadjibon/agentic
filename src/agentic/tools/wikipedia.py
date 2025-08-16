from langchain_core.tools import tool
from langchain_community.utilities import WikipediaAPIWrapper
from langchain_community.tools import WikipediaQueryRun

wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

@tool
def search_wikipedia(query: str) -> str:
    """Search Wikipedia for information about the given query.
    This tool is useful when you need to search Wikipedia for information about the given query.

    Args:
        query (str): The query to search Wikipedia for.

    Returns:
        str: The results of the search.
    """
    return wikipedia.run(query)
