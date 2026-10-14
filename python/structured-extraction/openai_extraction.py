"""Structured extraction with the OpenAI SDK and a strict JSON schema."""

import openai
from openai import OpenAI

from invoice import (
    INVOICE_SCHEMA,
    MODEL,
    REQUEST_TIMEOUT_SECONDS,
    SYSTEM_PROMPT,
    USER_PROMPT,
    parse_extraction,
    print_extraction,
    require_api_key,
)

BASE_URL = "https://api.aiand.com/v1"


def main() -> None:
    client = OpenAI(
        api_key=require_api_key(),
        base_url=BASE_URL,
        timeout=REQUEST_TIMEOUT_SECONDS,
    )

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": USER_PROMPT},
            ],
            temperature=0,
            max_completion_tokens=800,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "invoice_extraction",
                    "schema": INVOICE_SCHEMA,
                    "strict": True,
                },
            },
        )
    except openai.APIStatusError as error:
        raise SystemExit(
            f"ai& API request failed with status {error.status_code}: {error.message}"
        ) from error
    except openai.APIConnectionError as error:
        raise SystemExit(f"Network error while calling the ai& API: {error}") from error

    content = response.choices[0].message.content
    if not isinstance(content, str):
        raise SystemExit("Expected the model to return JSON text.")

    print_extraction(parse_extraction(content))


if __name__ == "__main__":
    main()
