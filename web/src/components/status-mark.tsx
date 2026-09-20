import { formatField } from "@/lib/format";

export function StatusMark({ value }: { value: string }) {
  const status = value.toLowerCase().replaceAll("_", "-");
  return <span className="status-mark" data-status={status}>{formatField(value)}</span>;
}
