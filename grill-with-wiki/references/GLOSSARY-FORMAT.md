# Glossary Format (Wiki)

Terminology in the agent wiki replaces `CONTEXT.md`. Two homes — pick by scope.

## Per-domain language (L2)

Add or extend `## Language` in `domains/<name>.md`:

```md
## Language

**Order**:
A customer request to purchase one or more products, tracked from placement through fulfillment.
_Avoid_: Purchase, transaction

**Cancellation**:
Voiding an entire order before any line item has shipped.
_Avoid_: Refund, return, partial cancel
```

## Cross-cutting glossary index (L4)

Create `reference/glossary.md` lazily when a term spans domains:

```md
---
layer: L4
scope: canonical term index
read_when: [glossary, terminology, language, domain terms]
parent: 01_MAP.md
source: domains/
---

# Glossary

| Term | Definition | Domain | Avoid |
|------|------------|--------|-------|
| **Customer** | Person or org that places orders | [ordering](../domains/ordering.md) | Client, buyer, account |
| **User** | Authenticated login identity | [auth topic](../topics/auth-levels.md) | Account, member |
```

L4 is tables only — no prose paragraphs.

## Rules

- **Be opinionated.** Pick one canonical term; list synonyms under `_Avoid_` or the Avoid column.
- **Keep definitions tight.** One or two sentences. Define what it IS, not what it does.
- **Domain-specific only.** General programming concepts (timeouts, DTOs) don't belong unless the project gives them a special meaning.
- **No implementation.** Glossary is not a spec, scratch pad, or decision log.

## Single vs multi-domain wikis

- **Most wikis:** terms live in the owning L2 domain's `## Language`
- **Cross-cutting terms:** index row in `reference/glossary.md` pointing to the canonical domain
- **Routing:** use `01_MAP.md` domain router to infer which L2 file owns a term

When the owning domain is unclear, ask before writing.
