// Structured extraction with the Anthropic SDK and a forced tool call.
//
// The schema is the tool's input_schema, and tool_choice makes the model call
// that tool, so the result arrives as the tool_use block's input.
import Anthropic from "@anthropic-ai/sdk";

import {
  invoiceJsonSchema,
  MODEL,
  REQUEST_TIMEOUT_MS,
  requireApiKey,
  SYSTEM_PROMPT,
  USER_PROMPT,
  validateExtraction,
} from "./invoice.js";

// The Anthropic SDK adds /v1/messages itself, so the base URL has no /v1.
const BASE_URL = "https://api.aiand.com";
const TOOL_NAME = "record_invoice";

function errorMessage(error: unknown): string {
  if (error instanceof Anthropic.APIConnectionError) {
    return `Network error while calling the ai& API: ${error.message}`;
  }
  if (error instanceof Anthropic.APIError) {
    return `ai& API request failed with status ${error.status}: ${error.message}`;
  }
  return error instanceof Error ? error.message : String(error);
}

async function main(): Promise<void> {
  const client = new Anthropic({
    apiKey: requireApiKey(),
    baseURL: BASE_URL,
    timeout: REQUEST_TIMEOUT_MS,
  });

  const message = await client.messages.create({
    model: MODEL,
    max_tokens: 800,
    system: SYSTEM_PROMPT,
    messages: [{ role: "user", content: USER_PROMPT }],
    tools: [
      {
        name: TOOL_NAME,
        description: "Record the invoice data extracted from the text.",
        input_schema: invoiceJsonSchema(),
      },
    ],
    tool_choice: { type: "tool", name: TOOL_NAME },
  });

  // Find the tool_use block by type. Do not rely on stop_reason.
  const toolUse = message.content.find(
    (block): block is Anthropic.ToolUseBlock => block.type === "tool_use" && block.name === TOOL_NAME,
  );
  if (!toolUse) {
    throw new Error(`Expected the model to call ${TOOL_NAME}.`);
  }

  console.log(JSON.stringify(validateExtraction(toolUse.input), null, 2));
}

try {
  await main();
} catch (error) {
  console.error(errorMessage(error));
  process.exitCode = 1;
}
