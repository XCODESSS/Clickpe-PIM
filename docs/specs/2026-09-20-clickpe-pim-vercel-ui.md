# ClickPe PIM Vercel Interface — design specification

Source: the user's frontend-design brief and UI-only scope clarification in the current conversation on 2026-09-20. Product semantics remain governed by `docs/specs/2026-09-19-clickpe-product-intelligence-monitor.md`.

## Product, audience, and job

The product is an evidence-first interface for inspecting whether public ClickPe loan claims can be compared with reviewed provider claims. Its primary audience is an analyst or reviewer who needs to understand a stored comparison quickly without mistaking a review item for an error, recommendation, or regulatory finding.

The interface's primary job is to make the chain from run health to comparison reason to exact evidence legible. It is not a loan marketplace, a consumer recommendation site, or a place to edit monitoring logic.

## Immutable implementation boundary

This work is presentation-only.

- Do not modify `src/clickpe_pim/**`, `app/**`, `tests/**`, `config/**`, `config.yaml`, `pyproject.toml`, `requirements.txt`, `uv.lock`, the SQLite schema, collection, extraction, normalization, mapping, comparison, scoring, monitoring, evaluation, or reporting logic.
- Keep the current Streamlit interface available and unchanged. It remains the local interface for append-only review events.
- Add the Vercel interface under `web/**`. It may read a finalized SQLite snapshot in read-only mode and may filter, sort, count, and format stored records for display.
- Never recalculate a normalized value, comparison status, priority, mapping decision, freshness band, completeness score, or change event in TypeScript.
- Never write to SQLite from the Vercel interface. Do not expose a review mutation, server action, route handler, or public API.
- Do not publish `review_events`, reviewer identities, review notes, local paths, raw database files, environment values, or unselected database records.
- A synthetic snapshot must carry a persistent synthetic-data banner. A production build must reject a synthetic run.

## Design concept: the evidence register

The interface borrows its structure from an analyst's reconciliation sheet rather than a consumer-finance website. The memorable device is the **evidence seam**: ClickPe evidence sits on the left, the applicable comparison source sits on the right, and a narrow central register records the stored comparison status and reason. Source boundaries, locators, hashes, timestamps, and mapping scope determine visual structure.

The seam appears once as the overview's characteristic opening and again as the full review-detail workbench. It is not repeated as decoration in unrelated views.

## Compact token system

### Color

| Token | Hex | Role |
|---|---:|---|
| Archive ink | `#142831` | Primary text, strong rules, and failed/unknown states paired with text |
| Cold stock | `#EEF3F5` | Page field; a cool archival paper rather than a warm cream |
| Source white | `#FFFFFF` | Evidence surfaces and focused reading areas |
| Register blue | `#2F5BEA` | Selected row, keyboard focus, links, and the comparison register |
| Review amber | `#A65F00` | Stored review/difference state; never the only status signal |
| Verified green | `#176B55` | Stored match/healthy state; never the only status signal |

No gradients are used. Status always combines color with an icon-free shape, border treatment, and readable text. Source white is reserved for evidence, which makes quoted material look physically separate from interpretation.

### Type

- **Archivo Variable** is the interface family. Body copy uses width 100 and weight 430–500. Navigation and data headings use weight 620. Display text uses width 88–92 rather than a separate theatrical display face.
- **Source Serif 4 Variable** appears only for exact source quotations. The type change means “verbatim evidence,” not “editorial flourish.”
- Numeric columns use tabular numerals from Archivo. Small labels remain proportional sans, not monospace.
- Type scale in rem: `0.75`, `0.875`, `1`, `1.25`, `1.563`, `1.953`, `2.441`.
- Body measure is capped at `68ch`; evidence quotations at `72ch` with `1.65` line-height.

### Layout

- Desktop uses a 14-column frame: a fixed 216 px navigation rail plus a 12-column content grid.
- Main content is left aligned. Numeric values are right aligned. Prose is never justified or centered.
- Evidence detail uses a `5 / 2 / 5` column split: left source, decision register, right source.
- Dense collections use continuous ledger rows with meaningful column rules. Identical rounded cards are prohibited.
- Border radius is limited to 2 px for focusable controls and 6 px for the mobile evidence disclosure. Large cards and soft shadows are prohibited.
- Mobile collapses the evidence seam into source → decision → source reading order and uses a compact bottom navigation.

### Motion

There is no automatic section-by-section entrance animation. Motion is reserved for direct actions: opening evidence, changing filters, and moving keyboard focus. Transitions stay under 160 ms and are disabled by `prefers-reduced-motion`.

## Wireframes

### Overview, desktop

```text
┌─────────────────┬────────────────────────────────────────────────────────────┐
│ ClickPe PIM     │ Latest finalized run · timestamp · complete/partial       │
│                 ├───────────────────────┬──────────┬─────────────────────────┤
│ Overview        │ ClickPe evidence      │ status   │ Comparison evidence     │
│ Reviews   12    │ “₹20,000–₹5 lakh…”   │ Different│ “₹20,000–₹3 lakh…”      │
│ Products        │ source · locator      │ reason   │ source · locator         │
│ Changes         ├───────────────────────┴──────────┴─────────────────────────┤
│ Providers       │ Inventory | cohort | official coverage | open review | run│
│                 ├─────────────────────────────────────┬──────────────────────┤
│                 │ Review ledger                       │ Source health         │
│ Method note     │ priority · product · field · state  │ checked / failed      │
└─────────────────┴─────────────────────────────────────┴──────────────────────┘
```

### Review detail, desktop

```text
┌─────────────────┬────────────────────────────────────────────────────────────┐
│ navigation      │ Product name / field / stored priority                   │
│                 ├───────────────────────┬──────────┬─────────────────────────┤
│                 │ ClickPe               │ decision │ Provider or internal    │
│                 │ exact quote           │ status   │ exact quote              │
│                 │ normalized value      │ reason   │ normalized value         │
│                 │ locator · timestamp   │ mapping  │ locator · timestamp      │
│                 │ hash · source link    │ scope    │ hash · source link       │
│                 ├───────────────────────┴──────────┴─────────────────────────┤
│                 │ Neutral interpretation and evidence limitations           │
└─────────────────┴────────────────────────────────────────────────────────────┘
```

### Mobile

```text
┌───────────────────────────┐
│ ClickPe PIM   Run: partial│
├───────────────────────────┤
│ Product / field           │
│ ClickPe source quote      │
├─ stored decision ─────────┤
│ reason and mapping scope  │
├───────────────────────────┤
│ Comparison source quote   │
├───────────────────────────┤
│ Overview Reviews Products │
└───────────────────────────┘
```

## View requirements and copy

### Overview

- Open with the highest stored-priority review item that has two evidence sides. Use the evidence seam, not a large metric or decorative illustration.
- If no two-sided review exists, open with run health and the sentence “No two-source review item is available in this snapshot.”
- Present inventory, cohort, applicable official-source coverage, open review items, high-priority items, source failures, recent changes, and finalized runs as one status register.
- Use the persistent sentence: “Review items are not findings of error or wrongdoing.”

### Reviews

- Label the page “Review queue.”
- Filters use plain terms: “Field,” “Status,” “Severity,” and “Product.”
- The empty result says: “No review items match these filters. Clear filters to see the full queue.”
- Selecting a row opens a stable `/reviews/[comparisonId]` URL.
- The detail view displays stored status, reason, reason code, confidence, priority, severity, mapping rationale/scope, both evidence excerpts when present, normalized values, source URLs, locators, retrieval times, and SHA-256 values.
- Missing evidence is explicit: “This side has no stored observation for the selected comparison.”
- No review form or mutation control appears in the Vercel interface.

### Products

- The index is a searchable ledger of name, native product ID, category, provider display name, active state, observation count, and review count.
- Product detail groups observations by field without collapsing contradictory claims.
- “Unknown,” “Absent,” “Ambiguous,” “Unsupported,” and “Failed” remain separate labels.
- Entity roles and programme mappings are shown as relationships, not as a provider ranking.

### Changes

- Display stored changes in reverse chronological order.
- Separate first-observation baseline from verified change by using the stored event type and explanatory copy; never infer a removal from an absent row.
- If the snapshot has no history, say: “No stored historical change is available for this run.”

### Providers

- Show entity ID, role, programme count, product count, approved applicable source count, and open review count.
- State: “Roles and programmes stay separate. This view does not rank providers.”

## Accessibility and responsive floor

- Meet WCAG 2.2 AA contrast for text, controls, and focus indicators.
- Provide a skip link, one `h1` per route, semantic landmarks, real tables on wide screens, and labelled list equivalents on narrow screens.
- Every interactive element is reachable and operable by keyboard with a visible 2 px register-blue focus ring and 2 px offset.
- External source links state the destination in accessible text and use `rel="noreferrer noopener"`.
- At 390 px width, no critical value or control may require horizontal page scrolling. Wide evidence hashes may wrap anywhere.
- At 200% zoom, navigation and evidence remain usable.
- Respect `prefers-reduced-motion` and Windows high-contrast mode.

## Uniqueness review before implementation

The first draft risked three generic patterns:

1. A finance-blue KPI dashboard. It was revised to use a cool archival field, a continuous run register, and a comparison-first opening rather than metric cards.
2. A fashionable sans-plus-display-serif pairing. It was revised so serif has one semantic role only: verbatim source evidence. Headlines stay in Archivo.
3. A standard sidebar plus card grid. It was revised to use ledger rows and the evidence seam; borders encode source and decision boundaries rather than decorate containers.

The single bold idea is the evidence seam. Gradients, ornamental charts, floating glass panels, rounded SaaS cards, numbered decoration, uppercase eyebrows, monospace metadata labels, and appended arrow glyphs are excluded because they do not improve this product's reasoning trail.

## Vercel delivery model

- Build a static Next.js App Router site under `web/` and deploy the prebuilt output to Vercel.
- During a local build, a frontend-only preparation script opens a user-selected SQLite database in read-only/query-only mode, selects one explicit finalized run, strips non-public fields, and writes a temporary public view-model JSON file under `web/.cache/`.
- The Next.js build statically generates all routes from that public view model. The database itself is never copied into `public/`, `.next/static/`, `out/`, or `.vercel/output/`.
- A built-in synthetic UI fixture may be used for local development and protected preview deployment. It must show the persistent synthetic banner.
- Production deployment is allowed only from a finalized non-synthetic run and only after inspecting the generated static output for private values.
- Vercel linking, preview deployment, and production deployment are separate approval-gated external actions.

## Acceptance conditions

- Only `web/**` and new planning/design documentation change; the protected backend paths have identical Git object hashes before and after implementation.
- The overview, review queue/detail, product index/detail, change history, and provider views render from stored records.
- No UI code implements financial normalization, comparison, scoring, completeness, freshness, entity resolution, or monitoring decisions.
- Empty, partial, failed-source, ambiguous, one-sided, all-match, and synthetic states have explicit copy.
- Keyboard, automated accessibility, responsive, unit, static-build, and browser navigation checks pass.
- Screenshot critique is completed at 1440×1024, 768×1024, and 390×844 before deployment.
- A protected Vercel preview is reviewed before any production deployment.
