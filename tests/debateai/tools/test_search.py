from debateai.tools.search import search_web


def test_search_web():
    result = search_web("What is the capital of France?")
    assert "Paris" in result
