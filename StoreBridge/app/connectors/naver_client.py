"""Naver Commerce API client."""

import logging
from typing import Any, Dict, Optional

import httpx

from app.config import settings
from app.services.rate_limiter import NaverRateLimiter

logger = logging.getLogger(__name__)


class NaverClient:
    """
    Client for Naver Commerce API.

    API Constraints:
    - Rate limit: 2 TPS (SEVERE bottleneck!)
    - Authentication: OAuth 2.0
    - IP whitelist required
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        api_url: Optional[str] = None,
        rate_limiter: Optional[NaverRateLimiter] = None,
        timeout: float = 30.0,
    ) -> None:
        """
        Initialize Naver Commerce API client.

        Args:
            client_id: OAuth client ID (default: from settings)
            client_secret: OAuth client secret (default: from settings)
            api_url: API base URL (default: from settings)
            rate_limiter: Rate limiter instance (default: create new)
            timeout: Request timeout in seconds (default: 30.0)
        """
        self.client_id = client_id or settings.naver_client_id
        self.client_secret = client_secret or settings.naver_client_secret
        self.api_url = api_url or settings.naver_api_url
        self.rate_limiter = rate_limiter or NaverRateLimiter()
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self._access_token: Optional[str] = None

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.api_url,
                timeout=self.timeout,
                headers={
                    "User-Agent": "StoreBridge/1.0",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def _ensure_authenticated(self) -> None:
        """Ensure OAuth access token is valid."""
        if self._access_token is None:
            await self._refresh_token()

    async def _refresh_token(self) -> None:
        """Refresh OAuth access token."""
        client = self._get_client()

        try:
            response = await client.post(
                "/oauth2.0/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials",
                },
            )
            response.raise_for_status()

            data = response.json()
            self._access_token = data["access_token"]
            logger.info("OAuth token refreshed successfully")

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to refresh OAuth token: {e}")
            raise

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Make authenticated API request with rate limiting.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint
            data: Request body (for POST/PUT)
            params: Query parameters

        Returns:
            Response JSON data

        Raises:
            Exception: If rate limit exceeded or API error
        """
        # Ensure authenticated
        await self._ensure_authenticated()

        # Acquire rate limit token
        if not await self.rate_limiter.acquire_with_wait(max_retries=5, backoff=0.5):
            raise Exception("Rate limit exceeded after retries")

        client = self._get_client()
        headers = {"Authorization": f"Bearer {self._access_token}"}

        try:
            if method.upper() == "GET":
                response = await client.get(endpoint, params=params, headers=headers)
            elif method.upper() == "POST":
                response = await client.post(endpoint, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = await client.put(endpoint, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = await client.delete(endpoint, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.error("Naver API rate limit exceeded (2 TPS)")
                raise Exception("Rate limit exceeded") from e
            elif e.response.status_code == 401:
                # Token expired, refresh and retry once
                logger.warning("OAuth token expired, refreshing...")
                await self._refresh_token()
                # Retry once (recursive call)
                return await self._make_request(method, endpoint, data, params)
            else:
                logger.error(f"Naver API error: {e.response.text}")
                raise

    async def upload_image(self, image_data: bytes, filename: str = "image.jpg") -> Dict[str, Any]:
        """
        Upload image to Naver CDN.

        Args:
            image_data: Image binary data
            filename: Image filename

        Returns:
            {
                "success": True,
                "image_url": "https://shopping-phinf.pstatic.net/..."
            }
        """
        await self._ensure_authenticated()

        # Acquire rate limit token
        if not await self.rate_limiter.acquire_with_wait():
            raise Exception("Rate limit exceeded")

        client = self._get_client()
        headers = {"Authorization": f"Bearer {self._access_token}"}

        try:
            files = {"image": (filename, image_data, "image/jpeg")}
            response = await client.post(
                "/v1/product-images/upload", files=files, headers=headers
            )
            response.raise_for_status()

            data = response.json()
            return {"success": True, "image_url": data["imageUrl"]}

        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to upload image: {e}")
            raise

    async def register_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Register product to Naver Smart Store.

        Args:
            product_data: Product data in Naver format
                {
                    "originProduct": {
                        "name": "상품명",
                        "salePrice": 10000,
                        "categoryId": "50000000",
                        "images": [{"url": "https://..."}],
                        "detailContent": "상품 상세 설명",
                        "optionCombinations": [...]
                    }
                }

        Returns:
            {
                "success": True,
                "originProductNo": "12345"
            }
        """
        data = await self._make_request("POST", "/v2/products", data=product_data)

        return {
            "success": True,
            "originProductNo": data.get("originProductNo"),
        }

    async def get_product(self, product_id: str) -> Dict[str, Any]:
        """
        Get product detail from Naver.

        Args:
            product_id: Naver product ID

        Returns:
            Product detail data
        """
        data = await self._make_request("GET", f"/v2/products/{product_id}")
        return data

    async def update_product(
        self, product_id: str, product_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update product in Naver Smart Store.

        Args:
            product_id: Naver product ID
            product_data: Updated product data

        Returns:
            {
                "success": True,
                "originProductNo": "12345"
            }
        """
        data = await self._make_request("PUT", f"/v2/products/{product_id}", data=product_data)

        return {
            "success": True,
            "originProductNo": data.get("originProductNo"),
        }

    async def delete_product(self, product_id: str) -> Dict[str, Any]:
        """
        Delete product from Naver Smart Store.

        Args:
            product_id: Naver product ID

        Returns:
            {"success": True}
        """
        await self._make_request("DELETE", f"/v2/products/{product_id}")
        return {"success": True}

    async def get_category_attributes(self, category_id: str) -> Dict[str, Any]:
        """
        Get required attributes for a category.

        Args:
            category_id: Naver category ID

        Returns:
            {
                "categoryId": "50000000",
                "requiredAttributes": [
                    {"name": "제조일자", "type": "date"},
                    {"name": "세탁방법", "type": "string"}
                ]
            }
        """
        data = await self._make_request("GET", f"/v1/categories/{category_id}/attributes")
        return data

    async def close(self) -> None:
        """Close HTTP client and rate limiter."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        await self.rate_limiter.close()

    async def __aenter__(self) -> "NaverClient":
        """Async context manager enter."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
