"""Forbidden word validator."""

import re
from dataclasses import dataclass
from typing import List


@dataclass
class ValidationResult:
    """Validation result."""

    is_valid: bool
    errors: List[str]


class ForbiddenWordValidator:
    """
    Validate text for forbidden words.

    Naver Smart Store has strict policies on product descriptions.
    Common forbidden words include:
    - Medical claims: "병 치료", "질병 완치"
    - Absolute claims: "100% 효과", "무조건"
    - Misleading: "의약품", "처방전"
    """

    DEFAULT_FORBIDDEN_WORDS = [
        "병 치료",
        "질병 완치",
        "의약품",
        "처방전",
        "100% 효과",
        "무조건",
        "반드시 효과",
        "완치",
        "치료제",
    ]

    def __init__(self, forbidden_words: List[str] = None) -> None:
        """
        Initialize validator.

        Args:
            forbidden_words: List of forbidden words (default: use DEFAULT_FORBIDDEN_WORDS)
        """
        self.forbidden_words = forbidden_words or self.DEFAULT_FORBIDDEN_WORDS

    def validate(self, text: str) -> ValidationResult:
        """
        Validate text for forbidden words.

        Args:
            text: Text to validate

        Returns:
            ValidationResult with is_valid flag and error list
        """
        if not text:
            return ValidationResult(is_valid=True, errors=[])

        errors = []

        for word in self.forbidden_words:
            # Case-insensitive search
            if re.search(re.escape(word), text, re.IGNORECASE):
                errors.append(f"Forbidden word detected: '{word}'")

        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors)

    def validate_product(self, name: str, description: str) -> ValidationResult:
        """
        Validate both product name and description.

        Args:
            name: Product name
            description: Product description

        Returns:
            ValidationResult with combined errors
        """
        name_result = self.validate(name)
        desc_result = self.validate(description)

        all_errors = name_result.errors + desc_result.errors
        is_valid = len(all_errors) == 0

        return ValidationResult(is_valid=is_valid, errors=all_errors)
