"""Structured extraction with the Anthropic SDK and a forced tool call.

The schema is the tool's input_schema, and tool_choice makes the model call
that tool, so the result arrives as the tool_use block's input.
"""

import anthropic
from anthropic import Anthropic

from invoice import (
    INVOICE_SCHEMA,
    MODEL,
    REQUEST_TIMEOUT_SECONDS,
    SYSTEM_PROMPT,
    USER_PROMPT,
    print_extraction,
    require_api_key,
    validate_extraction,
)

# The Anthropic SDK adds /v1/messages itself, so the base URL has no /v1.
BASE_URL = "https://api.aiand.com"
TOOL_NAME = "record_invoice"


def main() -> None:
    client = Anthropic(
        api_key=require_api_key(),
        base_url=BASE_URL,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    try:
        message = client.messages.create(
            model=MODEL,
            max_tokens=800,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": USER_PROMPT}],
            tools=[
                {
                    "name": TOOL_NAME,
                    "description": "Record the invoice data extracted from the text.",
                    "input_schema": INVOICE_SCHEMA,
                }
            ],
            tool_choice={"type": "tool", "name": TOOL_NAME},
        )
    except anthropic.APIStatusError as error:
        raise SystemExit(
            f"ai& API request failed with status {error.status_code}: {error.message}"
        ) from error
    except anthropic.APIConnectionError as error:
        raise SystemExit(f"Network error while calling the ai& API: {error}") from error

    # Find the tool_use block by type. Do not rely on stop_reason.
    tool_use = next(
        (block for block in message.content if block.type == "tool_use" and block.name == TOOL_NAME),
        None,
    )
    if tool_use is None:
        raise SystemExit(f"Expected the model to call {TOOL_NAME}.")

    print_extraction(validate_extraction(tool_use.input))


if __name__ == "__main__":
    main()
