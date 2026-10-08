import json
from typing import Any

from src.calculations import calculate_product_values
from src.excel_reader import find_alias_match, find_product_by_id
from src.receipt_schema import ProductLine, ReceiptExtraction


def _build_review_item(
    original_text: str,
    issue_type: str,
    ai_suggestion: str | None,
    confidence: float,
) -> dict[str, Any]:
    """
    Build an internal review item.

    Review IDs and Receipt IDs will be generated later by the application.
    """

    return {
        "original_text": original_text,
        "issue_type": issue_type,
        "ai_suggestion": ai_suggestion,
        "confidence": confidence,
        "status": "Pending",
        "correction": None,
    }


def _format_new_product_suggestion(
    product_line: ProductLine,
) -> str | None:
    """
    Convert new product details into a readable JSON string.
    """

    if product_line.new_product_details is None:
        return None

    return json.dumps(
        product_line.new_product_details.model_dump(),
        ensure_ascii=False,
        indent=2,
    )


def _validate_existing_product(
    product_line: ProductLine,
    product_index: dict[str, dict[str, Any]],
) -> tuple[dict[str, Any] | None, str | None]:
    """
    Validate that an existing Product ID actually exists in the catalogue.

    Returns:
        (product_metadata, error_message)
    """

    if product_line.product_id is None:
        return None, "Existing product result does not contain a Product ID."

    product = find_product_by_id(product_index=product_index, product_id=product_line.product_id)

    if product is None:
        return (
            None,
            f"Product ID '{product_line.product_id}' does not exist in the active product catalogue.",
        )

    return product, None # Product has been validated and exists in the catalogue.


def _validate_alias_match(
    product_line: ProductLine,
    store_name: str | None,
    alias_index: dict[tuple[str, str], str],
) -> str | None:
    """
    Validate Gemini alias matches against the deterministic alias index.

    Returns an error message when the alias claim cannot be confirmed.
    """

    if product_line.match_method != "alias": 
        return None

    expected_product_id = find_alias_match(
        alias_index=alias_index,
        receipt_text=product_line.receipt_name,
        store=store_name,
    )

    if expected_product_id is None:
        return (
            "Gemini classified the product using an alias match, "
            "but no confirmed alias exists for this receipt text and store."
        )

    if expected_product_id != product_line.product_id:
        return (
            "Gemini alias match conflicts with the confirmed alias mapping. "
            f"Expected '{expected_product_id}', "
            f"received '{product_line.product_id}'."
        )

    return None


def _process_accepted_product(
    product_line: ProductLine,
    product: dict[str, Any],
) -> dict[str, Any]:
    """
    Prepare a safe existing product for later Price_History writing. 
    Make all the deterministic calculations for an accepted product and return a dictionary with all the relevant information.
    """

    calculated_values = calculate_product_values(
        gross_price=product_line.gross_price,
        discount_amount=product_line.discount_amount,
        quantity_value=product_line.quantity_value,
        quantity_unit=product_line.quantity_unit,
        comparison_unit=product["comparison_unit"],
    )

    return {
        "line_index": product_line.line_index,
        "receipt_name": product_line.receipt_name,
        "product_id": product_line.product_id,
        "normalized_name": product["normalized_name"],
        "category": product["category"],
        "subcategory": product["subcategory"],
        "default_brand": product["default_brand"],
        "comparison_unit": product["comparison_unit"],
        "quantity_original": product_line.quantity_original,
        "quantity_value": product_line.quantity_value,
        "quantity_unit": product_line.quantity_unit,
        "gross_price": product_line.gross_price,
        "discount_amount": product_line.discount_amount,
        "price_paid": calculated_values["price_paid"],
        "comparable_quantity": calculated_values["comparable_quantity"],
        "comparable_unit": calculated_values["comparable_unit"],
        "comparable_price": calculated_values["comparable_price"],
        "match_method": product_line.match_method,
        "confidence": product_line.confidence,
    }


def process_receipt_result(
    result: ReceiptExtraction,
    product_index: dict[str, dict[str, Any]],
    alias_index: dict[tuple[str, str], str],
) -> dict[str, Any]:
    """
    Process a validated receipt extraction result.

    Safe existing products are prepared for later Price_History writing.
    Uncertain, inconsistent, or new products are converted into review items.

    This function does not modify the Excel workbook.
    """

    accepted_products = []
    review_items = []

    store_name = result.ticket.store_name

    for product_line in result.products:

        if product_line.status == "new_product": # New products are always sent for review.
            review_items.append(
                _build_review_item(
                    original_text=product_line.receipt_name,
                    issue_type="New product approval",
                    ai_suggestion=_format_new_product_suggestion(product_line),
                    confidence=product_line.confidence,
                )
            )

            continue

        if product_line.status == "review": # Products that require review are sent for review, with Gemini's suggestion if available.
            suggestion = None

            if product_line.product_id is not None: # If Gemini suggested an existing Product ID, we use the product name as the suggestion.
                product = find_product_by_id(
                    product_index=product_index,
                    product_id=product_line.product_id,
                )

                if product is not None:
                    suggestion = (
                        f"{product_line.product_id} - "
                        f"{product['normalized_name']}"
                    )

            if (
                suggestion is None
                and product_line.review_reason is not None
            ): # If there is no product id, we use the review reason provided by Gemini as suggestion.
                suggestion = product_line.review_reason

            review_items.append(
                _build_review_item(
                    original_text=product_line.receipt_name,
                    issue_type="Product match requires review",
                    ai_suggestion=suggestion,
                    confidence=product_line.confidence,
                )
            )

            continue

        if product_line.status != "ok": # Any other status is unexpected and sent for review, with Gemini's suggestion if available.
            review_items.append(
                _build_review_item(
                    original_text=product_line.receipt_name,
                    issue_type="Unexpected product status",
                    ai_suggestion=product_line.status,
                    confidence=product_line.confidence,
                )
            )

            continue

        # If we reach this point, the product line has status "ok" and can be processed further.
        product, product_error = _validate_existing_product( # We validate that the Product ID actually exists in the catalogue.
            product_line=product_line,
            product_index=product_index,
        )

        if product_error is not None:
            review_items.append(
                _build_review_item(
                    original_text=product_line.receipt_name,
                    issue_type="Invalid product reference",
                    ai_suggestion=product_error,
                    confidence=product_line.confidence,
                )
            )

            continue

        # If the product line was matched using an alias, we validate that the alias is consistent with the deterministic alias index.
        alias_error = _validate_alias_match( 
            product_line=product_line,
            store_name=store_name,
            alias_index=alias_index,
        )

        if alias_error is not None: 
            review_items.append(
                _build_review_item(
                    original_text=product_line.receipt_name,
                    issue_type="Alias validation conflict",
                    ai_suggestion=alias_error,
                    confidence=product_line.confidence,
                )
            )

            continue

        # If we reach this point, the product line has been validated and can be accepted for later Price_History writing.
        accepted_product = _process_accepted_product( # We perform all the deterministic calculations for the accepted product.
            product_line=product_line,
            product=product,
        )

        accepted_products.append(accepted_product)

    for discount in result.unassigned_discounts: # Process unassigned discounts, which are always sent for review.
        suggestion = (
            discount.notes if discount.notes
            else (
                f"Unassigned discount amount: {discount.amount}"
            )
        )

        review_items.append(
            _build_review_item(
                original_text=discount.receipt_text,
                issue_type="Unassigned discount",
                ai_suggestion=suggestion,
                confidence=discount.confidence,
            )
        )

    return {
        "accepted_products": accepted_products,
        "review_items": review_items,
        "warnings": result.warnings,
    }