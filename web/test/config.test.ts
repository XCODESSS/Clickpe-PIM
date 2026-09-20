import { readFileSync } from "node:fs";

import { describe, expect, it } from "vitest";

describe("static UI boundary", () => {
  it("cannot acquire a backend runtime", () => {
    const pkg = JSON.parse(readFileSync("package.json", "utf8"));
    const config = readFileSync("next.config.ts", "utf8");
    expect(pkg.engines.node).toBe(">=22.19 <23");
    expect(pkg.scripts).not.toHaveProperty("start:api");
    expect(config).toContain('output: "export"');
    expect(config).toContain("unoptimized: true");
    expect(JSON.stringify(pkg)).not.toMatch(/streamlit|clickpe_pim|fastapi/i);
  });
});
