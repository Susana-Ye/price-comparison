import json
from pathlib import Path

from src.receipt_schema import ReceiptExtraction


def load_mock_receipt(json_path: Path) -> ReceiptExtraction:
    with json_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return ReceiptExtraction.model_validate(data)