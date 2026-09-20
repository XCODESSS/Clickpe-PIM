"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { formatField } from "@/lib/format";
import type { ReviewView } from "@/lib/snapshot/types";

type FilterState = {
  field: string;
  status: string;
  severity: string;
  product: string;
};

const emptyFilters: FilterState = { field: "", status: "", severity: "", product: "" };

function initialFilters(): FilterState {
  if (typeof window === "undefined") return emptyFilters;
  const query = new URLSearchParams(window.location.search);
  return {
    field: query.get("field") ?? "",
    status: query.get("status") ?? "",
    severity: query.get("severity") ?? "",
    product: query.get("product") ?? "",
  };
}

function options(items: ReviewView[], key: "field" | "status" | "severity") {
  return [...new Set(items.map((item) => item[key]).filter((value): value is string => Boolean(value)))]
    .toSorted((left, right) => left.localeCompare(right));
}

export function ReviewLedger({ reviews }: { reviews: ReviewView[] }) {
  const [filters, setFilters] = useState<FilterState>(initialFilters);
  const products = useMemo(
    () => [...new Map(reviews.map((item) => [item.productId, item.productName])).entries()]
      .toSorted((left, right) => left[1].localeCompare(right[1])),
    [reviews],
  );
  const visible = reviews.filter((item) =>
    (!filters.field || item.field === filters.field)
    && (!filters.status || item.status === filters.status)
    && (!filters.severity || item.severity === filters.severity)
    && (!filters.product || item.productId === filters.product));

  function update(key: keyof FilterState, value: string) {
    const next = { ...filters, [key]: value };
    setFilters(next);
    const query = new URLSearchParams();
    for (const [name, selected] of Object.entries(next)) if (selected) query.set(name, selected);
    const suffix = query.size ? `?${query.toString()}` : window.location.pathname;
    window.history.replaceState(null, "", query.size ? suffix : window.location.pathname);
  }

  function clear() {
    setFilters(emptyFilters);
    window.history.replaceState(null, "", window.location.pathname);
  }

  return (
    <section aria-labelledby="review-ledger-heading">
      <div className="filter-register">
        <h2 id="review-ledger-heading">Stored review items</h2>
        <div className="filter-grid">
          <label>Field
            <select value={filters.field} onChange={(event) => update("field", event.target.value)}>
              <option value="">All fields</option>
              {options(reviews, "field").map((value) => <option key={value} value={value}>{formatField(value)}</option>)}
            </select>
          </label>
          <label>Status
            <select value={filters.status} onChange={(event) => update("status", event.target.value)}>
              <option value="">All statuses</option>
              {options(reviews, "status").map((value) => <option key={value} value={value}>{formatField(value)}</option>)}
            </select>
          </label>
          <label>Severity
            <select value={filters.severity} onChange={(event) => update("severity", event.target.value)}>
              <option value="">All severities</option>
              {options(reviews, "severity").map((value) => <option key={value} value={value}>{formatField(value)}</option>)}
            </select>
          </label>
          <label>Product
            <select value={filters.product} onChange={(event) => update("product", event.target.value)}>
              <option value="">All products</option>
              {products.map(([id, name]) => <option key={id} value={id}>{name}</option>)}
            </select>
          </label>
          <button type="button" onClick={clear}>Clear filters</button>
        </div>
        <p className="result-count" aria-live="polite">{visible.length} {visible.length === 1 ? "review item" : "review items"}</p>
      </div>
      {visible.length === 0 ? (
        <p className="ledger-empty">No review items match these filters. Clear filters to see the full queue.</p>
      ) : (
        <div className="ledger-scroll">
          <table className="ledger-table review-ledger">
            <thead><tr><th>Priority</th><th>Product</th><th>Field</th><th>Status</th><th>Severity</th><th>Stored reason</th></tr></thead>
            <tbody>
              {visible.map((item) => (
                <tr key={item.comparisonId}>
                  <td data-label="Priority">{item.priority ?? "Unknown"}</td>
                  <th scope="row" data-label="Product"><Link href={`/reviews/${encodeURIComponent(item.comparisonId)}/`}>{item.productName}</Link></th>
                  <td data-label="Field">{formatField(item.field)}</td>
                  <td data-label="Status">{formatField(item.status)}</td>
                  <td data-label="Severity">{item.severity ? formatField(item.severity) : "Unknown"}</td>
                  <td data-label="Stored reason">{item.reason.length > 110 ? `${item.reason.slice(0, 107)}…` : item.reason}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
