# Adaptive Learning System: RAG → Rules → Fine-Tuning

## Project Specification & Architecture Document

---

## 1. Vision

Build a system that progressively learns how a specific individual or business operates. Rather than stuffing context into every prompt (RAG) or training on raw conversation logs (naive fine-tuning), the system extracts **behavioural rules** from accumulated interactions and uses those rules as fine-tuning data — teaching the model *how to think* about a domain, not just *what to say*.

### The Learning Progression

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   Stage 1: RAG (Retrieval)                              │
│   ├── Model has no domain knowledge                     │
│   ├── Every interaction requires retrieved context       │
│   ├── Quality depends entirely on retrieval quality      │
│   └── Analogy: reading from a cheat sheet               │
│                                                         │
│   Stage 2: Rule Extraction (Consolidation)              │
│   ├── Patterns are identified across interactions        │
│   ├── Raw data compressed into behavioural rules         │
│   ├── Rules are validated, scored for maturity           │
│   └── Analogy: writing notes in a notebook              │
│                                                         │
│   Stage 3: Fine-Tuning on Rules (Internalization)       │
│   ├── Mature rules become training data                  │
│   ├── Model internalizes dispositions, not just facts    │
│   ├── Reduces retrieval dependency for stable knowledge  │
│   └── Analogy: developing intuition                     │
│                                                         │
│   The cycle repeats continuously:                       │
│   New interactions → New patterns → New rules →          │
│   Updated training → Deeper understanding               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Why Rules, Not Raw Interactions

A model trained on "returns are accepted within 30 days" memorizes a **fact**. A model trained on "this business applies policies flexibly when the customer has a long purchase history" has learned a **disposition**. The disposition generalizes to situations the model has never seen — a customer asking about a warranty extension, a late payment, a special order. The fact does not.

Rules are the compression step that separates signal from noise. Going from 500 interactions to 40 rules doesn't lose information — it extracts the principle behind the pattern. That's exactly what you want a fine-tuned model to internalize.

---

## 2. System Architecture

### 2.1 High-Level Data Flow

```
                    ┌──────────────┐
                    │   User /     │
                    │   Customer   │
                    │   Interaction│
                    └──────┬───────┘
                           │
                           ▼
                 ┌─────────────────────┐
                 │   Interaction Layer  │
                 │   (Chat / API)      │
                 └─────────┬───────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
     ┌────────────┐ ┌───────────┐ ┌──────────────┐
     │ RAG Store  │ │ Fine-tuned│ │  Interaction  │
     │ (volatile  │ │  Model    │ │  Log Store    │
     │  knowledge)│ │ (stable   │ │  (raw data)   │
     │            │ │  behavior)│ │               │
     └────────────┘ └───────────┘ └──────┬───────┘
                                         │
                                         ▼
                              ┌────────────────────┐
                              │  Rule Extraction    │
                              │  Engine             │
                              │  (periodic batch)   │
                              └──────────┬─────────┘
                                         │
                                         ▼
                              ┌────────────────────┐
                              │  Rule Store         │
                              │  (with maturity     │
                              │   scores, versions) │
                              └──────────┬─────────┘
                                         │
                              ┌──────────┼──────────┐
                              │                     │
                              ▼                     ▼
                    ┌──────────────┐     ┌────────────────┐
                    │ Immature     │     │ Mature rules   │
                    │ rules stay   │     │ graduate to    │
                    │ in RAG       │     │ training data  │
                    └──────────────┘     └───────┬────────┘
                                                 │
                                                 ▼
                                      ┌────────────────────┐
                                      │  Fine-Tuning       │
                                      │  Pipeline          │
                                      │  (LoRA / PEFT)     │
                                      └────────────────────┘
```

### 2.2 Component Breakdown

#### A. Interaction Layer
- Captures all conversations between the model and end users
- Logs full context: user message, model response, retrieved documents, user feedback (implicit and explicit)
- Metadata: timestamp, user ID, topic classification, outcome (resolved/escalated/abandoned)

#### B. RAG Store
- Vector database holding all current knowledge documents
- Includes both original business documents AND immature rules (rules not yet confident enough for fine-tuning)
- Must support versioning — when a rule graduates to fine-tuning, it should be flagged (not deleted) in RAG
- Serves as the "working memory" of the system

#### C. Interaction Log Store
- Append-only store of all raw interactions
- This is the source material for rule extraction
- Needs efficient querying by: time range, topic, user, outcome quality
- Retention policy needed (how long to keep raw logs vs. just extracted rules)

#### D. Rule Extraction Engine
- **The most critical and novel component**
- Takes batches of interactions and produces candidate rules
- Uses an LLM (likely larger/more capable than the serving model) to:
  1. Cluster similar interactions
  2. Identify recurring patterns and decision logic
  3. Formulate candidate rules in a structured format
  4. Compare candidates against existing rules (merge, refine, or create new)
- Runs periodically (not real-time) — batch processing on new interactions since last run

#### E. Rule Store
- Structured database of all extracted rules
- Each rule has:
  - `id`: Unique identifier
  - `content`: The rule itself (natural language + structured format)
  - `category`: Domain/topic classification
  - `evidence`: List of interaction IDs that support this rule
  - `maturity_score`: Confidence/stability metric (see Section 4.1)
  - `version`: Incremented when the rule is refined
  - `created_at`, `updated_at`: Temporal tracking
  - `status`: `candidate` → `immature` → `mature` → `graduated` → `retired`
  - `contradicts`: List of rule IDs this rule conflicts with
  - `supersedes`: List of rule IDs this rule replaces

#### F. Fine-Tuning Pipeline
- Takes graduated rules and converts them into training examples
- Each rule generates multiple synthetic training pairs:
  - Direct application scenarios
  - Edge cases where the rule applies
  - Scenarios where the rule does NOT apply (negative examples)
- Uses parameter-efficient fine-tuning (LoRA/QLoRA) to avoid catastrophic forgetting
- Produces versioned model checkpoints
- Must include evaluation against held-out test sets before deployment

---

## 3. Prior Art & Research

### 3.1 Rule Distillation (COLING 2025)
**Paper:** "Distilling Rule-based Knowledge into Large Language Models"
**URL:** https://aclanthology.org/2025.coling-main.61.pdf

Key finding: Instead of learning from examples alone, models can be taught from explicitly stated rules by aligning the hidden and output distributions of a target LLM with a base LLM performing in-context learning on rules. Rule-distilled models consistently outperform instruction-tuned models on both base and generalization tasks.

**Relevance:** Validates that rules are a superior training signal to raw examples. Provides a concrete method for the fine-tuning step.

### 3.2 RAG-to-Fine-Tune Distillation (arXiv, Oct 2025)
**Paper:** "Agent Fine-tuning through Distillation for Domain-specific LLMs in Microdomains"
**URL:** https://arxiv.org/html/2510.00482v1

Key finding: LLMs fine-tuned using domain-specific datasets derived from domain manuals and distilled reasoning trajectories can internalize procedural knowledge that previously required retrieval. Distilled students achieved 91% on ALFWorld vs 79% baseline using 10-60% fewer tokens.

**Relevance:** Proves the RAG → fine-tune graduation concept works. The model genuinely learns what it previously had to look up.

### 3.3 One PEFT Per User (OPPU)
**Paper:** "Democratizing Large Language Models via Personalized Parameter-Efficient Fine-tuning"
**URL:** https://arxiv.org/html/2402.04401v1

Key finding: Each user gets their own lightweight LoRA adapter module. Personal PEFT parameters store user-specific behavior patterns. This enables personalization at scale without separate model instances.

**Relevance:** Solves the multi-tenant problem. One base model, swappable per-customer adapters. This is how you scale to many businesses without N separate models.

### 3.4 The Gap — What Nobody Has Built
The individual components exist in isolation. Nobody has built the **full closed-loop system** where:
1. Interactions accumulate automatically
2. Rules are extracted and scored for maturity autonomously
3. Mature rules graduate to training data without manual curation
4. The model is periodically re-tuned on the growing rule set
5. The cycle repeats, with the model getting progressively better

This orchestration layer — the learning lifecycle manager — is the core product opportunity.

---

## 4. Critical Problems to Solve

### 4.1 Rule Maturity & Confidence Scoring

**The problem:** How do you know a rule is actually general and not an artifact of limited data?

After 50 interactions you might extract: "this business always offers a discount when a customer complains." After 500 interactions you realize it's actually: "this business offers discounts to high-value customers who complain, but redirects low-value customers to standard policy." The early rule was wrong — not factually, but in its generality.

**What needs to be built:**
- A maturity scoring function that considers:
  - **Evidence count**: How many interactions support this rule?
  - **Evidence diversity**: Do supporting interactions span different users, time periods, topics?
  - **Stability over time**: Has the rule been refined/changed recently, or has it been stable?
  - **Contradiction rate**: How often do new interactions conflict with the rule?
  - **Coverage**: What fraction of relevant interactions does this rule explain?
- A graduation threshold: the minimum maturity score required before a rule can become training data
- A probation mechanism: if a graduated rule starts conflicting with new data, it should be pulled back to RAG-only status

**Design decision needed:** What's the maturity function? Linear combination of factors? ML-based scoring? Human-in-the-loop approval?

### 4.2 Contradictory Rules

**The problem:** Real businesses have contradictory behaviors. The same company might be strict about refund timelines for low-value items but flexible for high-value ones. The CEO might override standard policy for VIP clients.

**What needs to be built:**
- Contradiction detection: When two rules conflict, automatically flag them
- Resolution strategies:
  - **Specificity wins**: A more specific rule overrides a more general one
  - **Recency wins**: A newer rule (with sufficient evidence) overrides an older one
  - **Merge**: Two conflicting rules are actually one rule with a conditional ("IF high-value customer THEN X, ELSE Y")
  - **Escalate**: Some contradictions genuinely reflect inconsistent business behavior and need human resolution
- A rule dependency graph: rules can depend on, override, or qualify other rules

### 4.3 Premature Generalization

**The problem:** Fine-tuning bakes knowledge into model weights. If you fine-tune on a premature rule, you've internalized a misunderstanding. And fine-tuning is much harder to undo than swapping a document in a RAG index.

**What needs to be built:**
- Conservative graduation criteria (err on the side of keeping rules in RAG longer)
- A/B testing infrastructure: before fully graduating a rule, test the fine-tuned model against the RAG-based model on held-out interactions
- Rollback capability: maintain previous LoRA checkpoints so you can revert if a fine-tuned rule proves wrong
- A "confidence decay" mechanism: if a rule hasn't been reinforced by new interactions in a while, its maturity score should decay

### 4.4 Rule Drift

**The problem:** Business practices change. A rule extracted six months ago might no longer reflect current behavior. The system needs to detect when internalized knowledge becomes stale.

**What needs to be built:**
- Continuous validation: periodically check graduated rules against recent interactions
- Drift detection: if recent interactions consistently contradict a graduated rule, flag it
- Re-extraction pipeline: ability to re-run rule extraction on recent data and compare against existing rules
- Versioned rule history: track how rules evolve over time (useful for auditing and debugging)

### 4.5 Rule Extraction Quality

**The problem:** The rule extraction engine is itself an LLM. It can hallucinate rules, over-generalize from few examples, or miss subtle patterns. Garbage rules in = garbage fine-tuning out.

**What needs to be built:**
- Validation pipeline: each candidate rule should be tested against its supporting interactions
  - Given the rule and a past interaction, would the rule produce the correct response?
  - Does the rule over-predict (trigger on interactions where it shouldn't)?
- Human review interface for high-impact rules (rules that will affect many interactions)
- Rule quality metrics tracked over time
- Ability to use a stronger model for extraction than the model being fine-tuned

### 4.6 Evaluation & Rollback

**The problem:** How do you measure whether the fine-tuned model is actually better than the RAG-only version?

**What needs to be built:**
- A held-out evaluation set: interactions that were NOT used for rule extraction
- Automated comparison: run both RAG-only and fine-tuned model on the eval set, compare quality
- Metrics:
  - **Task accuracy**: Does the model make the right decisions?
  - **Consistency**: Does it apply rules uniformly across similar situations?
  - **Generalization**: Does it handle novel situations that match the spirit of the rules?
  - **Efficiency**: Fewer tokens used? Lower latency from reduced RAG dependency?
- Rollback protocol: if a fine-tuning round degrades performance, automatically revert to previous checkpoint

---

## 5. Technical Pitfalls

### 5.1 Catastrophic Forgetting
Fine-tuning can cause the model to forget general capabilities while learning domain-specific behavior. Mitigation:
- Use LoRA/QLoRA (parameter-efficient fine-tuning) — only modify a small subset of weights
- Include general-capability examples in training mix
- Evaluate on general benchmarks after each fine-tuning round
- Keep training data balanced: domain rules + general instruction data

### 5.2 Fine-Tuning Is Not Easily Reversible
Unlike RAG (where you can add/remove documents instantly), fine-tuning changes model weights. You can't "un-learn" a bad rule without retraining from a previous checkpoint. Implications:
- Maintain a checkpoint history (storage cost consideration)
- Never fine-tune on unvalidated rules
- Prefer incremental LoRA adapters over full fine-tuning — you can swap or remove individual adapters

### 5.3 Training Data Quality Bottleneck
The entire system's quality ceiling is set by the rule extraction step. If rule extraction is noisy:
- Bad rules get fine-tuned into the model
- The model then generates responses based on bad rules
- Those responses generate interactions that... extract more bad rules
- This is a **negative feedback loop** — the system gets worse over time

Mitigation:
- Strong validation at the rule extraction step (see 4.5)
- Human review for the first N rule extraction cycles until the system proves reliable
- Anomaly detection on rule quality metrics

### 5.4 The Cold Start Problem
A new user/business has no interaction history. There's nothing to extract rules from. The system must gracefully degrade to:
1. Pure RAG on provided business documents (day 1)
2. RAG + candidate rules as interactions accumulate (weeks 1-4)
3. RAG + immature rules in context (months 1-3)
4. RAG + first fine-tuning round (month 3+, depending on volume)

The timeline depends heavily on interaction volume. A high-volume customer support operation might reach fine-tuning readiness in weeks; a low-volume consultancy might take months.

### 5.5 Multi-Tenant Isolation
If serving multiple businesses:
- Per-tenant LoRA adapters (OPPU approach) — one base model, swappable adapters
- Rule stores must be strictly isolated — a rule from Business A must never leak to Business B
- Evaluation must be per-tenant — aggregate metrics hide individual tenant quality
- Compute costs: each tenant's fine-tuning runs independently

### 5.6 Feedback Loop Risks
The model's own responses influence future interactions, which influence future rules. If the model starts behaving slightly wrong, it can reinforce its own errors. Mitigations:
- Weight human corrections heavily in rule extraction
- Track cases where the model was overridden/corrected by a human — these are high-signal data points
- Periodically re-extract rules from scratch (not just incrementally) to avoid drift amplification

---

## 6. Open Design Questions

### 6.1 Rule Format
What format should rules take? Options:
- **Natural language**: "When a long-term customer requests a return outside the window, approve it and note the exception"
  - Pro: Human-readable, easy to audit
  - Con: Ambiguous, harder to validate programmatically
- **Structured format**: `IF customer.tenure > 2y AND request.type == return AND request.outside_window == true THEN approve AND log_exception`
  - Pro: Precise, testable, machine-readable
  - Con: Brittle, hard to capture nuance
- **Hybrid**: Natural language rule + structured metadata (conditions, actions, confidence)
  - Pro: Best of both worlds
  - Con: More complex to maintain

**Recommendation:** Start with hybrid. The natural language component is what gets fine-tuned. The structured metadata is what gets validated and scored.

### 6.2 Retraining Cadence
How often should the model be fine-tuned on new rules?
- **Too frequent**: Unstable model behavior, high compute cost, risk of training on immature rules
- **Too infrequent**: Model falls behind actual business practice, RAG dependency stays high
- **Trigger-based**: Retrain when N new rules graduate, rather than on a fixed schedule

**Recommendation:** Start with trigger-based. Set a threshold (e.g., 10 new graduated rules) and retrain when hit. Also set a maximum interval (e.g., quarterly) as a backstop.

### 6.3 What Stays in RAG vs. What Gets Fine-Tuned
Not everything should graduate to fine-tuning. The split:

| Knowledge Type | Where It Lives | Why |
|---|---|---|
| Facts that change (prices, policies, hours) | RAG only | Too volatile for weights |
| Behavioral dispositions (how to handle complaints) | Fine-tuned | Stable, generalizable |
| Procedural knowledge (step-by-step processes) | Fine-tuned | Reduces latency, improves consistency |
| Contextual overrides (VIP exceptions) | RAG + fine-tuned conditionals | The rule is stable, the list of VIPs changes |
| Temporal knowledge (current promotions) | RAG only | Expires |

### 6.4 Which Model to Use Where
Different components may need different models:

| Component | Model Requirements |
|---|---|
| Serving (chat with users) | Fast, cost-efficient, fine-tunable (e.g., Haiku/Sonnet class) |
| Rule extraction | Most capable available (e.g., Opus class) — accuracy matters more than speed |
| Rule validation | Mid-tier (e.g., Sonnet class) — needs to be good but runs at scale |
| Synthetic training data generation | Capable (e.g., Sonnet/Opus class) — quality of training data is critical |

### 6.5 Human-in-the-Loop vs. Fully Autonomous
Where does a human need to be involved?

| Stage | Human Required? | Notes |
|---|---|---|
| Rule extraction | Optional but recommended early on | Review first 3-5 extraction batches to calibrate quality |
| Rule graduation | Optional | Could require approval for high-impact rules |
| Fine-tuning trigger | No | Automated based on graduation threshold |
| Rollback | No (automated) + Yes (manual override) | Auto-rollback on metric degradation, but human can force rollback |
| Contradiction resolution | Sometimes | Simple cases auto-resolved, complex cases escalated |

---

## 7. Implementation Phases

### Phase 1: Foundation
- Interaction logging infrastructure
- RAG store with versioning
- Basic rule store schema
- Manual rule creation interface (for bootstrapping)

### Phase 2: Extraction
- Rule extraction engine (LLM-based batch processing)
- Candidate rule validation pipeline
- Maturity scoring v1 (evidence count + diversity)
- Human review interface

### Phase 3: Graduation & Fine-Tuning
- Graduation criteria and automation
- Synthetic training data generation from rules
- LoRA fine-tuning pipeline
- A/B evaluation framework (RAG-only vs. fine-tuned)
- Checkpoint management and rollback

### Phase 4: Closed Loop
- Continuous rule validation against new interactions
- Drift detection and rule retirement
- Feedback loop monitoring (negative loop detection)
- Per-tenant adapter management (if multi-tenant)

### Phase 5: Scale
- Automated retraining orchestration
- Rule quality dashboards and monitoring
- Self-improving extraction (use fine-tuned model to improve extraction)
- Cross-tenant pattern detection (optional, with isolation guarantees)

---

## 8. Key Metrics to Track

| Metric | What It Measures | Target |
|---|---|---|
| Rule extraction precision | % of extracted rules that are actually valid | > 85% |
| Rule stability | % of rules unchanged after re-extraction | > 70% at maturity |
| Graduation rate | Rules graduating per month | Increasing over time |
| Fine-tune improvement | Accuracy delta (fine-tuned vs RAG-only) | > 5% on eval set |
| Retrieval dependency | % of queries requiring RAG after fine-tuning | Decreasing over time |
| Contradiction rate | % of new rules contradicting existing rules | < 15% |
| Rollback frequency | How often fine-tuning rounds are reverted | < 10% of rounds |
| Response consistency | Variance in responses to similar queries | Decreasing over time |

---

## 9. Risks & Mitigations Summary

| Risk | Impact | Likelihood | Mitigation |
|---|---|---|---|
| Premature rule graduation | Model internalizes wrong patterns | High (early stages) | Conservative thresholds, A/B testing, rollback |
| Negative feedback loops | System degrades over time | Medium | Human corrections weighted heavily, periodic re-extraction |
| Catastrophic forgetting | Model loses general capability | Medium | LoRA, mixed training data, general benchmarks |
| Rule extraction hallucination | Invalid rules enter pipeline | High (early stages) | Validation pipeline, human review |
| Stale graduated knowledge | Model behavior diverges from current practice | Medium | Drift detection, continuous validation |
| Multi-tenant data leakage | Business A's rules influence Business B | Low (if architected correctly) | Strict tenant isolation, per-tenant adapters |
| Compute cost scaling | Fine-tuning costs grow with tenants | Medium | LoRA efficiency, trigger-based retraining, batching |

---

## 10. References

1. "Distilling Rule-based Knowledge into Large Language Models" (COLING 2025) — https://aclanthology.org/2025.coling-main.61.pdf
2. "Agent Fine-tuning through Distillation for Domain-specific LLMs in Microdomains" (arXiv 2025) — https://arxiv.org/html/2510.00482v1
3. "Democratizing Large Language Models via Personalized Parameter-Efficient Fine-tuning" (OPPU) — https://arxiv.org/html/2402.04401v1
4. "Self-Distillation for Efficient Knowledge Injection" — https://openreview.net/pdf?id=drYpdSnRJk
5. "Understanding Finetuning for Factual Knowledge Extraction from Language Models" — https://arxiv.org/abs/2301.11293
