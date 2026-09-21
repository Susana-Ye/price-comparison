import base64
import json
import mimetypes
from pathlib import Path
from typing import Any

from google import genai

from src.config import GEMINI_MODEL
from src.receipt_schema import ReceiptExtraction
from src.system_prompt import SYSTEM_PROMPT


client = genai.Client() # The SDK automatically reads the API key from the environment variable GOOGLE_API_KEY. Make sure to set it before running the script.


def _encode_file_base64(file_path: str | Path) -> str:
    """
    Read a file (in this case, the receipt image) and return its Base64-encoded contents. 
    """

    file_path = Path(file_path)

    with file_path.open("rb") as file: #"rb" mode is used to read the file in binary mode
        return base64.b64encode(
            file.read()
        ).decode("utf-8")


def _get_mime_type(file_path: str | Path) -> str:
    """
    Detect the MIME type (e.g., image/jpeg) of the receipt file. 
    Gemini needs to know the MIME type to correctly interpret the file.
    """

    file_path = Path(file_path)

    mime_type, _ = mimetypes.guess_type(file_path) # returns a tuple (type, encoding), we only care about the MIME type here.

    if mime_type is None:
        raise ValueError(
            f"Could not determine MIME type for file: {file_path}"
        )

    return mime_type


def _build_context(
    products: list[dict[str, Any]],
    aliases: list[dict[str, Any]],
) -> str:
    """
    Build the catalogue context sent to Gemini.
    Here we combine SYSTEM_PROMPT + KNOWN_PRODUCTS + KNOWN_ALIASES
    """

    products_json = json.dumps(
        products,
        ensure_ascii=False, # allows non-ASCII characters (like accented letters) to be preserved in the JSON output.
        indent=2,
    )

    aliases_json = json.dumps(
        aliases,
        ensure_ascii=False,
        indent=2,
    )

    return f""" 
{SYSTEM_PROMPT}

KNOWN_PRODUCTS:
{products_json}

KNOWN_ALIASES:
{aliases_json}

Analyse the attached receipt according to the structured output schema.
"""


def analyse_receipt(
    receipt_path: str | Path,
    products: list[dict[str, Any]],
    aliases: list[dict[str, Any]],
) -> ReceiptExtraction:
    """
    Analyse a receipt image with Gemini and validate the structured result.
    """

    receipt_path = Path(receipt_path)

    if not receipt_path.exists():
        raise FileNotFoundError(
            f"Receipt file not found: {receipt_path}"
        )

    image_base64 = _encode_file_base64(receipt_path)

    mime_type = _get_mime_type(receipt_path)

    prompt = _build_context(products=products, aliases=aliases,)

    interaction = client.interactions.create(
        model=GEMINI_MODEL,

        input=[
            {"type": "text", "text": prompt,},
            {"type": "image", "data": image_base64, "mime_type": mime_type,},
        ], # Interactions API supports multimodal inputs, send catalogue context + receipt image

        response_format={
            "type": "text",
            "mime_type": "application/json",
            "schema": ReceiptExtraction.model_json_schema(), # Transforms the Pydantic model into a JSON schema that Gemini can use to validate its output.
        }, # Structured output schema is provided to Gemini
    )

    if not interaction.output_text:
        raise ValueError("Gemini returned an empty response.")

    result = ReceiptExtraction.model_validate_json(
        interaction.output_text
    ) # Validate the JSON output, if it doesn't conform to the schema, this will raise a validation error.

    return result