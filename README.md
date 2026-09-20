# AI Price Comparison Agent

An AI-powered receipt processing and price comparison system.

The project analyzes purchase receipts, extracts structured product and pricing data using Google Gemini, normalizes product names, and stores the results in an Excel-based price history.

The long-term goal is to build a personal price comparison agent capable of tracking price changes across different stores and identifying where products are cheapest.

## Current Features

- Receipt analysis using Google Gemini API
- Structured JSON output using Pydantic
- Product normalization
- Product confidence and review status
- Excel-based product catalogue
- Historical price tracking
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
Excel database
      ↓
Price comparison
```

## Project Structure

```text
price-comparison/
│
├── receipts/               # Receipt images (not uploaded to GitHub)
├── output/                 # Generated outputs
│
├── receipt_agent.py        # Main receipt processing logic
├── schemas.py              # Pydantic models / structured output schema
├── prompts.py              # AI system prompts
├── test_gemini.py          # Gemini API connection test
│
├── requirements.txt
├── .gitignore
└── README.md
```

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

## Data Model

The Excel file currently contains several structured tables.

### Products

Master product catalogue.

```text
Product ID
Normalized name
Category
Subcategory
Brand
Comparison unit
```

### Price History

Stores individual purchase observations.

```text
Date
Store
Product ID
Receipt product name
Quantity
Gross price
Discount
Net price
Comparable price
```

### Product Aliases

Maps retailer-specific receipt names to normalized products.

Example:

```text
CHIQUITA LOS → P0006 → Banana
BANANEN      → P0006 → Banana
```

### Review

Stores products or discounts that the AI cannot identify confidently.

The system prefers human review instead of guessing uncertain information.

## AI Design Principles

The AI should:

- Never invent product IDs
- Never invent weights, quantities, brands, or discounts
- Preserve the original receipt product name
- Normalize product names into Spanish
- Prefer human review when confidence is low
- Only assign discounts when the relationship is clear
- Return structured JSON

Python is responsible for:

- Validation
- Price calculations
- Unit conversions
- Excel updates
- ID generation
- Historical data storage

## Roadmap

- [x] Define Excel data structure
- [x] Create product catalogue
- [x] Create price history
- [x] Create product alias system
- [x] Define structured AI output
- [x] Connect to Gemini API
- [ ] Extract data from receipt images
- [ ] Read known products automatically from Excel
- [ ] Match receipt products against the catalogue
- [ ] Automatically update Excel
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
