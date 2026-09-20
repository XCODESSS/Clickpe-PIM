"use client";

import Link from "next/link";
import { useState } from "react";

import { formatField } from "@/lib/format";
import type { ProductView } from "@/lib/snapshot/types";

export function ProductLedger({ products }: { products: ProductView[] }) {
  const [query, setQuery] = useState("");
  const normalize = (value: string) => value
    .toLocaleLowerCase()
    .replace(/[_-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
  const needle = normalize(query);
  const visible = products.filter((product) => !needle || [
    product.name,
    product.productId,
    product.category,
    product.providerName ?? "",
  ].some((value) => normalize(value).includes(needle)));
  return (
    <section aria-labelledby="product-ledger-heading">
      <div className="product-search">
        <h2 id="product-ledger-heading">Stored products</h2>
        <label htmlFor="product-query">Search products</label>
        <input id="product-query" type="search" value={query} onChange={(event) => setQuery(event.target.value)} />
        <p className="result-count" aria-live="polite">{visible.length} {visible.length === 1 ? "product" : "products"}</p>
      </div>
      {visible.length === 0 ? (
        <p className="ledger-empty">No products match this search. Clear the search to see the full product list.</p>
      ) : (
        <div className="ledger-scroll">
          <table className="ledger-table product-ledger">
            <thead><tr><th>Product</th><th>Native ID</th><th>Category</th><th>Provider display</th><th>Active state</th><th>Observations</th><th>Reviews</th></tr></thead>
            <tbody>
              {visible.map((product) => (
                <tr key={product.productId}>
                  <th scope="row" data-label="Product"><Link href={`/products/${encodeURIComponent(product.productId)}/`}>{product.name}</Link></th>
                  <td data-label="Native ID">{product.productId}</td>
                  <td data-label="Category">{formatField(product.category)}</td>
                  <td data-label="Provider display">{product.providerName ?? "Unknown"}</td>
                  <td data-label="Active state">{formatField(product.activeStatus)}</td>
                  <td data-label="Observations">{product.observations.length}</td>
                  <td data-label="Reviews">{product.reviewCount}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
