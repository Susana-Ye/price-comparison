import json
from pathlib import Path
from typing import Any

from src.excel_reader import (
    load_aliases,
    load_products,
    build_alias_index,
    build_product_index,
)
from src.gemini_service import analyse_receipt
from src.receipt_schema import ReceiptExtraction
from src.config import USE_GEMINI, MOCK_RECEIPT_JSON_PATH
from src.mock_service import load_mock_receipt

from src.review_handler import process_receipt_result
from src.id_generator import (
    generate_next_receipt_id,
    generate_record_ids,
    generate_review_ids,
)
from src.excel_writer import write_processed_receipt


def save_receipt_result(
    result: ReceiptExtraction,
    output_path: str | Path,
) -> None: 
    """
    Save a validated receipt extraction result as formatted JSON in the specified output path.
    """

    output_path = Path(output_path)

    output_path.parent.mkdir(parents=True, exist_ok=True) # Create the output directory if it doesn't exist

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(
            result.model_dump(),
            file,
            ensure_ascii=False,
            indent=2,
        ) # Save the Pydantic model given by Gemini as JSON in output_path


def run_pipeline(
    receipt_path: str | Path, 
    excel_path: str | Path,
    output_path: str | Path, # Path to files as parameter, allows for reusability and testing with different files
    output_excel_path: str | Path,
) -> dict[str, Any]:
    """
    Run the receipt-processing pipeline.

    This version:
    - reads the product catalogue;
    - reads confirmed product aliases;
    - analyses the receipt using Gemini or mock data;
    - validates the structured output with Pydantic;
    - saves the validated result as JSON;
    - builds deterministic lookup indexes;
    - processes accepted products and review items;
    - generates internal IDs;
    - writes the processed result to a new Excel workbook.

    The source Excel workbook is not modified.
    """

    print("Step 1/8 - Loading products...")

    products = load_products(excel_path)

    print(f"Loaded {len(products)} products.")
    print()

    print("Step 2/8 - Loading product aliases...")

    aliases = load_aliases(excel_path)

    print(f"Loaded {len(aliases)} aliases.")
    print()

    if USE_GEMINI:
        print("Step 3/8 - Analysing receipt with Gemini...")

        result = analyse_receipt(receipt_path, products, aliases)

        print("Gemini response validated successfully.")
        
    else:
        print("Step 3/8 - Loading mock receipt...")

        result = load_mock_receipt(MOCK_RECEIPT_JSON_PATH)

        print("Mock receipt loaded successfully.")

    print()

    print("Step 4/8 - Saving validated JSON...")

    save_receipt_result(result=result, output_path=output_path)

    print(f"Saved result to: {output_path}")
    print()

    print("Step 5/8 - Building lookup indexes...")

    product_index = build_product_index(products)

    print(f"Built product index with {len(product_index)} entries.")

    alias_index = build_alias_index(aliases)    

    print(f"Built alias index with {len(alias_index)} entries.")
    print()

    print("Step 6/8 - Processing products and review items...")

    processed = process_receipt_result(
        result=result,
        product_index=product_index,
        alias_index=alias_index,
    )

    accepted_products = processed["accepted_products"]

    review_items = processed["review_items"]

    print(f"Accepted products: {len(accepted_products)}")

    print(f"Review items: {len(review_items)}")
    print()

    print("Step 7/8 - Generating internal IDs...")

    receipt_id = generate_next_receipt_id(excel_path)

    print(f"Generated Receipt ID: {receipt_id}")

    record_ids = generate_record_ids(
        excel_path=excel_path,
        count=len(accepted_products),
    )

    print(f"Generated {len(record_ids)} Record IDs.")

    review_ids = generate_review_ids(
        excel_path=excel_path,
        count=len(review_items),
    )

    print(f"Generated {len(review_ids)} Review IDs.")
    print()

    print("Step 8/8 - Writing updated Excel workbook...")

    write_processed_receipt(
        source_excel_path=excel_path,
        output_excel_path=output_excel_path,
        result=result,
        accepted_products=accepted_products,
        review_items=review_items,
        receipt_id=receipt_id,
        record_ids=record_ids,
        review_ids=review_ids,
    )

    print(f"Saved updated workbook to: {output_excel_path}")
    print()

    return { # Return a dictionary with all relevant information other than result for further processing 
        "result": result,
        "receipt_id": receipt_id,
        "accepted_products": accepted_products,
        "review_items": review_items,
        "record_ids": record_ids,
        "review_ids": review_ids,
        "warnings": processed["warnings"],
        "output_json_path": Path(
            output_path
        ),
        "output_excel_path": Path(
            output_excel_path
        ),
    }