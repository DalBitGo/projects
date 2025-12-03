"""Integration tests for Domeggook API client."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import httpx

from app.connectors.domeggook_client import DomeggookClient


class TestDomeggookClientIntegration:
    """Integration tests for DomeggookClient with mocked HTTP responses."""

    @pytest.mark.asyncio
    async def test_get_item_list_success(self):
        """상품 리스트 가져오기 성공."""
        # Create mock client
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "total_count": 100,
            "items": [
                {
                    "item_id": "DG-001",
                    "item_name": "테스트 상품",
                    "price": 10000,
                    "category": "패션의류",
                    "image_url": "https://example.com/image.jpg",
                }
            ],
        }
        mock_client.get.return_value = mock_response

        client = DomeggookClient(api_key="test_key")
        client._client = mock_client

        result = await client.get_item_list(page=1, page_size=10)

        assert result["success"] is True
        assert result["total_count"] == 100
        assert len(result["items"]) == 1
        assert result["items"][0]["item_id"] == "DG-001"

    @pytest.mark.asyncio
    async def test_get_item_view_success(self):
        """상품 상세 정보 조회 성공."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "item": {
                "item_id": "DG-001",
                "item_name": "테스트 상품",
                "price": 10000,
                "images": ["https://example.com/1.jpg"],
                "options": ["블랙-S", "블랙-M"],
            }
        }
        mock_client.get.return_value = mock_response

        client = DomeggookClient(api_key="test_key")
        client._client = mock_client

        result = await client.get_item_view("DG-001")

        assert result["success"] is True
        assert result["item"]["item_id"] == "DG-001"
        assert len(result["item"]["images"]) == 1

    @pytest.mark.asyncio
    async def test_rate_limit_error_429(self):
        """Rate limit 초과 (429) 에러 처리."""
        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Too Many Requests",
            request=MagicMock(),
            response=mock_response,
        )
        mock_client.get.return_value = mock_response

        client = DomeggookClient(api_key="test_key")
        client._client = mock_client

        with pytest.raises(Exception, match="Rate limit exceeded"):
            await client.get_item_list()

    @pytest.mark.asyncio
    async def test_euc_kr_encoding_fallback(self):
        """EUC-KR 인코딩 폴백 처리."""
        euc_kr_data = '{"item": {"item_name": "한글상품"}}'.encode("euc-kr")

        mock_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.side_effect = Exception("UTF-8 decode failed")
        mock_response.content = euc_kr_data
        mock_client.get.return_value = mock_response

        client = DomeggookClient(api_key="test_key")
        client._client = mock_client

        result = await client.get_item_view("DG-001")

        assert result["success"] is True
        assert result["item"]["item_name"] == "한글상품"

    @pytest.mark.asyncio
    async def test_context_manager_closes_client(self):
        """Context manager가 client를 올바르게 종료."""
        client = DomeggookClient(api_key="test_key")

        # Manually create a mock client
        mock_client = AsyncMock()
        client._client = mock_client

        await client.close()

        # After close, client should be None
        assert client._client is None
        mock_client.aclose.assert_called_once()
