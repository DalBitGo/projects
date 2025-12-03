"""Domeggook OpenAPI client."""

import logging
from typing import Any, Dict, List, Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


class DomeggookClient:
    """
    Client for Domeggook OpenAPI.

    API Constraints:
    - Rate limit: 180 calls/minute, 15,000/day
    - Encoding: EUC-KR
    - Response format: JSON
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_url: Optional[str] = None,
        timeout: float = 30.0,
    ) -> None:
        """
        Initialize Domeggook API client.

        Args:
            api_key: API key (default: from settings)
            api_url: API base URL (default: from settings)
            timeout: Request timeout in seconds (default: 30.0)
        """
        self.api_key = api_key or settings.domeggook_api_key
        self.api_url = api_url or settings.domeggook_api_url
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.api_url,
                timeout=self.timeout,
                headers={
                    "User-Agent": "StoreBridge/1.0",
                },
            )
        return self._client

    async def get_item_list(
        self,
        page: int = 1,
        page_size: int = 100,
        category: Optional[str] = None,
        keyword: Optional[str] = None,
        price_min: Optional[int] = None,
        price_max: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get product list from Domeggook.

        Args:
            page: Page number (1-indexed)
            page_size: Items per page (max 100)
            category: Category filter
            keyword: Search keyword
            price_min: Minimum price filter
            price_max: Maximum price filter

        Returns:
            {
                "success": True,
                "total_count": 1000,
                "items": [
                    {
                        "item_id": "DG-001",
                        "item_name": "상품명",
                        "price": 10000,
                        "category": "패션의류",
                        "image_url": "https://..."
                    }
                ]
            }

        Raises:
            httpx.HTTPStatusError: If API returns error status
            httpx.TimeoutException: If request times out
        """
        client = self._get_client()

        params = {
            "key": self.api_key,
            "page": page,
            "page_size": page_size,
        }

        if category:
            params["category"] = category
        if keyword:
            params["keyword"] = keyword
        if price_min is not None:
            params["price_min"] = price_min
        if price_max is not None:
            params["price_max"] = price_max

        try:
            response = await client.get("/getItemList", params=params)
            response.raise_for_status()

            # Handle EUC-KR encoding
            data = self._decode_response(response)

            return {
                "success": True,
                "total_count": data.get("total_count", 0),
                "items": data.get("items", []),
            }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error("Rate limit exceeded (180/min or 15,000/day)")
                raise Exception("Rate limit exceeded") from e
            logger.error(f"Domeggook API error: {e}")
            raise
        except httpx.TimeoutException as e:
            logger.error(f"Domeggook API timeout: {e}")
            raise

    async def get_item_view(self, item_id: str) -> Dict[str, Any]:
        """
        Get product detail from Domeggook.

        Args:
            item_id: Product ID

        Returns:
            {
                "success": True,
                "item": {
                    "item_id": "DG-001",
                    "item_name": "상품명",
                    "price": 10000,
                    "category": "패션의류",
                    "images": ["https://...", "https://..."],
                    "description": "상품 상세 설명",
                    "options": ["블랙-S", "블랙-M", "화이트-S"],
                    "stock_quantity": 100
                }
            }
        """
        client = self._get_client()

        params = {
            "key": self.api_key,
            "item_id": item_id,
        }

        try:
            response = await client.get("/getItemView", params=params)
            response.raise_for_status()

            data = self._decode_response(response)

            return {
                "success": True,
                "item": data.get("item", {}),
            }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise Exception("Rate limit exceeded") from e
            logger.error(f"Failed to get item detail: {e}")
            raise

    async def get_category_list(self) -> Dict[str, Any]:
        """
        Get category list from Domeggook.

        Returns:
            {
                "success": True,
                "categories": [
                    {"id": "1", "name": "패션의류", "parent_id": None},
                    {"id": "2", "name": "티셔츠", "parent_id": "1"}
                ]
            }
        """
        client = self._get_client()

        params = {"key": self.api_key}

        try:
            response = await client.get("/getCategoryList", params=params)
            response.raise_for_status()

            data = self._decode_response(response)

            return {
                "success": True,
                "categories": data.get("categories", []),
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to get categories: {e}")
            raise

    def _decode_response(self, response: httpx.Response) -> Dict[str, Any]:
        """
        Decode response with EUC-KR encoding handling.

        Args:
            response: HTTP response

        Returns:
            Decoded JSON data
        """
        try:
            # Try UTF-8 first (modern APIs)
            return response.json()
        except Exception:
            # Fallback to EUC-KR
            try:
                content = response.content.decode("euc-kr")
                import json

                return json.loads(content)
            except Exception as e:
                logger.error(f"Failed to decode response: {e}")
                raise

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self) -> "DomeggookClient":
        """Async context manager enter."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
