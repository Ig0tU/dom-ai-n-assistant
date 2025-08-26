import json
import pytest
from unittest.mock import Mock
from auraflow.app.agents.market_research import MarketResearchAgent

@pytest.fixture
def mock_openai_client():
    """Fixture for a mocked OpenAI client."""
    client = Mock()
    mock_response = {
        "chosen_topic": "AI-Powered Cover Letter Generator",
        "target_audience": "Job seekers looking to optimize their applications.",
        "reasoning": "This idea solves a clear, painful problem and has a large, motivated target audience."
    }
    client.query.return_value = json.dumps(mock_response)
    return client

@pytest.fixture
def mock_reddit_client():
    """Fixture for a mocked Reddit client."""
    client = Mock()
    client.get_hot_posts.return_value = [
        "I built an AI-Powered Cover Letter Generator",
        "Show r/SideProject: A tool to track your crypto portfolio",
        "My new app helps you find the best local coffee shops"
    ]
    return client

def test_find_niche_success(mock_openai_client, mock_reddit_client):
    """
    Test N1: Tests the MarketResearchAgent's find_niche method for successful execution.
    Verifies that it processes mocked data and returns a structured JSON object.
    """
    # Arrange
    agent = MarketResearchAgent(
        openai_client=mock_openai_client,
        reddit_client=mock_reddit_client
    )

    # Act
    result = agent.find_niche(subreddit="test")

    # Assert
    mock_reddit_client.get_hot_posts.assert_called_once_with("test", limit=15)
    mock_openai_client.query.assert_called_once()

    assert result is not None
    assert result["chosen_topic"] == "AI-Powered Cover Letter Generator"
    assert "target_audience" in result
    assert "reasoning" in result

def test_find_niche_reddit_fails(mock_openai_client, mock_reddit_client):
    """
    Tests that find_niche returns None when the Reddit client fails to fetch posts.
    """
    # Arrange
    mock_reddit_client.get_hot_posts.return_value = [] # Simulate failure
    agent = MarketResearchAgent(
        openai_client=mock_openai_client,
        reddit_client=mock_reddit_client
    )

    # Act
    result = agent.find_niche()

    # Assert
    assert result is None
    mock_openai_client.query.assert_not_called()
