// The invoice text, schema and validation shared by both variants of this recipe.
import { z } from "zod";

export const MODEL = process.env.AIAND_MODEL ?? "openai/gpt-oss-120b";
export const REQUEST_TIMEOUT_MS = 60_000;

export const SYSTEM_PROMPT = "Extract invoice data. Return only data that matches the provided schema.";

const invoiceText = `
Northstar Coffee Supply sent invoice INV-2026-0142 to Bluebird Labs on
May 18, 2026. Payment is due by June 17, 2026. The invoice includes
12 cases of espresso beans at 48.50 USD each and 4 replacement grinder
burr sets at 82.00 USD each. The billing contact is Mara Chen at
mara.chen@bluebird.example.
`.trim();

export const USER_PROMPT = `Extract structured invoice data from this text:\n\n${invoiceText}`;

export const invoiceExtractionSchema = z
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

export type InvoiceExtraction = z.infer<typeof invoiceExtractionSchema>;

// The JSON Schema sent to the API, derived from the Zod schema.
export function invoiceJsonSchema(): { type: "object"; [key: string]: unknown } {
  const jsonSchema = z.toJSONSchema(invoiceExtractionSchema) as { type: "object"; [key: string]: unknown };
  delete jsonSchema.$schema;
  return jsonSchema;
}

export function requireApiKey(): string {
  const apiKey = process.env.AIAND_API_KEY;
  if (!apiKey) {
    throw new Error("Set AIAND_API_KEY in your environment.");
  }
  return apiKey;
}

export function validateExtraction(value: unknown): InvoiceExtraction {
  const result = invoiceExtractionSchema.safeParse(value);
  if (!result.success) {
    throw new Error(`Model output did not match the schema:\n${z.prettifyError(result.error)}`);
  }
  return result.data;
}

export function parseExtraction(content: string): InvoiceExtraction {
  let parsed: unknown;
  try {
    parsed = JSON.parse(content);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    throw new Error(`Model returned invalid JSON: ${message}`);
  }
  return validateExtraction(parsed);
}
