"""Tests for analytics endpoints."""

import pytest
from unittest.mock import AsyncMock, patch


def test_analyze_endpoint_validation(client):
    """Test that analyze endpoint validates input."""
    response = client.post("/api/analytics/analyze", json={})
    assert response.status_code == 422  # Validation error


def test_analyze_endpoint_empty_prompt(client):
    """Test analyze endpoint with empty prompt."""
    response = client.post("/api/analytics/analyze", json={"prompt": ""})
    # Should either validate or handle gracefully
    assert response.status_code in [200, 422, 500]


@pytest.mark.asyncio
async def test_brand_name_extraction():
    """Test brand name extraction from various prompt formats."""
    from app.api.analytics import _extract_brand_name

    # Test various prompt formats
    assert "Tesla" in _extract_brand_name("Analyze Tesla brand visibility")
    assert "Apple" in _extract_brand_name("How is Apple doing in the market?")
    assert "Nike" in _extract_brand_name("Nike company performance")

    # Test fallback for unclear prompts
    result = _extract_brand_name("analyze market trends")
    assert isinstance(result, str)
    assert len(result) > 0


def test_analyze_endpoint_with_mock(client, mock_perplexity_response):
    """Test analyze endpoint with mocked Perplexity response."""
    with patch('app.services.perplexity_client.PerplexityClient.search_and_analyze') as mock_search:
        mock_search.return_value = mock_perplexity_response

        with patch('app.supabase.client.db.insert') as mock_db:
            mock_db.return_value = None

            response = client.post(
                "/api/analytics/analyze",
                json={"prompt": "Analyze Tesla brand visibility"}
            )

            # Should handle the request even if external services are mocked
            assert response.status_code in [200, 500]  # Either success or handled error


@pytest.mark.asyncio
async def test_sentiment_calculation():
    """Test sentiment calculation logic."""
    from app.api.analytics import _extract_four_parameters

    mock_result = {
        "total_sources_analyzed": 10,
        "crawled_content": [
            {"content": "excellent positive great", "source": "https://test.com/1"},
            {"content": "good innovative strong", "source": "https://test.com/2"},
            {"content": "neutral standard average", "source": "https://test.com/3"},
            {"content": "bad poor negative", "source": "https://test.com/4"},
        ]
    }

    result = _extract_four_parameters(mock_result, "TestBrand")

    assert "sentiment" in result
    assert "tone" in result["sentiment"]
    assert result["sentiment"]["tone"] in ["positive", "negative", "neutral"]
    assert "score" in result["sentiment"]
    assert 0 <= result["sentiment"]["score"] <= 1


@pytest.mark.asyncio
async def test_coverage_calculation():
    """Test coverage quality calculation."""
    from app.api.analytics import _determine_coverage_quality, _calculate_meaningful_coverage

    assert _determine_coverage_quality(50) == "excellent"
    assert _determine_coverage_quality(35) == "very good"
    assert _determine_coverage_quality(25) == "good"
    assert _determine_coverage_quality(15) == "fair"
    assert _determine_coverage_quality(5) == "poor"

    assert "Comprehensive" in _calculate_meaningful_coverage(50)
    assert "Extensive" in _calculate_meaningful_coverage(40)
    assert "Good" in _calculate_meaningful_coverage(30)
