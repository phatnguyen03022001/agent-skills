---
name: research
description: Use when an engineering decision depends on unknown, current, disputed, externally documented, or version-sensitive technical facts that should not be guessed.
---

# Research

Research exists to resolve a decision, not to accumulate links.

## Start with the decision

State the question the evidence must answer and what would change the engineering choice. Separate what is already known from what must be verified. If the target repository already contains authoritative evidence, read that before leaving the repository.

Use external research when facts are current, version-sensitive, unfamiliar, contested, security-sensitive, pricing/billing-related, or materially affect architecture.

## Source order

Prefer evidence in this order when available:

1. target-repository authority and source code;
2. official specifications and vendor documentation;
3. upstream source repositories, release notes, and reference implementations;
4. authoritative engineering or standards bodies;
5. strong secondary technical sources;
6. community discussion for experience signals, not unquestioned facts.

Do not promote search ranking, popularity, or repetition into authority.

## Evidence discipline

Label material claims as:

- **FACT**: directly supported by inspected evidence;
- **INFERENCE**: reasoned from facts, with the reasoning stated;
- **ASSUMPTION**: temporarily accepted but not verified;
- **UNKNOWN**: unresolved and potentially decision-relevant.

Check publication/version dates and distinguish the date a source was published from the date an event or behavior changed. Resolve conflicting sources by authority, freshness, scope, and directness. Quote sparingly; prefer precise paraphrase with citations.

Stop researching when the decision is supported well enough to act, remaining uncertainty is explicit, and additional sources are unlikely to change the choice.

Treat examples as evidence about behavior only when their version and conditions match the target. If documentation and source disagree, surface the disagreement instead of silently choosing the convenient answer.

## Boundaries

Do not use research as a substitute for inspecting the actual repository, running available tests, or measuring runtime behavior. Do not generate a decorative bibliography after the decision is already clear.

Use `reuse-first` when the question is whether an existing library, platform feature, protocol, or repository component should be adopted instead of building. Use `design-review` when the evidence is already known and the task is to judge architecture trade-offs.
