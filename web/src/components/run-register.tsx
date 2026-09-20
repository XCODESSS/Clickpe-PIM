import type { PublicSnapshot } from "@/lib/snapshot/types";

import { StatusMark } from "./status-mark";

export function RunRegister({ snapshot }: { snapshot: PublicSnapshot }) {
  const { overview } = snapshot;
  const coverage = overview.coverageDenominator === 0
    ? "Unknown"
    : `${overview.coverageNumerator}/${overview.coverageDenominator}`;
  const values = [
    ["Inventory products", overview.inventoryProducts],
    ["Monitored cohort", overview.cohortProducts],
    ["Applicable official-source coverage", coverage],
    ["Review items", overview.reviewItems],
    ["High priority", overview.highPriorityItems],
    ["Source failures", overview.failedSources],
    ["Recent changes", overview.recentChanges],
    ["Finalized runs", overview.finalizedRuns],
  ] as const;
  return (
    <section className="run-register" aria-labelledby="run-register-heading">
      <h2 id="run-register-heading">Run register</h2>
      <dl>
        {values.map(([label, value]) => (
          <div key={label}><dt>{label}</dt><dd>{value}</dd></div>
        ))}
        <div><dt>Run status</dt><dd><StatusMark value={snapshot.run.status} /></dd></div>
      </dl>
    </section>
  );
}
