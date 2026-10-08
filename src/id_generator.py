import re
from pathlib import Path

from openpyxl import load_workbook


PRODUCTS_SHEET = "Products"
PRICE_HISTORY_SHEET = "Price_History"
RECEIPTS_SHEET = "Receipts"
REVIEW_SHEET = "Review"


PRODUCT_ID_HEADER = "Product ID"
RECORD_ID_HEADER = "Record ID"
RECEIPT_ID_HEADER = "Receipt ID"
REVIEW_ID_HEADER = "Review ID"


PRODUCT_ID_PREFIX = "P"
RECORD_ID_PREFIX = "R"
RECEIPT_ID_PREFIX = "T"
REVIEW_ID_PREFIX = "REV"


PRODUCT_ID_WIDTH = 4
RECORD_ID_WIDTH = 5
RECEIPT_ID_WIDTH = 4
REVIEW_ID_WIDTH = 4


def _find_column_index(worksheet, header_name: str) -> int:
    """
    Find the Excel column index for a given header.
    """

    for cell in worksheet[1]:
        if cell.value is None:
            continue

        if str(cell.value).strip() == header_name:
            return cell.column # Return the column index (1-based) for the matching header

    raise ValueError(
        f"Header '{header_name}' was not found in sheet '{worksheet.title}'."
    )


def _load_existing_ids(
    excel_path: str | Path,
    sheet_name: str,
    header_name: str,
) -> list[str]:
    """
    Load all non-empty IDs from a specific Excel column.
    """

    workbook = load_workbook(filename=excel_path, data_only=True, read_only=True)

    try:
        if sheet_name not in workbook.sheetnames:
            raise ValueError(f"Workbook does not contain the '{sheet_name}' sheet.")

        worksheet = workbook[sheet_name]

        column_index = _find_column_index(worksheet=worksheet, header_name=header_name)

        existing_ids = []

        for row in worksheet.iter_rows(min_row=2, values_only=True):
            value = row[column_index - 1] # Get the value from the specified column index (adjusted for 0-based indexing, for the header row)

            if value is None:
                continue

            existing_ids.append(str(value).strip())

        return existing_ids

    finally:
        workbook.close()


def _extract_id_number(value: str, prefix: str) -> int:
    """
    Extract the numeric part of an internal application ID.
    """

    pattern = rf"^{re.escape(prefix)}(\d+)$" # Regular expression pattern to match the prefix followed by digits

    match = re.fullmatch(pattern, value)

    if match is None:
        raise ValueError(
            f"Invalid ID format: '{value}'. "
            f"Expected prefix '{prefix}' followed by digits."
        )

    return int(match.group(1))


def generate_next_id(existing_ids: list[str], prefix: str, width: int) -> str:
    """
    Generate the next ID after the highest existing numeric ID.
    """

    if not existing_ids:
        next_number = 1

    else:
        numbers = [
            _extract_id_number(value=existing_id, prefix=prefix)
            for existing_id in existing_ids
        ]

        next_number = max(numbers) + 1

    return f"{prefix}{next_number:0{width}d}" # Format the next number with leading zeros to match the specified width


def generate_id_batch(existing_ids: list[str], prefix: str, width: int, count: int) -> list[str]:
    """
    Generate multiple sequential IDs without modifying Excel.
    Returns a list of new IDs starting from the next available number (use generate_next_id to get the first one).
    """

    if count < 0:
        raise ValueError("ID batch count cannot be negative.")

    if count == 0:
        return []

    first_id = generate_next_id(existing_ids=existing_ids,
        prefix=prefix, width=width)

    first_number = _extract_id_number(value=first_id, prefix=prefix)

    return [
        f"{prefix}{number:0{width}d}"
        for number in range(first_number, first_number + count)
    ]


def generate_next_receipt_id(excel_path: str | Path) -> str:
    """
    Generate the next Receipt ID.
    """

    existing_ids = _load_existing_ids(
        excel_path=excel_path,
        sheet_name=RECEIPTS_SHEET,
        header_name=RECEIPT_ID_HEADER,
    )

    return generate_next_id(
        existing_ids=existing_ids,
        prefix=RECEIPT_ID_PREFIX,
        width=RECEIPT_ID_WIDTH,
    )


def generate_record_ids(
    excel_path: str | Path,
    count: int,
) -> list[str]:
    """
    Generate Record IDs for Price_History rows.
    """

    existing_ids = _load_existing_ids(
        excel_path=excel_path,
        sheet_name=PRICE_HISTORY_SHEET,
        header_name=RECORD_ID_HEADER,
    )

    return generate_id_batch(
        existing_ids=existing_ids,
        prefix=RECORD_ID_PREFIX,
        width=RECORD_ID_WIDTH,
        count=count,
    )


def generate_review_ids(
    excel_path: str | Path,
    count: int,
) -> list[str]:
    """
    Generate Review IDs for Review rows.
    """

    existing_ids = _load_existing_ids(
        excel_path=excel_path,
        sheet_name=REVIEW_SHEET,
        header_name=REVIEW_ID_HEADER,
    )

    return generate_id_batch(
        existing_ids=existing_ids,
        prefix=REVIEW_ID_PREFIX,
        width=REVIEW_ID_WIDTH,
        count=count,
    )


def generate_next_product_id(
    excel_path: str | Path,
) -> str:
    """
    Generate the next Product ID.

    This function is intended for the future new-product approval workflow.
    """

    existing_ids = _load_existing_ids(
        excel_path=excel_path,
        sheet_name=PRODUCTS_SHEET,
        header_name=PRODUCT_ID_HEADER,
    )

    return generate_next_id(
        existing_ids=existing_ids,
        prefix=PRODUCT_ID_PREFIX,
        width=PRODUCT_ID_WIDTH,
    )