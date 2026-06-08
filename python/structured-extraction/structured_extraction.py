import json
import os
from typing import Any

import aiand
from jsonschema import Draft202012Validator, ValidationError
from urllib3.exceptions import HTTPError


MODEL = "openai/gpt-oss-120b"
REQUEST_TIMEOUT = (10, 60)

INVOICE_TEXT = """
Northstar Coffee Supply sent invoice INV-2026-0142 to Bluebird Labs on
May 18, 2026. Payment is due by June 17, 2026. The invoice includes
12 cases of espresso beans at 48.50 USD each and 4 replacement grinder
burr sets at 82.00 USD each. The billing contact is Mara Chen at
mara.chen@bluebird.example.
""".strip()

INVOICE_SCHEMA = {
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


def build_request() -> aiand.CreateChatCompletionRequest:
    return aiand.CreateChatCompletionRequest.from_dict(
        {
            "model": MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Extract invoice data. Return only JSON that matches the provided schema."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Extract structured invoice data from this text:\n\n{INVOICE_TEXT}",
                },
            ],
            "temperature": 0,
            "max_completion_tokens": 800,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "invoice_extraction",
                    "schema": INVOICE_SCHEMA,
                    "strict": True,
                },
            },
        }
    )


def parse_extraction(content: str) -> dict[str, Any]:
    try:
        extracted = json.loads(content)
    except json.JSONDecodeError as error:
        raise SystemExit(f"Model returned invalid JSON: {error}") from error

    try:
        INVOICE_VALIDATOR.validate(extracted)
    except ValidationError as error:
        raise SystemExit(f"Model JSON did not match the schema: {error.message}") from error

    return extracted


def main() -> None:
    api_key = os.environ.get("AIAND_API_KEY")
    if not api_key:
        raise SystemExit("Set AIAND_API_KEY in your environment.")

    configuration = aiand.Configuration(access_token=api_key)
    request = build_request()

    with aiand.ApiClient(configuration) as api_client:
        client = aiand.OpenaiApi(api_client)
        try:
            response = client.create_chat_completion(request, _request_timeout=REQUEST_TIMEOUT)
        except aiand.ApiException as error:
            raise SystemExit(
                f"ai& API request failed with status {error.status}: {error.reason}"
            ) from error
        except HTTPError as error:
            raise SystemExit(f"Network error while calling the ai& API: {error}") from error

    content = response.choices[0].message.content
    if not isinstance(content, str):
        raise RuntimeError("Expected the model to return JSON text.")

    extracted = parse_extraction(content)
    print(json.dumps(extracted, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
