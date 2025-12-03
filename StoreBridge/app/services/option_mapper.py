"""Option mapper for converting Domeggook options to Naver format."""

from typing import Any, Dict, List, Optional


class OptionMapper:
    """
    Parse and convert Domeggook product options to Naver Commerce API format.

    Handles:
    - 1D options (simple): ["블랙", "화이트", "네이비"]
    - 2D options (combination): ["블랙-S", "블랙-M", "화이트-S"]
    - 3D options (combination): ["블랙-S-면", "화이트-M-폴리"]
    """

    SEPARATORS = ["-", "/", "_", " ", ":"]

    def parse(self, raw_options: List[str]) -> Dict[str, Any]:
        """
        Parse raw option strings from Domeggook.

        Args:
            raw_options: Raw option strings (e.g., ["블랙-S", "화이트-M"])

        Returns:
            Parsed option structure:
            {
                "type": "SIMPLE" | "COMBINATION" | "EMPTY",
                "separator": str | None,
                "dimensions": [...],
                "combinations": [...]
            }

        Raises:
            ValueError: If options have inconsistent separators
        """
        if not raw_options:
            return {"type": "EMPTY", "separator": None, "dimensions": [], "combinations": []}

        # Strip whitespace
        raw_options = [opt.strip() for opt in raw_options]

        # Detect separator
        separator = self._detect_separator(raw_options)

        if separator is None:
            # Simple 1D options
            return self._parse_simple(raw_options)
        else:
            # Combination 2D/3D options
            split_options = [opt.split(separator) for opt in raw_options]
            # Strip whitespace from each part
            split_options = [[part.strip() for part in opt] for opt in split_options]
            return self._parse_combination(split_options, separator)

    def _detect_separator(self, raw_options: List[str]) -> Optional[str]:
        """
        Detect separator used in options.

        Args:
            raw_options: Raw option strings

        Returns:
            Detected separator or None if no separator found

        Raises:
            ValueError: If multiple separators are used inconsistently
        """
        detected_separator = None
        found_separators = []

        for sep in self.SEPARATORS:
            # Skip space separator initially to check for actual separators first
            if sep == " ":
                continue

            if any(sep in opt for opt in raw_options):
                found_separators.append(sep)
                # Check if all options use this separator consistently
                uses_sep = [sep in opt for opt in raw_options]
                if all(uses_sep):
                    detected_separator = sep
                    break

        # Check for inconsistent separators (some options use one, some use another)
        if len(found_separators) > 1:
            raise ValueError(
                f"Inconsistent separator: both '{found_separators[0]}' and '{found_separators[1]}'"
            )

        # If no separator found and contains space, check if space is actual separator
        if detected_separator is None:
            # Check for space separator (but only if consistent)
            if any(" " in opt for opt in raw_options):
                uses_space = [" " in opt for opt in raw_options]
                if all(uses_space):
                    detected_separator = " "

        return detected_separator

    def _parse_simple(self, raw_options: List[str]) -> Dict[str, Any]:
        """
        Parse simple 1D options.

        Args:
            raw_options: Simple option strings (e.g., ["블랙", "화이트"])

        Returns:
            {
                "type": "SIMPLE",
                "dimension_name": "색상",
                "values": ["블랙", "화이트"]
            }
        """
        # Infer dimension name (default to "옵션")
        dimension_name = self._infer_dimension_name(raw_options)

        return {
            "type": "SIMPLE",
            "separator": None,
            "dimension_name": dimension_name,
            "values": raw_options,
            "dimensions": [{"name": dimension_name, "values": raw_options}],
            "combinations": [
                {dimension_name: value} for value in raw_options
            ],  # For compatibility
        }

    def _parse_combination(
        self, split_options: List[List[str]], separator: str
    ) -> Dict[str, Any]:
        """
        Parse combination 2D/3D options.

        Args:
            split_options: Split option parts (e.g., [["블랙", "S"], ["화이트", "M"]])
            separator: Detected separator

        Returns:
            {
                "type": "COMBINATION",
                "separator": "-",
                "dimensions": [
                    {"name": "색상", "values": ["블랙", "화이트"]},
                    {"name": "사이즈", "values": ["S", "M"]}
                ],
                "combinations": [
                    {"색상": "블랙", "사이즈": "S"},
                    {"색상": "화이트", "사이즈": "M"}
                ]
            }
        """
        if not split_options:
            return {"type": "EMPTY", "separator": None, "dimensions": [], "combinations": []}

        # Get number of dimensions
        num_dimensions = len(split_options[0])

        # Extract unique values per dimension
        dimensions = []
        for dim_idx in range(num_dimensions):
            values = list(set(opt[dim_idx] for opt in split_options if len(opt) > dim_idx))
            dimension_name = self._infer_dimension_name_from_values(values, dim_idx)
            dimensions.append({"name": dimension_name, "values": sorted(values)})

        # Build combinations
        combinations = []
        for opt_parts in split_options:
            if len(opt_parts) == num_dimensions:
                combo = {dimensions[i]["name"]: opt_parts[i] for i in range(num_dimensions)}
                combinations.append(combo)

        return {
            "type": "COMBINATION",
            "separator": separator,
            "dimensions": dimensions,
            "combinations": combinations,
        }

    def _infer_dimension_name(self, values: List[str]) -> str:
        """
        Infer dimension name from values.

        Args:
            values: Option values

        Returns:
            Inferred dimension name (e.g., "색상", "사이즈")
        """
        # Simple heuristics
        size_keywords = ["S", "M", "L", "XL", "XXL", "FREE"]
        color_keywords = ["블랙", "화이트", "레드", "블루", "그린", "옐로우", "네이비"]

        has_size = any(v.upper() in size_keywords for v in values)
        has_color = any(v in color_keywords for v in values)

        if has_size:
            return "사이즈"
        elif has_color:
            return "색상"
        else:
            return "옵션"

    def _infer_dimension_name_from_values(self, values: List[str], dim_idx: int) -> str:
        """
        Infer dimension name from values and index.

        Args:
            values: Unique values for this dimension
            dim_idx: Dimension index (0, 1, 2, ...)

        Returns:
            Inferred dimension name
        """
        # Try to infer from values
        size_keywords = ["S", "M", "L", "XL", "XXL", "FREE", "24", "26", "28", "30"]
        color_keywords = ["블랙", "화이트", "레드", "블루", "그린", "옐로우", "네이비", "그레이"]
        material_keywords = ["면", "폴리", "나일론", "레이온", "울", "캐시미어"]

        has_size = any(any(k in v.upper() for k in size_keywords) for v in values)
        has_color = any(any(k in v for k in color_keywords) for v in values)
        has_material = any(any(k in v for k in material_keywords) for v in values)

        if has_color:
            return "색상"
        elif has_size:
            return "사이즈"
        elif has_material:
            return "재질"
        else:
            # Default names by index
            default_names = ["옵션1", "옵션2", "옵션3"]
            return default_names[dim_idx] if dim_idx < len(default_names) else f"옵션{dim_idx+1}"

    def to_naver_format(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert parsed options to Naver Commerce API format.

        Args:
            parsed: Parsed option structure from parse()

        Returns:
            Naver-formatted options:
            {
                "optionType": "SIMPLE" | "COMBINATION",
                "optionCombinations": [
                    {
                        "optionName1": "색상",
                        "optionValue1": "블랙",
                        "optionName2": "사이즈",
                        "optionValue2": "S",
                        "stockQuantity": 0,
                        "price": 0
                    }
                ]
            }
        """
        if parsed["type"] == "EMPTY":
            return {"optionType": "SIMPLE", "optionCombinations": []}

        combinations = []
        for combo in parsed["combinations"]:
            naver_combo = {"stockQuantity": 0, "price": 0}  # Default values

            for idx, (dim_name, value) in enumerate(combo.items(), start=1):
                naver_combo[f"optionName{idx}"] = dim_name
                naver_combo[f"optionValue{idx}"] = value

            combinations.append(naver_combo)

        return {
            "optionType": parsed["type"],
            "optionCombinations": combinations,
        }
