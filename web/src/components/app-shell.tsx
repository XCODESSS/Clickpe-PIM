import Link from "next/link";
import type { ReactNode } from "react";

import { formatTimestamp } from "@/lib/format";
import type { PublicSnapshot } from "@/lib/snapshot/types";

const routes = [
  ["Overview", "/"],
  ["Review queue", "/reviews/"],
  ["Products", "/products/"],
  ["Changes", "/changes/"],
  ["Providers", "/providers/"],
] as const;

export function AppShell({ snapshot, activePath, children }: {
  snapshot: PublicSnapshot;
  activePath: string;
  children: ReactNode;
}) {
  return (
    <div className={snapshot.run.synthetic ? "has-synthetic-banner" : undefined}>
      <a className="skip-link" href="#main-content">Skip to main content</a>
      {snapshot.run.synthetic ? (
        <div className="synthetic-banner" role="status">Synthetic interface preview</div>
      ) : null}
      <div className="app-frame">
        <aside className="navigation-rail">
          <div className="brand-block">
            <Link className="brand-name" href="/">ClickPe PIM</Link>
            <span className="brand-detail">Run {snapshot.run.status} · {formatTimestamp(snapshot.run.finishedAt)}</span>
          </div>
          <nav className="primary-navigation" aria-label="Primary navigation">
            {routes.map(([label, href]) => (
              <Link key={href} href={href} aria-current={activePath === href ? "page" : undefined}>
                {label}
              </Link>
            ))}
          </nav>
          <p className="rail-method">Read-only public evidence from one finalized run.</p>
        </aside>
        <main id="main-content" className="workspace">{children}</main>
      </div>
    </div>
  );
}
