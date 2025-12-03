"""Simple E2E tests for core functionality (without Celery/DB)."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.connectors.domeggook_client import DomeggookClient
from app.connectors.naver_client import NaverClient
from app.services.option_mapper import OptionMapper
from app.validators.product_validator import ProductValidator


class TestSimpleProductFlow:
    """E2E test for product data flow (without database/celery)."""

    @pytest.mark.asyncio
    async def test_complete_product_transformation(self):
        """
        전체 플로우 테스트: 도매꾹 → 변환 → 검증 → 네이버 포맷

        플로우:
        1. 도매꾹에서 상품 데이터 가져오기 (mock)
        2. 옵션 파싱 및 변환
        3. 상품 검증
        4. 네이버 포맷으로 변환
        5. 네이버 API로 등록 (mock)
        """
        # Step 1: Mock Domeggook API - 상품 데이터 가져오기
        domeggook_product = {
            "item_id": "DG-12345",
            "item_name": "남성용 반팔 티셔츠",
            "price": 15000,
            "category": "패션의류",
            "images": [
                "https://example.com/image1.jpg",
                "https://example.com/image2.jpg",
            ],
            "description": "편안한 여름용 티셔츠입니다.",
            "options": ["블랙-S", "블랙-M", "블랙-L", "화이트-M", "화이트-L"],
            "stock_quantity": 100,
        }

        mock_domeggook_client = AsyncMock()
        mock_response = MagicMock()
        mock_response.json.return_value = {"item": domeggook_product}
        mock_domeggook_client.get.return_value = mock_response

        client = DomeggookClient(api_key="test_key")
        client._client = mock_domeggook_client

        domeggook_result = await client.get_item_view("DG-12345")
        product_data = domeggook_result["item"]

        # Step 2: 옵션 파싱
        mapper = OptionMapper()
        parsed_options = mapper.parse(product_data["options"])

        assert parsed_options["type"] == "COMBINATION"
        assert parsed_options["separator"] == "-"
        assert len(parsed_options["dimensions"]) == 2
        assert len(parsed_options["combinations"]) == 5

        # Step 3: 상품 검증
        validator = ProductValidator()

        # Valid product should pass
        validation_result = validator.validate({
            "name": product_data["item_name"],
            "price": product_data["price"],
            "images": product_data["images"],
            "description": product_data["description"],
            "category": product_data["category"],
        })
        assert validation_result.is_valid is True
        assert len(validation_result.errors) == 0

        # Step 4: 네이버 포맷으로 변환
        naver_options = mapper.to_naver_format(parsed_options)

        assert naver_options["optionType"] == "COMBINATION"
        assert len(naver_options["optionCombinations"]) == 5

        # Verify first combination
        first_combo = naver_options["optionCombinations"][0]
        assert "optionName1" in first_combo
        assert "optionValue1" in first_combo
        assert "optionName2" in first_combo
        assert "optionValue2" in first_combo

        # Step 5: 네이버 상품 등록 (mock)
        naver_product_data = {
            "originProduct": {
                "name": product_data["item_name"],
                "salePrice": product_data["price"],
                "categoryId": "50000000",  # 의류 카테고리
                "images": [{"url": img} for img in product_data["images"]],
                "detailContent": product_data["description"],
                **naver_options,
            }
        }

        mock_naver_client = AsyncMock()
        mock_rate_limiter = AsyncMock()
        mock_rate_limiter.acquire_with_wait.return_value = True
        mock_rate_limiter.close = AsyncMock()

        token_response = MagicMock()
        token_response.json.return_value = {"access_token": "test_token"}

        register_response = MagicMock()
        register_response.json.return_value = {"originProductNo": "NV-98765"}

        mock_naver_client.post.side_effect = [token_response, register_response]

        naver_client = NaverClient(
            client_id="test_id",
            client_secret="test_secret",
            rate_limiter=mock_rate_limiter,
        )
        naver_client._client = mock_naver_client

        result = await naver_client.register_product(naver_product_data)

        assert result["success"] is True
        assert result["originProductNo"] == "NV-98765"

        # Cleanup
        await naver_client.close()

    @pytest.mark.asyncio
    async def test_product_validation_rejection(self):
        """검증 실패 케이스 - 필수 필드 누락."""
        validator = ProductValidator()

        # Product missing required field should fail
        result = validator.validate({
            "price": 10000,
            "images": ["https://example.com/img.jpg"],
            # Missing "name" and "description"
        })

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("name" in err for err in result.errors)
        assert any("description" in err for err in result.errors)

    @pytest.mark.asyncio
    async def test_product_validation_negative_price(self):
        """검증 실패 케이스 - 음수 가격."""
        validator = ProductValidator()

        result = validator.validate({
            "name": "정상 상품명",
            "price": -1000,  # Negative price
            "images": ["https://example.com/img.jpg"],
            "description": "설명",
            "category": "패션의류",
        })

        assert result.is_valid is False
        assert any("non-negative" in err for err in result.errors)

    @pytest.mark.asyncio
    async def test_option_parsing_various_formats(self):
        """다양한 옵션 형식 파싱 테스트."""
        mapper = OptionMapper()

        # 1D options
        result_1d = mapper.parse(["블랙", "화이트", "네이비"])
        assert result_1d["type"] == "SIMPLE"
        assert len(result_1d["dimensions"]) == 1

        # 2D options with dash
        result_2d_dash = mapper.parse(["블랙-S", "블랙-M", "화이트-S"])
        assert result_2d_dash["type"] == "COMBINATION"
        assert result_2d_dash["separator"] == "-"
        assert len(result_2d_dash["dimensions"]) == 2

        # 2D options with slash
        result_2d_slash = mapper.parse(["레드/L", "블루/XL"])
        assert result_2d_slash["type"] == "COMBINATION"
        assert result_2d_slash["separator"] == "/"

        # 3D options
        result_3d = mapper.parse(["블랙-S-면", "블랙-M-폴리", "화이트-S-면"])
        assert result_3d["type"] == "COMBINATION"
        assert len(result_3d["dimensions"]) == 3

    @pytest.mark.asyncio
    async def test_rate_limiter_integration_with_naver_client(self):
        """Rate limiter와 Naver 클라이언트 통합 테스트."""
        # Mock rate limiter that blocks
        mock_rate_limiter = AsyncMock()
        mock_rate_limiter.acquire_with_wait.return_value = False  # Blocked
        mock_rate_limiter.close = AsyncMock()

        mock_naver_client = AsyncMock()
        token_response = MagicMock()
        token_response.json.return_value = {"access_token": "test_token"}
        mock_naver_client.post.return_value = token_response

        naver_client = NaverClient(
            client_id="test_id",
            client_secret="test_secret",
            rate_limiter=mock_rate_limiter,
        )
        naver_client._client = mock_naver_client

        # Should fail due to rate limiting
        with pytest.raises(Exception, match="Rate limit exceeded"):
            await naver_client.register_product({"originProduct": {}})

        await naver_client.close()
