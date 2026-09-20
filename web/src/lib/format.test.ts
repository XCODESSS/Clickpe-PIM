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
