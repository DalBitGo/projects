"""Option mapper unit tests."""

import pytest

from app.services.option_mapper import OptionMapper


@pytest.mark.unit
class TestOptionMapper:
    """Test option mapping (Domeggook → Naver)."""

    @pytest.fixture
    def mapper(self):
        """Create OptionMapper instance."""
        return OptionMapper()

    # ===== 1D Options (Simple) =====

    def test_parse_1d_simple_options(self, mapper):
        """단일 차원 옵션 (색상만)."""
        raw_options = ["블랙", "화이트", "네이비"]

        result = mapper.parse(raw_options)

        assert result["type"] == "SIMPLE"
        assert result["dimension_name"] == "색상"
        assert result["values"] == ["블랙", "화이트", "네이비"]

    def test_parse_1d_size_options(self, mapper):
        """단일 차원 옵션 (사이즈만)."""
        raw_options = ["S", "M", "L", "XL"]

        result = mapper.parse(raw_options)

        assert result["type"] == "SIMPLE"
        assert result["dimension_name"] == "사이즈"

    # ===== 2D Options (Combination) =====

    def test_parse_2d_combination_with_dash(self, mapper):
        """2차원 조합 옵션 (색상-사이즈, separator='-')."""
        raw_options = ["블랙-S", "블랙-M", "화이트-S", "화이트-M"]

        result = mapper.parse(raw_options)

        assert result["type"] == "COMBINATION"
        assert result["separator"] == "-"
        assert len(result["dimensions"]) == 2

        # Dimension 1: 색상
        dim1 = result["dimensions"][0]
        assert dim1["name"] == "색상"
        assert set(dim1["values"]) == {"블랙", "화이트"}

        # Dimension 2: 사이즈
        dim2 = result["dimensions"][1]
        assert dim2["name"] == "사이즈"
        assert set(dim2["values"]) == {"M", "S"}

        # Combinations
        assert len(result["combinations"]) == 4
        assert {"색상": "블랙", "사이즈": "S"} in result["combinations"]

    def test_parse_2d_combination_with_slash(self, mapper):
        """2차원 조합 옵션 (separator='/')."""
        raw_options = ["레드/L", "블루/XL"]

        result = mapper.parse(raw_options)

        assert result["type"] == "COMBINATION"
        assert result["separator"] == "/"
        assert len(result["dimensions"]) == 2

    # ===== 3D Options (Combination) =====

    def test_parse_3d_combination(self, mapper):
        """3차원 조합 옵션 (색상-사이즈-재질)."""
        raw_options = ["블랙-S-면", "블랙-M-면", "블랙-M-폴리", "화이트-S-면"]

        result = mapper.parse(raw_options)

        assert result["type"] == "COMBINATION"
        assert len(result["dimensions"]) == 3
        assert result["dimensions"][0]["name"] == "색상"
        assert result["dimensions"][1]["name"] == "사이즈"
        assert result["dimensions"][2]["name"] == "재질"

    # ===== Edge Cases =====

    def test_empty_options_returns_empty_result(self, mapper):
        """빈 옵션 리스트."""
        result = mapper.parse([])

        assert result["type"] == "EMPTY"
        assert result["dimensions"] == []

    def test_options_with_whitespace(self, mapper):
        """공백 포함 옵션."""
        raw_options = [" 블랙 - S ", " 화이트 - M "]

        result = mapper.parse(raw_options)

        # 공백 제거 후 파싱
        assert result["type"] == "COMBINATION"
        dim1_values = result["dimensions"][0]["values"]
        dim2_values = result["dimensions"][1]["values"]
        assert "블랙" in dim1_values
        assert "화이트" in dim1_values
        assert "S" in dim2_values
        assert "M" in dim2_values

    def test_options_with_special_characters(self, mapper):
        """특수문자 포함 옵션."""
        raw_options = ["블랙(무광)-S", "화이트(광택)-M"]

        result = mapper.parse(raw_options)

        assert result["type"] == "COMBINATION"
        assert "블랙(무광)" in result["dimensions"][0]["values"]

    def test_inconsistent_separator_raises_error(self, mapper):
        """일관성 없는 separator."""
        raw_options = ["블랙-S", "화이트/M"]  # Mixed separators

        with pytest.raises(ValueError, match="Inconsistent separator"):
            mapper.parse(raw_options)

    # ===== Naver Format Conversion =====

    def test_to_naver_format_simple(self, mapper):
        """네이버 API 형식 변환 (Simple)."""
        raw_options = ["블랙", "화이트"]
        parsed = mapper.parse(raw_options)

        naver_format = mapper.to_naver_format(parsed)

        assert naver_format["optionType"] == "SIMPLE"
        assert len(naver_format["optionCombinations"]) == 2
        assert naver_format["optionCombinations"][0]["optionName1"] == "색상"
        assert naver_format["optionCombinations"][0]["optionValue1"] == "블랙"
        assert naver_format["optionCombinations"][0]["stockQuantity"] == 0
        assert naver_format["optionCombinations"][0]["price"] == 0

    def test_to_naver_format_2d(self, mapper):
        """네이버 API 형식 변환 (2D Combination)."""
        raw_options = ["블랙-S", "화이트-M"]
        parsed = mapper.parse(raw_options)

        naver_format = mapper.to_naver_format(parsed)

        assert naver_format["optionType"] == "COMBINATION"
        assert len(naver_format["optionCombinations"]) == 2

        combo1 = naver_format["optionCombinations"][0]
        assert combo1["optionName1"] == "색상"
        assert combo1["optionValue1"] in ["블랙", "화이트"]
        assert combo1["optionName2"] == "사이즈"
        assert combo1["optionValue2"] in ["S", "M"]
        assert combo1["stockQuantity"] == 0
        assert combo1["price"] == 0

    def test_to_naver_format_3d(self, mapper):
        """네이버 API 형식 변환 (3D Combination)."""
        raw_options = ["블랙-S-면"]
        parsed = mapper.parse(raw_options)

        naver_format = mapper.to_naver_format(parsed)

        assert naver_format["optionType"] == "COMBINATION"
        combo = naver_format["optionCombinations"][0]
        assert "optionName1" in combo
        assert "optionValue1" in combo
        assert "optionName2" in combo
        assert "optionValue2" in combo
        assert "optionName3" in combo
        assert "optionValue3" in combo

    def test_to_naver_format_empty(self, mapper):
        """네이버 API 형식 변환 (Empty)."""
        parsed = mapper.parse([])

        naver_format = mapper.to_naver_format(parsed)

        assert naver_format["optionType"] == "SIMPLE"
        assert naver_format["optionCombinations"] == []

    # ===== Dimension Name Inference =====

    def test_infer_dimension_name_color(self, mapper):
        """색상 인식."""
        values = ["블랙", "화이트", "레드"]
        name = mapper._infer_dimension_name(values)
        assert name == "색상"

    def test_infer_dimension_name_size(self, mapper):
        """사이즈 인식."""
        values = ["S", "M", "L", "XL"]
        name = mapper._infer_dimension_name(values)
        assert name == "사이즈"

    def test_infer_dimension_name_default(self, mapper):
        """알 수 없는 옵션."""
        values = ["옵션A", "옵션B"]
        name = mapper._infer_dimension_name(values)
        assert name == "옵션"

    def test_separator_detection(self, mapper):
        """Separator 자동 감지."""
        # Dash
        assert mapper._detect_separator(["블랙-S"]) == "-"

        # Slash
        assert mapper._detect_separator(["블랙/S"]) == "/"

        # Underscore
        assert mapper._detect_separator(["블랙_S"]) == "_"

        # Space
        assert mapper._detect_separator(["블랙 S"]) == " "

        # None
        assert mapper._detect_separator(["블랙"]) is None
