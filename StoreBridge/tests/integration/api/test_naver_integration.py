"""Integration tests for Naver Commerce API client."""

import pytest
from unittest.mock import AsyncMock, MagicMock
import httpx

from app.connectors.naver_client import NaverClient
from app.services.rate_limiter import NaverRateLimiter


class TestNaverClientIntegration:
    """Integration tests for NaverClient with mocked HTTP responses."""

    @pytest.fixture
    def mock_rate_limiter(self):
        """Mock rate limiter that always allows requests."""
        limiter = AsyncMock(spec=NaverRateLimiter)
        limiter.acquire_with_wait.return_value = True
        limiter.close = AsyncMock()
        return limiter

    @pytest.mark.asyncio
    async def test_register_product_success(self, mock_rate_limiter):
        """상품 등록 성공."""
        mock_client = AsyncMock()

        # First call: OAuth token
        token_response = MagicMock()
        token_response.json.return_value = {"access_token": "test_token_123"}

        # Second call: Product registration
        register_response = MagicMock()
        register_response.json.return_value = {"originProductNo": "12345"}

        mock_client.post.side_effect = [token_response, register_response]

        client = NaverClient(
            client_id="test_id",
            client_secret="test_secret",
            rate_limiter=mock_rate_limiter,
        )
        client._client = mock_client

        product_data = {
            "originProduct": {
                "name": "테스트 상품",
                "salePrice": 10000,
                "categoryId": "50000000",
            }
        }

        result = await client.register_product(product_data)

        assert result["success"] is True
        assert result["originProductNo"] == "12345"
        mock_rate_limiter.acquire_with_wait.assert_called()

    @pytest.mark.asyncio
    async def test_oauth_token_refresh_on_401(self, mock_rate_limiter):
        """401 에러 시 토큰 자동 갱신."""
        mock_client = AsyncMock()

        # OAuth tokens
        token_response_1 = MagicMock()
        token_response_1.json.return_value = {"access_token": "old_token"}

        token_response_2 = MagicMock()
        token_response_2.json.return_value = {"access_token": "new_token"}

        # API call 401 error
        api_response_401 = MagicMock()
        api_response_401.status_code = 401
        api_response_401.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Unauthorized",
            request=MagicMock(),
            response=api_response_401,
        )

        # Retry success
        api_response_success = MagicMock()
        api_response_success.json.return_value = {"originProductNo": "67890"}

        mock_client.post.side_effect = [
            token_response_1,
            api_response_401,
            token_response_2,
            api_response_success,
        ]

        client = NaverClient(
            client_id="test_id",
            client_secret="test_secret",
            rate_limiter=mock_rate_limiter,
        )
        client._client = mock_client

        result = await client.register_product({"originProduct": {}})

        assert result["success"] is True
        assert result["originProductNo"] == "67890"
        assert mock_client.post.call_count == 4

    @pytest.mark.asyncio
    async def test_rate_limit_blocks_request(self, mock_rate_limiter):
        """Rate limiter가 요청을 차단."""
        mock_rate_limiter.acquire_with_wait.return_value = False

        mock_client = AsyncMock()
        token_response = MagicMock()
        token_response.json.return_value = {"access_token": "test_token"}
        mock_client.post.return_value = token_response

        client = NaverClient(
            client_id="test_id",
            client_secret="test_secret",
            rate_limiter=mock_rate_limiter,
        )
        client._client = mock_client

        with pytest.raises(Exception, match="Rate limit exceeded"):
            await client.register_product({"originProduct": {}})

    @pytest.mark.asyncio
    async def test_upload_image_success(self, mock_rate_limiter):
        """이미지 업로드 성공."""
        mock_client = AsyncMock()

        token_response = MagicMock()
        token_response.json.return_value = {"access_token": "test_token"}

        upload_response = MagicMock()
        upload_response.json.return_value = {
            "imageUrl": "https://shopping-phinf.pstatic.net/test.jpg"
        }

        mock_client.post.side_effect = [token_response, upload_response]

        client = NaverClient(
            client_id="test_id",
            client_secret="test_secret",
            rate_limiter=mock_rate_limiter,
        )
        client._client = mock_client

        image_data = b"fake_image_data"
        result = await client.upload_image(image_data, "test.jpg")

        assert result["success"] is True
        assert "pstatic.net" in result["image_url"]

    @pytest.mark.asyncio
    async def test_get_product_success(self, mock_rate_limiter):
        """상품 조회 성공."""
        mock_client = AsyncMock()

        token_response = MagicMock()
        token_response.json.return_value = {"access_token": "test_token"}

        get_response = MagicMock()
        get_response.json.return_value = {
            "originProductNo": "12345",
            "name": "테스트 상품",
            "salePrice": 10000,
        }

        mock_client.post.return_value = token_response
        mock_client.get.return_value = get_response

        client = NaverClient(
            client_id="test_id",
            client_secret="test_secret",
            rate_limiter=mock_rate_limiter,
        )
        client._client = mock_client

        result = await client.get_product("12345")

        assert result["originProductNo"] == "12345"
        assert result["name"] == "테스트 상품"

    @pytest.mark.asyncio
    async def test_naver_api_error_429(self, mock_rate_limiter):
        """Naver API 429 에러 처리."""
        mock_client = AsyncMock()

        token_response = MagicMock()
        token_response.json.return_value = {"access_token": "test_token"}

        api_response_429 = MagicMock()
        api_response_429.status_code = 429
        api_response_429.raise_for_status.side_effect = httpx.HTTPStatusError(
            "Too Many Requests",
            request=MagicMock(),
            response=api_response_429,
        )

        mock_client.post.side_effect = [token_response, api_response_429]

        client = NaverClient(
            client_id="test_id",
            client_secret="test_secret",
            rate_limiter=mock_rate_limiter,
        )
        client._client = mock_client

        with pytest.raises(Exception, match="Rate limit exceeded"):
            await client.register_product({"originProduct": {}})

    @pytest.mark.asyncio
    async def test_context_manager_closes_resources(self, mock_rate_limiter):
        """Context manager가 모든 리소스를 올바르게 종료."""
        client = NaverClient(
            client_id="test_id",
            client_secret="test_secret",
            rate_limiter=mock_rate_limiter,
        )

        mock_client = AsyncMock()
        client._client = mock_client

        await client.close()

        assert client._client is None
        mock_client.aclose.assert_called_once()
        mock_rate_limiter.close.assert_called_once()
