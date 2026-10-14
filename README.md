# aiand-cookbook

Runnable recipes for the ai& API, using the OpenAI and Anthropic SDKs.

ai& is compatible with both APIs. Use the OpenAI SDK with the base URL `https://api.aiand.com/v1`, or the Anthropic SDK with the base URL `https://api.aiand.com`. Each recipe has a variant for each SDK.

## Recipes

### Structured Extraction

Extract invoice details from natural-language text into a strict JSON shape.

| | OpenAI SDK | Anthropic SDK |
| -- | -- | -- |
| Method | `response_format` with a strict JSON schema | a forced tool call whose `input_schema` is the schema |
| Python | [`python/structured-extraction/openai_extraction.py`](python/structured-extraction/openai_extraction.py) | [`python/structured-extraction/anthropic_extraction.py`](python/structured-extraction/anthropic_extraction.py) |
| TypeScript | [`typescript/structured-extraction/openai_extraction.ts`](typescript/structured-extraction/openai_extraction.ts) | [`typescript/structured-extraction/anthropic_extraction.ts`](typescript/structured-extraction/anthropic_extraction.ts) |

Docs: [Structured Outputs](https://docs.aiand.com/capabilities/structured-outputs/), [Structured Extraction](https://docs.aiand.com/cookbook/extraction/), [Messages API](https://docs.aiand.com/api/messages/).

## Prerequisites

- An ai& API key.
- Python 3.10 or newer for Python recipes.
- Node 22 or newer for TypeScript recipes.

Set your API key before you run a recipe:

```sh
export AIAND_API_KEY=your-aiand-api-key
```

The recipes use `openai/gpt-oss-120b`. To use a different model, set `AIAND_MODEL`.

## Tests

CI runs each recipe against the live ai& API on each pull request, on each push to `main`, and once a day. The run fails if a recipe exits with an error or if its output does not match the schema.
