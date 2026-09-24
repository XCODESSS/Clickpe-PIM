import type { EvidenceView } from "./snapshot/types";

export function formatField(value: string): string {
  if (!value) return "Unknown";
  return value
    .replaceAll("_", " ")
    .replace(/\b\w/g, (part) => part.toUpperCase());
}

export function formatTimestamp(value: string): string {
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return "Unknown time";
  return new Intl.DateTimeFormat("en-GB", {
    dateStyle: "medium",
    timeStyle: "short",
    timeZone: "Asia/Kolkata",
  }).format(parsed);
}

export function formatHash(value: string | null): string {
  return value ?? "Hash unavailable";
}

export function formatValue(evidence: EvidenceView): string {
  const value = evidence.value;
  if (!value) return formatField(evidence.state);
  if (value.text) return value.text;
  if (value.boolean !== null) return value.boolean ? "Yes" : "No";
  if (value.options.length) return value.options.join(", ");
  const bounds = [value.lower, value.upper].filter((part): part is string => part !== null);
  const joined = bounds.length === 2 ? `${bounds[0]}–${bounds[1]}` : bounds[0] ?? "Unknown";
  const qualifier = value.qualifier === "exact" || value.qualifier === "range"
    ? null
    : value.qualifier === "up_to" ? "Up to" : formatField(value.qualifier);
  return [value.approximate ? "Approximately" : null, qualifier, joined, value.unit, value.period !== "unknown" ? value.period : null]
    .filter(Boolean)
    .join(" ");
}
