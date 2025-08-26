import pytest
from unittest.mock import Mock, call
from auraflow.app.agents.product_generation import ProductGenerationAgent

@pytest.fixture
def mock_openai_client():
    """Fixture for a mocked OpenAI client that returns outline and chapter content."""
    client = Mock()
    # Configure the mock to return different values on subsequent calls
    client.query.side_effect = [
        # First call (outline)
        "Chapter 1: Introduction\nChapter 2: The Core Idea",
        # Second call (content for Chapter 1)
        "This is the introduction content.",
        # Third call (content for Chapter 2)
        "This is the core idea content."
    ]
    return client

def test_generate_ebook_success(mock_openai_client, tmp_path):
    """
    Test N2: Tests the ProductGenerationAgent's generate_ebook method.
    Verifies that it generates a complete Markdown file from a topic.
    """
    # Arrange
    agent = ProductGenerationAgent(openai_client=mock_openai_client)
    venture_id = "test-venture-123"
    topic = "AI Productivity"

    # Override the ventures path to use the temporary directory
    # This is a bit of a hack; a better way would be to make the path configurable.
    # For this test, we can patch the 'open' call or the os.makedirs call.
    # But for simplicity, we'll just check the output path.
    # In a real app, the base path `ventures` would be passed in or be a setting.

    # We will temporarily modify the working directory for the test
    # so the ventures folder is created inside tmp_path
    import os
    original_cwd = os.getcwd()
    os.chdir(tmp_path)

    # Act
    result = agent.generate_ebook(venture_id, topic)

    # Assert
    assert result is not None
    ebook_path = result["ebook_path"]
    assert ebook_path == f"ventures/{venture_id}/product.md"

    # Check that the file was created and has the correct content
    assert (tmp_path / ebook_path).exists()

    content = (tmp_path / ebook_path).read_text(encoding="utf-8")
    assert "# AI Productivity" in content
    assert "## Chapter 1: Introduction" in content
    assert "This is the introduction content." in content
    assert "## Chapter 2: The Core Idea" in content
    assert "This is the core idea content." in content

    # Verify that the OpenAI client was called correctly
    assert mock_openai_client.query.call_count == 3

    # Restore original working directory
    os.chdir(original_cwd)

def test_generate_ebook_no_outline(mock_openai_client):
    """
    Tests that generate_ebook returns None if the LLM fails to produce an outline.
    """
    # Arrange
    mock_openai_client.query.side_effect = [None] # First call returns None
    agent = ProductGenerationAgent(openai_client=mock_openai_client)

    # Act
    result = agent.generate_ebook("test-venture", "A Topic")

    # Assert
    assert result is None
    mock_openai_client.query.assert_called_once()
