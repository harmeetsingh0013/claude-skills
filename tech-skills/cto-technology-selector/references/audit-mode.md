# Audit mode — reviewing an existing stack, including gaps

Read this when the user hands you a document that describes technology **decisions already made** (an existing stack, an architecture doc that names real technologies already in production, a "here's what we're running" list) and wants it reviewed, challenged, or reconsidered — as opposed to a requirements/architecture doc meant to drive a *fresh* selection (that's `document-discovery.md`).

Signals this is audit mode: "review our current stack," "grill this," "what would you change here," "are we missing anything," "our traffic has grown, does this still hold up," or a document that reads as a decided architecture rather than a set of requirements.

Audit mode produces **three kinds of finding**, and they are not the same thing and should not be blended:

1. **Keep** — a decision that's still justified given current requirements and evidence.
2. **Revise or replace** — a decision that no longer fits (or never did), and should change.
3. **Add** — a capability the system now needs that the current stack doesn't have at all.

## Step 1: Build the current-state inventory

Read the document the same way `document-discovery.md` describes — don't trust filenames, cross-check for contradictions, note gaps. But the goal here is different: extract a clean inventory of *what's actually running today* — technology, version if stated, and what role it plays. If the document doesn't clearly state a decision's rationale (many don't — that's often exactly why someone wants an audit), don't invent one; note it as "rationale not documented" rather than guessing what the original reasoning must have been.

## Step 2: Find out what's changed

An audit is only meaningful relative to *current* requirements, which usually aren't identical to whatever justified the original decisions. Before evaluating anything, find out what's different now — traffic growth, new compliance requirements, a new integration, team changes, cost pressure, incidents that exposed a weakness. This is a short, targeted interview (same adaptive-depth principle as `interview-mode.md`): ask what prompted the audit and what's changed, rather than re-asking everything from scratch. If the user already told you (e.g. "traffic has grown and reads are slow"), don't ask again — that's your signal.

## Step 3: Evaluate each existing decision → Keep or Revise/Replace

Run every inventoried decision through the same six-dimension fit model in `evaluation-model.md`, but against *current* requirements, not the ones that (may have) justified it originally. Also apply current-state verification (`research-policy.md`) — a decision that was sound when made can be stale now (EOL approaching, a maintenance-mode project, a newer approach that closes a real gap).

Before recommending a replacement, run it through the existing-technology-constraints checklist in `disagreement-protocol.md` — what problem does the current tech actually cause, is it architectural/operational/organizational/preference, what would migration cost, is there a cheaper fix that doesn't require replacement. Working technology doesn't get replaced just because something newer exists; it gets replaced when there's a measurable, requirements-driven reason.

## Step 4: Find gaps → Add

This is the part a pure "review what's here" pass misses: **the most important finding in an audit is often something that isn't in the document at all.**

Look for capabilities the *current* requirements imply that the stack doesn't provide. The classic shape: traffic or load has grown since the original decisions were made, and a category of technology that was never needed before now is. A cache is the canonical example — an existing stack with no caching layer isn't a "replace X" finding, it's an "add Y" finding, and it needs a different justification than a replacement does:

- What specific symptom points at the gap? (rising read latency, repeated identical queries hitting the primary DB, a specific endpoint under load) — not "caching is generally good," but a concrete problem this system actually has now.
- Could the gap be closed *without* adding a new technology — query optimization, an index, vertical scaling, a read replica, adjusting the existing DB's own caching? The simplicity principle in `evaluation-model.md` applies exactly as it does for greenfield decisions: don't add a component because it's the expected next step, add it because the requirements now justify it and the cheaper options don't close the gap.
- If a new technology genuinely is the right answer, it still goes through the full six-dimension evaluation and needs alternatives considered — a "we need a cache" conclusion isn't a "therefore Redis" conclusion without asking why Redis specifically (in-memory vs. persistence needs, existing infra it needs to sit next to, team familiarity, operational cost of running one more stateful component) versus alternatives like Memcached, a CDN-layer cache, or the database's own caching/materialized views.
- Consider integration and operational fit with what's *already there* specifically — a new component in an audit isn't greenfield, it has to coexist with the existing stack's deployment model, observability setup, and the team that already operates it.

## Presenting the results

Conversationally (for a quick "does this still hold up" question) or as part of the final document (for a full re-evaluation) — either way, keep the three buckets visibly separate: what to keep, what to revise/replace, what to add. Each finding, in any bucket, carries the same "why" requirement as every other recommendation this skill makes (see SKILL.md) — a "Keep" finding needs a reason too, not just the changes.

If the user wants the audit turned into the final document, the same present → discuss → finalize gate in SKILL.md applies: present the three-bucket summary with reasoning first, invite cross-questions specifically on the revise/replace and add findings (those are where a user is most likely to push back), work through whatever comes up, and only then write the file.

When this feeds the final technology-stack document (`output-document.md`), add a short **Current-State Audit** section right after the executive summary, listing the three buckets at a glance, and give each *changed or added* decision its own full appendix entry per the standard format. "Keep" decisions can get a shorter appendix note (still with reasoning — "still fits: X, Y, Z" — but need not repeat the original vendor evaluation in full) unless the user specifically wants every kept decision re-justified from scratch.
