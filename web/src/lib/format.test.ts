import { describe, expect, it } from "vitest";

import { formatField, formatHash, formatTimestamp, formatValue } from "./format";
import type { EvidenceView } from "./snapshot/types";

function evidence(overrides: Partial<EvidenceView> = {}): EvidenceView {
  return {
    observationId: "obs",
    sourceId: "source",
    sourceType: "official_product",
    sourceUrl: "https://example.org",
    retrievedAt: "2026-09-20T08:00:00Z",
    sha256: "a".repeat(64),
    field: "loan_amount",
    state: "present",
    rawText: "INR 0",
    locator: "#amount",
    context: "offer",
    confidence: 1,
    value: {
      kind: "money",
      lower: "0",
      upper: null,
      text: null,
      boolean: null,
      options: [],
      unit: "INR",
      period: "unknown",
      basis: "unknown",
      qualifier: "exact",
      approximate: false,
    },
    ...overrides,
  };
}

describe("display-only formatters", () => {
  it.each([
    ["up_to", null, "120000.0", false, "Up to 120000.0 INR"],
    ["from", "0", null, false, "From 0 INR"],
    ["range", "100", "200", false, "100–200 INR"],
    ["exact", "100", null, true, "Approximately 100 INR"],
    ["up_to", null, "100", true, "Approximately Up to 100 INR"],
    ["conditional", "100", null, false, "Conditional 100 INR"],
    ["policy", "100", null, false, "Policy 100 INR"],
  ])("preserves %s numeric semantics", (qualifier, lower, upper, approximate, expected) => {
    expect(formatValue(evidence({ value: { ...evidence().value!, qualifier, lower, upper, approximate } }))).toBe(expected);
  });

  it.each(["policy", "conditional"])("preserves stored %s text", (qualifier) => {
    expect(formatValue(evidence({ value: { ...evidence().value!, qualifier, text: "Subject to lender policy" } }))).toBe("Subject to lender policy");
  });

  it("keeps stored zero, false, and unknown distinct", () => {
    expect(formatValue(evidence())).toBe("0 INR");
    expect(formatValue(evidence({ value: { ...evidence().value!, lower: null, kind: "boolean", boolean: false, unit: null } }))).toBe("No");
    expect(formatValue(evidence({ state: "absent", value: null }))).toBe("Absent");
  });

  it("preserves annual period and omits unknown period", () => {
    expect(formatValue(evidence({ value: { ...evidence().value!, lower: "12", unit: "percent", period: "annual" } }))).toBe("12 percent annual");
    expect(formatValue(evidence())).toBe("0 INR");
  });

  it("uses safe fallback formatting", () => {
    expect(formatField("minimum_credit_score")).toBe("Minimum Credit Score");
    expect(formatTimestamp("not-a-date")).toBe("Unknown time");
    expect(formatHash("f".repeat(64))).toHaveLength(64);
    expect(formatHash(null)).toBe("Hash unavailable");
  });
});
