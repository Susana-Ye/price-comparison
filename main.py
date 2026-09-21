from src.config import (
    EXCEL_PATH,
    RECEIPT_PATH,
    OUTPUT_JSON_PATH,
)

from src.pipeline import run_pipeline


def main() -> None:
    """
    Run the receipt-processing pipeline using the configured project paths.
    """

    result = run_pipeline(
        receipt_path=RECEIPT_PATH,
        excel_path=EXCEL_PATH,
        output_path=OUTPUT_JSON_PATH,
    )

    print()
    print("Pipeline completed successfully.")
    print()

    print("Receipt summary:")
    print(f"Store: {result.ticket.store_name}")
    print(f"Date: {result.ticket.date}")
    print(f"Total paid: {result.ticket.total_paid}")
    print(f"Products detected: {len(result.products)}")

    review_count = sum(1 for product in result.products
        if product.status == "review"
    )

    new_product_count = sum(1 for product in result.products
        if product.status == "new_product"
    )

    print(f"Products requiring review: {review_count}")
    print(f"New products detected: {new_product_count}")

    if result.warnings:
        print()
        print("Warnings:")

        for warning in result.warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()