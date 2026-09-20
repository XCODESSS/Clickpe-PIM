import "server-only";

import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { publicSnapshotSchema, type PublicSnapshot } from "./types";

export function getSnapshot(): PublicSnapshot {
  const path = resolve(process.cwd(), ".cache", "public-snapshot.json");
  let payload: string;
  try {
    payload = readFileSync(path, "utf8");
  } catch {
    throw new Error("The public UI snapshot was not prepared.");
  }
  return publicSnapshotSchema.parse(JSON.parse(payload));
}
