from typing import Literal


ComparisonUnit = Literal[
    "kg",
    "L",
    "unit",
]


def calculate_price_paid(
    gross_price: float | None,
    discount_amount: float | None,
) -> float | None:
    """
    Calculate the final price paid for a product line.
    """

    if gross_price is None:
        return None

    discount = (discount_amount if discount_amount is not None else 0.0)

    price_paid = gross_price - discount

    return round(price_paid, 2)


def normalize_quantity(
    quantity_value: float | None,
    quantity_unit: str | None,
    comparison_unit: ComparisonUnit | None,
) -> tuple[float | None, str | None]:
    """
    Convert an extracted quantity into the product's comparison unit.

    Returns:
        (comparable_quantity, comparable_unit)
    """

    if (
        quantity_value is None
        or quantity_unit is None
        or comparison_unit is None
    ):
        return None, None

    if comparison_unit == "kg":
        if quantity_unit == "kg":
            return quantity_value, "kg"

        if quantity_unit == "g":
            return quantity_value / 1000, "kg"

    if comparison_unit == "L":
        if quantity_unit == "L":
            return quantity_value, "L"

        if quantity_unit == "ml":
            return quantity_value / 1000, "L"

    if comparison_unit == "unit":
        if quantity_unit == "unit":
            return quantity_value, "unit"

    return None, None


def calculate_comparable_price(
    price_paid: float | None,
    comparable_quantity: float | None,
) -> float | None:
    """
    Calculate price per comparison unit.
    """

    if (
        price_paid is None
        or comparable_quantity is None
        or comparable_quantity <= 0
    ):
        return None

    comparable_price = price_paid / comparable_quantity

    return round(comparable_price, 2)


def calculate_product_values(
    gross_price: float | None,
    discount_amount: float | None,
    quantity_value: float | None,
    quantity_unit: str | None,
    comparison_unit: ComparisonUnit | None,
) -> dict:
    """
    Perform all deterministic calculations for one product line.
    """

    price_paid = calculate_price_paid(
        gross_price=gross_price,
        discount_amount=discount_amount,
    )

    comparable_quantity, comparable_unit = (
        normalize_quantity(
            quantity_value=quantity_value,
            quantity_unit=quantity_unit,
            comparison_unit=comparison_unit,
        )
    )

    comparable_price = calculate_comparable_price(
        price_paid=price_paid,
        comparable_quantity=comparable_quantity,
    )

    return {
        "price_paid": price_paid,
        "comparable_quantity": comparable_quantity,
        "comparable_unit": comparable_unit,
        "comparable_price": comparable_price,
    }