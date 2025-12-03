"""Product validator."""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.validators.forbidden_word_validator import ForbiddenWordValidator, ValidationResult


@dataclass
class ProductValidationResult:
    """Product validation result."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]


class ProductValidator:
    """
    Validate product data before registration.

    Validates:
    - Required fields
    - Price constraints
    - Image requirements
    - Forbidden words
    - Category mapping
    """

    def __init__(self, forbidden_word_validator: Optional[ForbiddenWordValidator] = None) -> None:
        """
        Initialize validator.

        Args:
            forbidden_word_validator: Forbidden word validator (default: create new)
        """
        self.forbidden_word_validator = forbidden_word_validator or ForbiddenWordValidator()

    def validate(self, product_data: Dict[str, Any]) -> ProductValidationResult:
        """
        Validate product data.

        Args:
            product_data: Product data dict
                {
                    "name": str,
                    "price": int,
                    "description": str,
                    "images": List[str],
                    "category": str,
                    "options": List[str]
                }

        Returns:
            ProductValidationResult with errors and warnings
        """
        errors: List[str] = []
        warnings: List[str] = []

        # Required fields
        required_fields = ["name", "price", "description"]
        for field in required_fields:
            if field not in product_data or not product_data[field]:
                errors.append(f"Required field missing: '{field}'")

        # Validate name
        name = product_data.get("name", "")
        if len(name) > 500:
            errors.append(f"Product name too long: {len(name)} chars (max: 500)")
        if len(name) < 2:
            errors.append(f"Product name too short: {len(name)} chars (min: 2)")

        # Validate price
        price = product_data.get("price")
        if price is not None:
            if not isinstance(price, int):
                errors.append(f"Price must be integer: {type(price)}")
            elif price < 0:
                errors.append(f"Price must be non-negative: {price}")
            elif price == 0:
                warnings.append("Price is 0 - may be rejected by Naver")

        # Validate images
        images = product_data.get("images", [])
        if not images:
            warnings.append("No images provided - product may be rejected")
        elif len(images) > 20:
            warnings.append(f"Too many images: {len(images)} (recommended: max 10)")

        # Validate forbidden words
        description = product_data.get("description", "")
        forbidden_result = self.forbidden_word_validator.validate_product(name, description)
        if not forbidden_result.is_valid:
            errors.extend(forbidden_result.errors)

        # Validate category
        category = product_data.get("category")
        if not category:
            errors.append("Category is required")

        is_valid = len(errors) == 0
        return ProductValidationResult(is_valid=is_valid, errors=errors, warnings=warnings)

    def validate_options(self, options: List[str]) -> ValidationResult:
        """
        Validate product options.

        Args:
            options: Option strings

        Returns:
            ValidationResult
        """
        errors = []

        if not options:
            return ValidationResult(is_valid=True, errors=[])

        if len(options) > 100:
            errors.append(f"Too many options: {len(options)} (max: 100)")

        for opt in options:
            if len(opt) > 100:
                errors.append(f"Option too long: '{opt}' ({len(opt)} chars, max: 100)")

        is_valid = len(errors) == 0
        return ValidationResult(is_valid=is_valid, errors=errors)
