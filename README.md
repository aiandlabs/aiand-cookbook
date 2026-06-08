# aiand-cookbook

Runnable recipes for the ai& API using the native ai& SDKs.

## Recipes

### Structured Extraction

Extract invoice details from natural-language text into a strict JSON shape.

- Related docs: [Structured Outputs](https://docs.aiand.com/capabilities/structured-outputs/)
- Python: [`python/structured-extraction`](python/structured-extraction)
- TypeScript: [`typescript/structured-extraction`](typescript/structured-extraction)

Both examples read `AIAND_API_KEY` from the environment and use the native ai& SDKs:

- Python package: `aiand`
- TypeScript package: `@aiand/sdk`

## Prerequisites

- An ai& API key.
- Python 3.10 or newer for Python recipes.
- Node 18 or newer for TypeScript recipes.

Set your API key before running a recipe:

```sh
export AIAND_API_KEY=your-aiand-api-key
```
