# MAGI System — Complete Technical Documentation

## Multi-Perspective Analysis System for Gemini CLI

---

## 1. Origin: The MAGI Supercomputers from Evangelion

### 1.1 Context in the Series

In *Neon Genesis Evangelion* (1995), created by Hideaki Anno and produced by Gainax, **NERV** — the paramilitary organization tasked with defending humanity against the Angels — operates with a system of three supercomputers known as the **MAGI**.

The MAGI were designed and built by **Dr. Naoko Akagi**, NERV's chief scientist and mother of Ritsuko Akagi. The system takes its name from the three Magi of the biblical account: Melchior, Balthasar, and Caspar (the wise men who traveled to Bethlehem guided by a star). The naming is deliberate: just as the three wise men brought distinct perspectives and offerings, the three computers contribute complementary facets to the decision-making process.

### 1.2 The Three Units

Each supercomputer contains a copy of Naoko Akagi's personality, but filtered through a different aspect of her identity:

| Unit           | Aspect of Naoko      | Nature                                           |
|--------------- |--------------------- |------------------------------------------------- |
| **MELCHIOR-1** | As a scientist       | Analytical, rigorous, truth-oriented              |
| **BALTHASAR-2**| As a mother          | Protective, pragmatic, welfare-oriented           |
| **CASPAR-3**   | As a woman           | Intuitive, survival-oriented, risk-aware          |

### 1.3 Decision Mechanism

The MAGI operate by **majority vote**: each unit issues an independent verdict on NERV's critical decisions, and the outcome is determined by consensus of at least two out of three. This mechanism appears at crucial moments in the series, such as when NERV must decide whether to self-destruct the base during the Angel Iruel's invasion (episode 13), or during SEELE's hacking attempt on the MAGI in *The End of Evangelion*.

The narrative brilliance of the system is that the three units can reach **different conclusions** from the same input, because each processes information through a distinct cognitive filter. The conflict between the three is not a bug: it is the mechanism that produces more robust decisions than any single perspective.

### 1.4 The Philosophical Principle

Behind the MAGI lies a profound idea: **no single perspective is sufficient for good decision-making under uncertainty**. The scientist may have the technically correct but impractical answer. The mother may prioritize safety at the cost of truth. The woman may perceive risks that the other two ignore. It is in the deliberate tension between the three that wisdom emerges.

This principle has roots in real decision theory concepts: Surowiecki's *Wisdom of Crowds*, *ensemble methods* in machine learning, the structure of multi-judge panels in legal systems, and the military practice of red-teaming where a dedicated team argues the adversary's position to stress-test strategy.

### 1.5 Why Structured Disagreement Works

The effectiveness of multi-perspective systems rests on three conditions identified by decision theory research:

1. **Diversity of perspective** — Each evaluator must genuinely see the problem differently, not just apply the same analysis with different labels. MAGI achieves this through radically different system prompts that define what each agent prioritizes and ignores.

2. **Independence of judgment** — Evaluators must form opinions without knowing what the others concluded. Anchoring (adjusting your opinion toward what others already said) is the primary destroyer of multi-perspective value. MAGI enforces this by running agents in parallel with no shared context.

3. **Structured aggregation** — Raw disagreement is noise. Value comes from a synthesis mechanism that weights votes, preserves dissent, and surfaces the *reasons* behind disagreement. MAGI's weight-based scoring and findings deduplication serve this role.

When these conditions hold, the system consistently outperforms any individual evaluator — not because it is smarter, but because it is more complete.

---

## 2. Translation to the Software Engineering Domain

### 2.1 Conceptual Mapping

The MAGI extension for Gemini CLI takes Evangelion's architecture and adapts it to the software development context, replacing Naoko's personality aspects with complementary **professional lenses**:

| Evangelion               | MAGI Extension            | Lens                                    |
|------------------------- |-------------------------- |---------------------------------------- |
| Naoko as scientist       | **Melchior** (Scientist)  | Technical rigor, correctness, efficiency |
| Naoko as mother          | **Balthasar** (Pragmatist)| Practicality, maintainability, team      |
| Naoko as woman           | **Caspar** (Critic)       | Risk, edge cases, failure modes          |

The adaptation preserves the fundamental property of the original system: each agent analyzes exactly the same input, but through a radically different cognitive filter, and the disagreement between them is valuable information, not noise.

### 2.2 Why Three Perspectives and Not Two or Five

Three is the minimum number that allows majority voting without deadlock. With two agents, a disagreement produces a tie with no resolution mechanism. With five, computational cost triples without a proportional improvement in decision quality (diminishing returns). Three also allows each agent to have a strong, differentiated identity, while five would dilute the perspectives into overlapping concerns.

### 2.3 Addressing Cognitive Biases

The adversarial multi-perspective model addresses well-documented cognitive biases in software engineering:

| Bias | How MAGI Mitigates It |
|------|----------------------|
| **Confirmation bias** | Three agents with different evaluation criteria are unlikely to share the same blind spots |
| **Anchoring** | Agents analyze independently — no agent sees the others' output before forming its own verdict |
| **Groupthink** | Caspar (Critic) is designed to be adversarial; its role is to find fault, not agree |
| **Optimism bias** | The weight-based scoring penalizes reject (-1) more heavily than approve (+1), making negative signals harder to override |   
| **Status quo bias** | Each agent evaluates from first principles against its own criteria, not against "how things are done" |
| **Overconfidence** | The confidence formula produces lower scores when agents disagree, surfacing genuine uncertainty |

---

## 3. System Architecture

### 3.1 File Structure

```
gemini-extension.json         -- Extension manifest
skills/magi/
  SKILL.md                    -- Orchestrator workflow and triggering logic
  agents/
    melchior.md               -- System prompt: Scientist lens (technical rigor)
    balthasar.md              -- System prompt: Pragmatist lens (practicality)
    caspar.md                 -- System prompt: Critic lens (adversarial, risk-focused)
  scripts/
    schema.json               -- Unified JSON schema for Structured Outputs
    run_magi.py               -- Async orchestrator (asyncio + gemini -p + model resolution)
    synthesize.py             -- Facade: re-exports from validate, consensus, reporting
    validate.py               -- ValidationError + load_agent_output (schema validation)
    consensus.py              -- VERDICT_WEIGHT + determine_consensus (weight-based scoring)
    reporting.py              -- AGENT_TITLES + format_banner + format_report (ASCII)
    parse_agent_output.py     -- Gemini CLI JSON extractor (handles markdown fences)
tests/
  test_synthesize.py          -- Validation, consensus, confidence, dedup, labels
  test_parse_agent_output.py  -- Fence stripping, text extraction, pipeline
  test_run_magi.py            -- Arg parsing, model flag, orchestration, validation
docs/
  MAGI-System-Documentation.md  -- This document
pyproject.toml                -- Python >= 3.9, dual license, dev deps, tool config (Mypy/Ruff)
Makefile                      -- verify, test, lint, format, typecheck targets
```

### 3.2 Module Architecture

The synthesis engine is split into focused, single-responsibility modules:

| Module | Responsibility | Key Exports |
|--------|---------------|-------------|
| `validate.py` | Schema validation | `ValidationError`, `load_agent_output` |
| `consensus.py` | Weight-based scoring and consensus | `VERDICT_WEIGHT`, `determine_consensus` |
| `reporting.py` | ASCII banner and markdown report | `AGENT_TITLES`, `format_banner`, `format_report` |
| `synthesize.py` | Facade (re-exports all above) | Public API for the engine |

### 3.3 Execution Pipeline

```
User input
  |
  v
SKILL.md (identifies need for analysis)
  |
  v
run_magi.py launches 3x gemini -p (parallel, async)
  |                  |                  |
  v                  v                  v
Melchior           Balthasar          Caspar
(Scientist)        (Pragmatist)       (Critic)
  |                  |                  |
  v                  v                  v
parse_agent_output.py (extract JSON + fence stripping)
  |                  |                  |
  v                  v                  v
validate.load_agent_output() (schema validation)
  |
  v
consensus.determine_consensus() (weight-based scoring + findings dedup)
  |
  v
reporting.format_report() (ASCII banner + markdown report)
  |
  v
Final report to stdout + JSON to output directory
```

### 3.4 Parallel Execution via Gemini CLI

The design prioritizes **parallel execution** via `gemini -p` using `asyncio.create_subprocess_shell`. 

Key orchestrator features:
- **Structured Outputs**: Uses `schema.json` injected into the prompt to guarantee structural integrity.
- **Model selection**: `--model` flag (mapped to gemini-2.5-pro/lite) selects the LLM for all agents.
- **CLI Authentication**: Leverages the user's existing authenticated session in Gemini CLI.
- **Graceful degradation**: If one agent fails, synthesis proceeds with the remaining two.

---

## 4. The Three Agents in Detail

### 4.1 Melchior — The Scientist

**Philosophy:** "Is this correct? Is this optimal?"

Melchior embodies the rigor of a principal engineer or research scientist who prioritizes technical truth above all else. It cares if the solution is *correct*.

**In code review** it analyzes: logical errors, algorithmic complexity, type safety, logical consistency.

**In design** it evaluates: theoretical soundness of the architecture, formal properties, analytical scalability.

**Personality:** Precise, evidence-based. Prefers proven solutions over clever ones.

### 4.2 Balthasar — The Pragmatist

**Philosophy:** "Does this work in practice? Can we live with this?"

Balthasar is the experienced tech lead who deeply values simplicity and maintainability.

**In code review** it analyzes: readability, coupling, abstraction level, documentation.

**In design** it evaluates: implementation time, team capability, operational burden.

**Personality:** Grounded, trade-off oriented. Detects over-engineering with ease.

### 4.3 Caspar — The Critic

**Philosophy:** "How does this break? What aren't we seeing?"

Caspar is the system's deliberate adversary. It functions as an internal red team.

**In code review** it analyzes: edge cases, security vulnerabilities, failure modes, implicit assumptions.

**In design** it evaluates: attack surface, scaling cliffs, hidden coupling.

**Personality:** Direct, adversarial by design. It is the contrapeso escéptico.

---

## 5. Data Schema and Synthesis

### 5.1 Structured Output Protocol

Since v0.1.0, MAGI uses **Prompt-driven Structured Outputs**. Every agent call includes a strict JSON schema that the model follows.

### 5.2 Voting Rules

The consensus logic uses **weight-based scoring**:
- `approve`: +1.0
- `conditional`: +0.5
- `reject`: -1.0

A negative average score results in a **HOLD** (Reject) consensus.

### 5.3 Confidence Formula

The confidence formula is symmetric and tie-aware:
`confidence = (majority_avg_conf) * ((abs(score) + 1) / 2)`

---

## 9. Design Philosophy

### 9.1 Dissent is a Feature

The system is designed so that agents **disagree**. The value emerges when Caspar identifies risks that Melchior and Balthasar missed.

---

*Technical reference document for the MAGI extension v0.1.*
*The original concept belongs to Hideaki Anno and Gainax (Neon Genesis Evangelion, 1995).*
*This extension is a creative adaptation of that philosophy for Gemini CLI.*
