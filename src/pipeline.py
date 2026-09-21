import json
from pathlib import Path

from src.excel_reader import load_aliases, load_products
from src.gemini_service import analyse_receipt
from src.receipt_schema import ReceiptExtraction


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
        ) # Save the Pydantic model given by Gemini as JSON


def run_pipeline(
    receipt_path: str | Path, 
    excel_path: str | Path,
    output_path: str | Path, # Path to files as parameter, allows for reusability and testing with different files
) -> ReceiptExtraction:
    """
    Run the first safe receipt-processing pipeline.

    This version:
    - reads the product catalogue;
    - reads confirmed product aliases;
    - sends the receipt and catalogue context to Gemini;
    - validates the structured output with Pydantic;
    - saves the validated result as JSON.

    It does not modify the Excel workbook.
    """

    print("Step 1/4 - Loading products...")

    products = load_products(excel_path)

    print(f"Loaded {len(products)} products.")


    print("Step 2/4 - Loading product aliases...")

    aliases = load_aliases(excel_path)

    print(f"Loaded {len(aliases)} aliases.")


    print("Step 3/4 - Analysing receipt with Gemini...")

    result = analyse_receipt(
        receipt_path=receipt_path,
        products=products,
        aliases=aliases,
    )
    
    print("Gemini response validated successfully.")


    print("Step 4/4 - Saving validated JSON...")

    save_receipt_result(
        result=result,
        output_path=output_path,
    )

    print(f"Saved result to: {output_path}")

    return result