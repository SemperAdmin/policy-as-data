// authority.ts
// Provenance layer. Given a citation identifier, walk the authority graph
// (data/maradmin-051-23.authority.jsonld) up to the root statute, so a decision
// can show where its rule's authority comes from.
//
// Pure and deterministic: every function takes the parsed graph as an argument.
// Nothing here reads disk or network.

import type { VerificationStatus } from "./types.ts";

/** One node of the authority @graph, normalized to a single upward edge. */
export interface AuthorityNode {
  id: string;
  type: string;
  label: string;
  /** The identifier this node draws authority from, if any. */
  parent?: string;
}

/** Parsed authority graph, keyed by identifier for O(1) lookup. */
export interface AuthorityGraph {
  byId: Map<string, AuthorityNode>;
}

/** Raw JSON-LD node shape (the subset this resolver reads). */
interface RawNode {
  "@id": string;
  "@type"?: string;
  label?: string;
  derivesAuthorityFrom?: string;
  partOf?: string;
}

/**
 * Normalize parsed JSON-LD into an AuthorityGraph. Each node's upward edge is
 * whichever of partOf (provision -> document) or derivesAuthorityFrom
 * (document -> issuing authority) is present.
 */
export function asAuthorityGraph(value: unknown): AuthorityGraph {
  const graph = (value as { "@graph"?: RawNode[] })?.["@graph"];
  if (!Array.isArray(graph)) {
    throw new Error("Authority data has no @graph array.");
  }
  const byId = new Map<string, AuthorityNode>();
  for (const node of graph) {
    byId.set(node["@id"], {
      id: node["@id"],
      type: node["@type"] ?? "pol:Unknown",
      label: node.label ?? node["@id"],
      parent: node.partOf ?? node.derivesAuthorityFrom,
    });
  }
  return { byId };
}

/**
 * Resolve the authority chain for a citation identifier, ordered root-first
 * (statute) to leaf (the cited provision).
 *
 * Returns an empty array when the identifier is not asserted in the graph —
 * for example an UNVERIFIED citation pointing at an UNCONFIRMED source line.
 * That empty result is meaningful: the system does not invent provenance it
 * cannot show.
 */
export function resolveAuthorityChain(
  graph: AuthorityGraph,
  identifier: string
): AuthorityNode[] {
  const chain: AuthorityNode[] = [];
  const seen = new Set<string>();
  let current: string | undefined = identifier;
  while (current && !seen.has(current)) {
    const node = graph.byId.get(current);
    if (!node) break;
    seen.add(current);
    chain.push(node);
    current = node.parent;
  }
  return chain.reverse();
}

/** Provenance attached to a citation: its chain and whether it resolved. */
export interface Provenance {
  identifier: string;
  status: VerificationStatus;
  chain: AuthorityNode[];
  /** True when the identifier resolves to at least one node in the graph. */
  asserted: boolean;
}

/** Build the provenance record for a single citation identifier. */
export function provenanceFor(
  graph: AuthorityGraph,
  identifier: string,
  status: VerificationStatus
): Provenance {
  const chain = resolveAuthorityChain(graph, identifier);
  return { identifier, status, chain, asserted: chain.length > 0 };
}
