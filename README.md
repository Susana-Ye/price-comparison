# AI Price Comparison Agent

An AI-powered receipt processing and price comparison system.

The project analyzes purchase receipts, extracts structured product and pricing data using Google Gemini, normalizes product names, matches receipt items against a known catalogue, and stores the results in an Excel-based price history.

The long-term goal is to build a personal price comparison agent capable of tracking price changes across different stores and identifying where products are cheapest.

## Current Features

- Receipt analysis using Google Gemini API
- Structured JSON output using Pydantic
- Product normalization
- Product matching against known catalogue entries
- Product confidence and review status
- Excel-based product catalogue and price history
- Product alias mapping
- Manual review workflow for uncertain matches
- Price comparison by kg, litre, or unit

## Planned Workflow

```text
Receipt image
      ↓
Google Gemini
      ↓
Structured JSON
      ↓
Python validation
      ↓
Product matching
      ↓
Price calculations
      ↓
Excel data update
      ↓
Price comparison
```

## Project Structure

```text
price-comparison/
│
├── .venv/
│
├── .gitignore
├── README.md
├── requirements.txt
├── test_gemini.py                         
├── main.py
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── receipt_schema.py                   
│   ├── system_prompt.py                    
│   ├── excel_reader.py
│   ├── gemini_service.py
│   └── pipeline.py
│
├── data/
│   ├── mock_receipt.json
│   └── price_comparison_structure.xlsx
│
├── receipts/                              
│
└── output/                                 
```

### Directory Overview

- `main.py`  
  Entry point for running the receipt-processing pipeline.

- `src/config.py`  
  Project configuration, file paths, model settings, and environment variables.

- `src/receipt_schema.py`  
  Pydantic models that define and validate the structured receipt output.

- `src/system_prompt.py`  
  System prompt and AI behaviour rules used when analyzing receipts.

- `src/excel_reader.py`  
  Reads known products and aliases from the Excel file.

- `src/gemini_service.py`  
  Handles communication with the Google Gemini API.

- `src/pipeline.py`  
  Coordinates the full receipt-processing workflow.

- `data/`  
  Local project data, including the Excel price-comparison structure. This directory is ignored by Git.

- `receipts/`  
  Local receipt images used as input. This directory is ignored by Git.

- `output/`  
  Generated JSON files and other local outputs. This directory is ignored by Git.

## Technologies

- Python
- Google Gemini API
- Pydantic
- OpenPyXL
- Excel

## Installation

Clone the repository:

```bash
git clone https://github.com/Susana-Ye/price-comparison.git
cd price-comparison
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## Gemini API Setup

Create a Gemini API key using Google AI Studio.

Set it as an environment variable:

### Windows PowerShell

```powershell
setx GEMINI_API_KEY "YOUR_API_KEY"
```

Restart the terminal after setting the environment variable.

Do not include your API key directly in the source code or upload it to GitHub.

## Test the Gemini Connection

Run:

```bash
python test_gemini.py
```

If the API is configured correctly, Gemini should return a response.

## Mock Receipt Mode

During development, the project can run without making requests to the Gemini API.

This is useful for testing the rest of the pipeline without consuming API quota or depending on external API availability.

The mock mode uses a predefined JSON file that follows the same `ReceiptExtraction` schema expected from Gemini.

### How It Works

The project supports two execution modes:

```text
USE_GEMINI = True
        ↓
Gemini API
        ↓
ReceiptExtraction

USE_GEMINI = False
        ↓
data/mock_receipt.json
        ↓
Pydantic validation
        ↓
ReceiptExtraction
```

Both modes produce the same validated `ReceiptExtraction` object, so the rest of the pipeline can run without changes.

### Configuration

The execution mode is controlled in:

```text
src/config.py
```

To use the real Gemini API:

```python
USE_GEMINI = True
```

To use the mock receipt:

```python
USE_GEMINI = False
```

The mock receipt path is also defined in `config.py`:

```python
MOCK_RECEIPT_JSON_PATH = BASE_DIR / "data" / "mock_receipt.json"
```

### Mock Receipt File

The mock receipt is stored in:

```text
data/mock_receipt.json
```

This file represents a simulated Gemini response and must follow the structure defined in:

```text
src/receipt_schema.py
```

Before being used by the pipeline, the JSON is validated with Pydantic:

```python
ReceiptExtraction.model_validate(data)
```

This ensures that development tests use the same data structure and validation rules as real Gemini responses.

### When to Use Mock Mode

Mock mode is recommended when working on parts of the application that do not require new AI extraction, such as:

* product matching
* price calculations
* unit conversions
* receipt ID generation
* price history creation
* review workflows
* Excel writing
* price comparison logic
* pipeline integration tests

This avoids unnecessary Gemini API calls during development.

### Switching Back to Gemini

When receipt extraction itself needs to be tested, change:

```python
USE_GEMINI = False
```

to:

```python
USE_GEMINI = True
```

The pipeline will then analyze the receipt image using the Gemini API instead of loading the local mock file.

## Data Model

The Excel file stored locally in `data/price_comparison_structure.xlsx` contains the main structured datasets used by the application.

The current workbook is standardized in English.

### Products

Master product catalogue.

Typical fields include:

```text
Product ID
Normalized Product
Category
Subcategory
Default Brand
Comparison Unit
Active
Notes
```

### Price History

Stores individual price observations.

Typical fields include:

```text
Record ID
Receipt ID
Date
Store
Product ID
Receipt / Original Product
Original Quantity
Comparable Quantity
Comparable Unit
Gross Price
Discount
Price Paid
Comparable Price
Notes
```

### Receipts

Stores receipt-level information such as:

```text
Receipt ID
Date
Store
Gross Total
Discounts
Total Paid
Line Count
Payment Method
Notes
```

### Product Aliases

Maps retailer-specific receipt names to known products.

Example:

```text
CHIQUITA LOS → P0006 → Banana
IJSBERGSLA   → P0076 → Iceberg lettuce
```

### Review

Stores products, discounts, or fields that the AI cannot identify confidently.

The system prefers human review instead of guessing uncertain information.

## AI Design Principles

The AI should:

- Never invent product IDs
- Never invent weights, quantities, brands, or discounts
- Preserve the original receipt text
- Normalize product names into English
- Prefer human review when confidence is low
- Only assign discounts when the relationship is clear
- Return structured JSON that follows the defined schema

Python is responsible for:

- JSON validation
- Price calculations
- Unit conversions
- Product ID generation
- Excel reading and writing
- Historical data storage
- Pipeline orchestration


## Roadmap

- [x] Define Excel data structure
- [x] Create product catalogue
- [x] Create price history
- [x] Create receipt table
- [x] Create product alias system
- [x] Create review workflow
- [x] Define structured AI output
- [x] Connect to Gemini API
- [x] Define modular project structure
- [x] Extract structured data from receipt images
- [x] Read known products automatically from Excel
- [x] Read known aliases automatically from Excel
- [ ] Match receipt products against the catalogue
- [ ] Generate review items for uncertain matches
- [ ] Automatically update Excel
- [ ] Add normalized price calculations
- [ ] Add price comparison logic
- [ ] Add dashboard and charts
- [ ] Build a Streamlit interface
- [ ] Migrate from Excel to a database
- [ ] Support multiple AI providers

## Privacy

Receipt images, personal data, API keys, and local Excel databases should not be uploaded to the repository.

These files are excluded through `.gitignore`.

## Status

This project is currently under development.
