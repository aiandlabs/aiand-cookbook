// Structured extraction with the OpenAI SDK and a strict JSON schema.
import OpenAI from "openai";

import {
  invoiceJsonSchema,
  MODEL,
  parseExtraction,
  REQUEST_TIMEOUT_MS,
  requireApiKey,
  SYSTEM_PROMPT,
  USER_PROMPT,
} from "./invoice.js";

const BASE_URL = "https://api.aiand.com/v1";

function errorMessage(error: unknown): string {
  if (error instanceof OpenAI.APIConnectionError) {
    return `Network error while calling the ai& API: ${error.message}`;
  }
  if (error instanceof OpenAI.APIError) {
    return `ai& API request failed with status ${error.status}: ${error.message}`;
  }
  return error instanceof Error ? error.message : String(error);
}

async function main(): Promise<void> {
  const client = new OpenAI({
    apiKey: requireApiKey(),
    baseURL: BASE_URL,
    timeout: REQUEST_TIMEOUT_MS,
  });

  const response = await client.chat.completions.create({
    model: MODEL,
    messages: [
      { role: "system", content: SYSTEM_PROMPT },
      { role: "user", content: USER_PROMPT },
    ],
    temperature: 0,
    max_completion_tokens: 800,
    response_format: {
      type: "json_schema",
      json_schema: {
        name: "invoice_extraction",
        schema: invoiceJsonSchema(),
        strict: true,
      },
    },
  });

  const content = response.choices[0]?.message.content;
  if (typeof content !== "string") {
    throw new Error("Expected the model to return JSON text.");
  }

  console.log(JSON.stringify(parseExtraction(content), null, 2));
}

try {
  await main();
} catch (error) {
  console.error(errorMessage(error));
  process.exitCode = 1;
}
