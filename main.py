from src.config import (
    EXCEL_PATH,
    RECEIPT_PATH,
    OUTPUT_JSON_PATH,
    OUTPUT_EXCEL_PATH,
)

from src.pipeline import run_pipeline


def main() -> None:
    """
    Run the receipt-processing pipeline using the configured project paths.
    """

    pipeline_result = run_pipeline(
        receipt_path=RECEIPT_PATH,
        excel_path=EXCEL_PATH,
        output_path=OUTPUT_JSON_PATH,
        output_excel_path=OUTPUT_EXCEL_PATH,
    )

    result = pipeline_result["result"]

    print()
    print("Pipeline completed successfully.")
    print()

    print("Receipt summary:")
    print(f"Receipt ID: {pipeline_result['receipt_id']}")
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

    print()
    print("Processing summary:")
    print(f"Accepted products: {len(pipeline_result['accepted_products'])}")
    print(f"Review items created: {len(pipeline_result['review_items'])}")
    print(f"Price records created: {len(pipeline_result['record_ids'])}")

    if result.warnings:
        print()
        print("Warnings:")

        for warning in result.warnings:
            print(f"- {warning}")

    print()
    print(f"JSON output: {pipeline_result['output_json_path']}")
    print(f"Excel output: {pipeline_result['output_excel_path']}")


if __name__ == "__main__":
    main()