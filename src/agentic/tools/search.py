from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun


search = DuckDuckGoSearchRun()


@tool
def search_web(query: str) -> str:
    """
    Search the web for information about the given query.
    This tool is useful when you need to search the web for information about the given query.

    Args:
        query (str): The query to search the web for.

    Returns:
        str: The results of the search.
    """
    return search.invoke(query)
