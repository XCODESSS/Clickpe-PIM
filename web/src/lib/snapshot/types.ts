import { z } from "zod";

export const comparisonStatusSchema = z.enum([
  "MATCH",
  "DIFFERENT",
  "MISSING_CLICKPE",
  "MISSING_PROVIDER",
  "UNCOMPARABLE",
  "AMBIGUOUS",
]);

export const valueViewSchema = z.object({
  kind: z.string(),
  lower: z.string().nullable(),
  upper: z.string().nullable(),
  text: z.string().nullable(),
  boolean: z.boolean().nullable(),
  options: z.array(z.string()),
  unit: z.string().nullable(),
  period: z.string(),
  basis: z.string(),
  qualifier: z.string(),
  approximate: z.boolean(),
}).strict();

export const evidenceViewSchema = z.object({
  observationId: z.string().min(1),
  sourceId: z.string().min(1),
  sourceType: z.string().min(1),
  sourceUrl: z.string().nullable(),
  retrievedAt: z.string(),
  sha256: z.string().nullable(),
  field: z.string().min(1),
  state: z.enum(["present", "absent", "ambiguous", "unsupported", "failed"]),
  rawText: z.string(),
  locator: z.string(),
  context: z.string(),
  confidence: z.number().min(0).max(1),
  value: valueViewSchema.nullable(),
}).strict();

export const mappingViewSchema = z.object({
  role: z.string(),
  programme: z.string().nullable(),
  segment: z.string().nullable(),
  geography: z.string().nullable(),
  scope: z.string(),
  reviewState: z.string(),
  confidence: z.number().min(0).max(1),
  rationale: z.string(),
}).strict();

export const reviewViewSchema = z.object({
  comparisonId: z.string().min(1),
  fingerprint: z.string().nullable(),
  productId: z.string().min(1),
  productName: z.string().min(1),
  field: z.string().min(1),
  kind: z.string(),
  status: comparisonStatusSchema,
  reason: z.string(),
  reasonCode: z.string(),
  confidence: z.number().min(0).max(1),
  priority: z.number().nullable(),
  severity: z.string().nullable(),
  state: z.string().nullable(),
  mapping: mappingViewSchema.nullable(),
  left: evidenceViewSchema.nullable(),
  right: evidenceViewSchema.nullable(),
}).strict();

export const productViewSchema = z.object({
  productId: z.string().min(1),
  name: z.string().min(1),
  category: z.string(),
  providerName: z.string().nullable(),
  activeStatus: z.string(),
  clickpeUrl: z.string().nullable(),
  cohortMember: z.boolean(),
  observations: z.array(evidenceViewSchema),
  mappings: z.array(mappingViewSchema),
  reviewCount: z.number().int().nonnegative(),
}).strict();

export const publicSnapshotSchema = z.object({
  schemaVersion: z.literal(1),
  buildId: z.string().regex(/^[a-f0-9]{64}$/),
  run: z.object({
    runId: z.string().min(1),
    finishedAt: z.string().min(1),
    status: z.enum(["complete", "partial"]),
    synthetic: z.boolean(),
    catalogueComplete: z.boolean(),
  }).strict(),
  overview: z.object({
    inventoryProducts: z.number().int().nonnegative(),
    cohortProducts: z.number().int().nonnegative(),
    reviewItems: z.number().int().nonnegative(),
    highPriorityItems: z.number().int().nonnegative(),
    failedSources: z.number().int().nonnegative(),
    coverageNumerator: z.number().int().nonnegative(),
    coverageDenominator: z.number().int().nonnegative(),
    recentChanges: z.number().int().nonnegative(),
    finalizedRuns: z.number().int().nonnegative(),
  }).strict(),
  products: z.array(productViewSchema),
  reviews: z.array(reviewViewSchema),
  changes: z.array(z.object({
    changeId: z.string().min(1),
    productId: z.string().min(1),
    productName: z.string().min(1),
    sourceId: z.string().nullable(),
    field: z.string().nullable(),
    type: z.string(),
    detectedAt: z.string(),
  }).strict()),
  providers: z.array(z.object({
    entityId: z.string().min(1),
    role: z.string(),
    programmes: z.number().int().nonnegative(),
    products: z.number().int().nonnegative(),
    approvedSources: z.number().int().nonnegative(),
    openReviews: z.number().int().nonnegative(),
  }).strict()),
}).strict();

export type ComparisonStatus = z.infer<typeof comparisonStatusSchema>;
export type EvidenceView = z.infer<typeof evidenceViewSchema>;
export type MappingView = z.infer<typeof mappingViewSchema>;
export type ReviewView = z.infer<typeof reviewViewSchema>;
export type ProductView = z.infer<typeof productViewSchema>;
export type PublicSnapshot = z.infer<typeof publicSnapshotSchema>;
