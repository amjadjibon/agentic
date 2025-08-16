import os

from langchain_core.tools import tool
from langchain_community.document_loaders import BrowserlessLoader


@tool
def scrape_website(url: str) -> str:
    """
    Scrape a website and return the content.
    This tool is useful when you need to scrape a website and return the content.

    Args:
        url (str): The URL of the website to scrape.

    Returns:
        str: The content of the website.
    """
    browserless_api_key = os.getenv("BROWSERLESS_API_KEY")
    if not browserless_api_key:
        raise ValueError("BROWSERLESS_API_KEY is not set")
    
    loader = BrowserlessLoader(api_key=browserless_api_key)
    
    documents = loader.load(url)
    result = ""
    for document in documents:
        result += document.page_content
    return result
