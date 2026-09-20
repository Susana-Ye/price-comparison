from typing import Literal
from pydantic import BaseModel, Field


class TicketInfo(BaseModel):
    store_name: str | None = Field(
        description="Canonical store name, for example Albert Heijn."
    )

    store_branch: str | None = Field(
        description="Store branch or location if visible on the receipt."
    )

    date: str | None = Field(
        description="Purchase date in YYYY-MM-DD format."
    )

    currency: str | None = Field(
        description="ISO currency code, for example EUR."
    )

    gross_total: float | None = Field(
        description="Receipt total before discounts, if explicitly visible."
    )

    discount_total: float | None = Field(
        description="Total discounts as a positive number."
    )

    total_paid: float | None = Field(
        description="Final amount paid."
    )

    payment_method: str | None = Field(
        description="Payment method if explicitly visible."
    )

class NewProductDetails(BaseModel):
    normalized_name: str = Field(
        description="Human-readable canonical product name in English."
    )

    brand: str | None = Field(
        description="Brand if visible or reliably inferable."
    )

    category: str | None = Field(
        description="Suggested product category in English."
    )

    subcategory: str | None = Field(
        description="Suggested product subcategory in English."
    )

    comparison_unit: Literal[
        "kg",
        "L",
        "unit",
    ] | None = Field(
        description="Suggested standard comparison unit for this product."
    )

class ProductLine(BaseModel):
    line_index: int = Field(
        description="1-based index of the product line."
    )

    receipt_name: str = Field(
        description="Product text exactly as printed on the receipt."
    )

    product_id: str | None = Field(
        description="Existing Product ID from KNOWN_PRODUCTS. Never invent one."
    )

    quantity_original: str | None = Field(
        description="Quantity representation visible on the receipt."
    )

    quantity_value: float | None = Field(
        description="Numeric quantity only if directly extractable from the receipt."
    )

    quantity_unit: Literal[
        "kg",
        "g",
        "L",
        "ml",
        "unit",
        "pack",
        "unknown",
    ] | None

    gross_price: float | None = Field(
        description="Product line price before an attributable product discount."
    )

    discount_amount: float | None = Field(
        description="Discount associated with this product, as a positive number."
    )

    printed_unit_price: float | None = Field(
        description="Unit price explicitly printed on the receipt. Do not calculate it."
    )

    printed_unit: Literal[
        "kg",
        "L",
        "unit",
    ] | None

    match_method: Literal[
        "alias",
        "exact_name",
        "semantic_match",
        "new_product",
        "unresolved",
    ]

    confidence: float = Field(
        ge=0,
        le=1,
        description="Confidence score between 0 and 1."
    )

    status: Literal[
        "ok",
        "review",
        "new_product",
    ]

    review_reason: str | None = Field(
        description="Reason why human review is required, otherwise null."
    )

    new_product_details: NewProductDetails | None = Field(
        description=(
            "Only populate this field when status is 'new_product'. "
            "Otherwise it must be null."
        )
    )


class UnassignedDiscount(BaseModel):
    receipt_text: str = Field(
        description="Discount text exactly as printed on the receipt."
    )

    amount: float | None = Field(
        description="Discount amount as a positive number."
    )

    confidence: float = Field(
        ge=0,
        le=1
    )

    notes: str | None


class ReceiptExtraction(BaseModel):
    schema_version: str = Field(
        description="Version of the extraction schema, for example 1.0."
    )

    ticket: TicketInfo

    products: list[ProductLine]

    unassigned_discounts: list[UnassignedDiscount]

    warnings: list[str]