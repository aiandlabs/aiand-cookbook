"""The invoice text, schema and validation shared by both variants of this recipe."""

import json
import os
from typing import Any

from jsonschema import Draft202012Validator, ValidationError

MODEL = os.environ.get("AIAND_MODEL", "openai/gpt-oss-120b")
REQUEST_TIMEOUT_SECONDS = 60.0

SYSTEM_PROMPT = "Extract invoice data. Return only data that matches the provided schema."

INVOICE_TEXT = """
Northstar Coffee Supply sent invoice INV-2026-0142 to Bluebird Labs on
May 18, 2026. Payment is due by June 17, 2026. The invoice includes
12 cases of espresso beans at 48.50 USD each and 4 replacement grinder
burr sets at 82.00 USD each. The billing contact is Mara Chen at
mara.chen@bluebird.example.
""".strip()

USER_PROMPT = f"Extract structured invoice data from this text:\n\n{INVOICE_TEXT}"

INVOICE_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "invoice_number": {"type": "string"},
        "vendor": {"type": "string"},
        "customer": {"type": "string"},
        "invoice_date": {"type": "string", "description": "ISO 8601 date"},
        "due_date": {"type": "string", "description": "ISO 8601 date"},
        "currency": {"type": "string"},
        "billing_contact": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "name": {"type": "string"},
                "email": {"type": "string"},
            },
            "required": ["name", "email"],
        },
        "line_items": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "description": {"type": "string"},
                    "quantity": {"type": "number"},
                    "unit_price": {"type": "number"},
                },
                "required": ["description", "quantity", "unit_price"],
            },
        },
    },
    "required": [
        "invoice_number",
        "vendor",
        "customer",
        "invoice_date",
        "due_date",
        "currency",
        "billing_contact",
        "line_items",
    ],
}

INVOICE_VALIDATOR = Draft202012Validator(INVOICE_SCHEMA)


def require_api_key() -> str:
    api_key = os.environ.get("AIAND_API_KEY")
    if not api_key:
        raise SystemExit("Set AIAND_API_KEY in your environment.")
    return api_key


def validate_extraction(extracted: Any) -> dict[str, Any]:
    try:
        INVOICE_VALIDATOR.validate(extracted)
    except ValidationError as error:
        raise SystemExit(f"Model output did not match the schema: {error.message}") from error
    return extracted


def parse_extraction(content: str) -> dict[str, Any]:
    try:
        extracted = json.loads(content)
    except json.JSONDecodeError as error:
        raise SystemExit(f"Model returned invalid JSON: {error}") from error
    return validate_extraction(extracted)


def print_extraction(extracted: dict[str, Any]) -> None:
    print(json.dumps(extracted, indent=2, sort_keys=True))
