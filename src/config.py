from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# This environment variable allows to switch between test data and production data without changing the code.
USE_TEST_DATA = os.getenv("USE_TEST_DATA", "false").lower() == "true"
if USE_TEST_DATA:
    EXCEL_PATH = BASE_DIR / "data" / "price_comparison_test_data.xlsx"
else:
    EXCEL_PATH = BASE_DIR / "data" / "price_comparison_structure.xlsx"

RECEIPT_PATH = BASE_DIR / "receipts" / "ticket.jpg"

OUTPUT_DIR = BASE_DIR / "output"

OUTPUT_JSON_PATH = OUTPUT_DIR / "ticket.json"

GEMINI_MODEL = "gemini-3.8-flash"

# Special configuration for testing and development purposes. 
# When set to False, the application won't call the Gemini API and will use a mock receipt JSON file. 
# This allows developers to test the pipeline without incurring API costs or waiting for network responses.
USE_GEMINI = False
MOCK_RECEIPT_JSON_PATH = BASE_DIR / "data" / "mock_receipt.json"