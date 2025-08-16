from agentic.tools.wikipedia import search_wikipedia


def test_search_wikipedia():
    result = search_wikipedia("What is the capital of France?")
    assert "Paris" in result
