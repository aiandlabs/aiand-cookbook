import { Configuration, FetchError, OpenaiApi, ResponseError } from "@aiand/sdk";
import { z } from "zod";

const MODEL = "openai/gpt-oss-120b";
const REQUEST_TIMEOUT_MS = 60_000;

const invoiceText = `
Northstar Coffee Supply sent invoice INV-2026-0142 to Bluebird Labs on
May 18, 2026. Payment is due by June 17, 2026. The invoice includes
12 cases of espresso beans at 48.50 USD each and 4 replacement grinder
burr sets at 82.00 USD each. The billing contact is Mara Chen at
mara.chen@bluebird.example.
`.trim();

const invoiceExtractionSchema = z
  .object({
    invoice_number: z.string(),
    vendor: z.string(),
    customer: z.string(),
    invoice_date: z.iso.date().describe("ISO 8601 date"),
    due_date: z.iso.date().describe("ISO 8601 date"),
    currency: z.string(),
    billing_contact: z
      .object({
        name: z.string(),
        email: z.email(),
      })
      .strict(),
    line_items: z.array(
      z
        .object({
          description: z.string(),
          quantity: z.number(),
          unit_price: z.number(),
        })
        .strict(),
    ),
  })
  .strict();

type InvoiceExtraction = z.infer<typeof invoiceExtractionSchema>;

function jsonSchemaFor(schema: z.ZodType): Record<string, unknown> {
  const jsonSchema = z.toJSONSchema(schema) as Record<string, unknown>;
  delete jsonSchema.$schema;
  return jsonSchema;
}

function parseExtraction(content: string): InvoiceExtraction {
  let parsed: unknown;

  try {
    parsed = JSON.parse(content);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`Model returned invalid JSON: ${message}`);
  }

  const result = invoiceExtractionSchema.safeParse(parsed);
  if (!result.success) {
    throw new Error(`Model JSON did not match the schema:\n${z.prettifyError(result.error)}`);
  }

  return result.data;
}

function errorMessage(error: unknown): string {
  if (error instanceof ResponseError) {
    return `ai& API request failed with status ${error.response.status}: ${error.response.statusText}`;
  }

  if (error instanceof FetchError) {
    return `Network error while calling the ai& API: ${error.message}`;
  }

  if (error instanceof Error && error.name === "AbortError") {
    return "ai& API request timed out.";
  }

  return error instanceof Error ? error.message : String(error);
}

async function main(): Promise<void> {
  const apiKey = process.env.AIAND_API_KEY;
  if (!apiKey) {
    throw new Error("Set AIAND_API_KEY in your environment.");
  }

  const client = new OpenaiApi(new Configuration({ accessToken: apiKey }));
  const response = await client.createChatCompletion(
    {
      createChatCompletionRequest: {
        model: MODEL,
        messages: [
          {
            role: "system",
            content: "Extract invoice data. Return only JSON that matches the provided schema.",
          },
          {
            role: "user",
            content: `Extract structured invoice data from this text:\n\n${invoiceText}`,
          },
        ],
        temperature: 0,
        max_completion_tokens: 800,
        response_format: {
          type: "json_schema",
          json_schema: {
            name: "invoice_extraction",
            schema: jsonSchemaFor(invoiceExtractionSchema),
            strict: true,
          },
        },
      },
    },
    { signal: AbortSignal.timeout(REQUEST_TIMEOUT_MS) },
  );

  const content = response.choices[0]?.message.content;
  if (typeof content !== "string") {
    throw new Error("Expected the model to return JSON text.");
  }

  const extracted = parseExtraction(content);
  console.log(JSON.stringify(extracted, null, 2));
}

try {
  await main();
} catch (error) {
  console.error(errorMessage(error));
  process.exitCode = 1;
}
