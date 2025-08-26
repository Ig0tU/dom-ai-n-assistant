import json
import pytest
from unittest.mock import Mock
from auraflow.app.agents.sales_fulfillment import SalesFulfillmentAgent

@pytest.fixture
def mock_openai_client():
    client = Mock()
    mock_copy = {
        "headline": "Test Headline",
        "subheader": "Test Subheader",
        "cta_button_text": "Buy Test",
        "features": ["Feature 1", "Feature 2"]
    }
    client.query.return_value = json.dumps(mock_copy)
    return client

@pytest.fixture
def mock_stripe_client():
    client = Mock()
    client.create_product_and_payment_link.return_value = "https://fake-stripe-link.com/123"
    return client

@pytest.fixture
def mock_vercel_client():
    client = Mock()
    client.deploy_static_site.return_value = "https://fake-vercel-deploy.com"
    return client

@pytest.fixture(autouse=True)
def mock_env(monkeypatch):
    """Mock environment variables."""
    monkeypatch.setenv("VENTURE_PRODUCT_PRICE_CENTS", "1234")

def test_create_and_deploy_storefront_success(
    mock_openai_client, mock_stripe_client, mock_vercel_client
):
    """
    Test N3: Tests the SalesFulfillmentAgent's storefront creation process.
    Verifies that it calls the Stripe and Vercel clients correctly.
    """
    # Arrange
    agent = SalesFulfillmentAgent(
        openai_client=mock_openai_client,
        stripe_client=mock_stripe_client,
        vercel_client=mock_vercel_client
    )
    venture_id = "test-venture-xyz"
    product_details = {"niche_idea": {"chosen_topic": "Test E-Book Topic"}}

    # Mock the template files
    # This is complex, so for a unit test, we can assume the files exist.
    # A better approach for integration testing would be needed.

    # Act
    result = agent.create_and_deploy_storefront(venture_id, product_details)

    # Assert
    assert result is not None

    # Verify Stripe call
    mock_stripe_client.create_product_and_payment_link.assert_called_once_with(
        "Test E-Book Topic", 1234
    )
    assert result["payment_link_url"] == "https://fake-stripe-link.com/123"

    # Verify Vercel call
    mock_vercel_client.deploy_static_site.assert_called_once()
    call_args, call_kwargs = mock_vercel_client.deploy_static_site.call_args
    assert call_kwargs['project_name'] == f"auraflow-venture-{venture_id[:8]}"
    assert "index.html" in call_kwargs['files_content']
    assert "style.css" in call_kwargs['files_content']
    assert result["landing_page_url"] == "https://fake-vercel-deploy.com"

    # Verify OpenAI call
    mock_openai_client.query.assert_called_once()
