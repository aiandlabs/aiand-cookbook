# Structured Extraction With Python

Extract invoice details from plain text into structured JSON. The recipe has two variants:

- `openai_extraction.py` uses the OpenAI SDK and `response_format` with a strict JSON schema.
- `anthropic_extraction.py` uses the Anthropic SDK and a forced tool call. The schema is the tool's `input_schema`, and the result is the tool call's input.

This recipe builds on the ai& [Structured Outputs](https://docs.aiand.com/capabilities/structured-outputs/) docs.

## What This Demonstrates

- Calling ai& with the OpenAI SDK (base URL `https://api.aiand.com/v1`) and the Anthropic SDK (base URL `https://api.aiand.com`).
- Asking the model for output that follows a strict schema.
- Validating the output locally with `jsonschema`.
- Reading `AIAND_API_KEY` from the environment without hardcoding credentials.

`invoice.py` holds the text, the schema and the validation that both variants use.

## Setup

```sh
cd python/structured-extraction
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export AIAND_API_KEY=your-aiand-api-key
```

## Run

```sh
python openai_extraction.py
python anthropic_extraction.py
```

Each script prints validated JSON that matches the invoice schema. To use a different model, set `AIAND_MODEL`.

## Notes on the Anthropic variant

- The Messages API on ai& does not support `output_config.format` yet. It ignores the parameter, and the model answers in free text. Use a forced tool call, as this recipe does.
- Find the result by the `tool_use` block. Do not rely on `stop_reason`: for a forced tool call, ai& can return `end_turn` instead of `tool_use`.
