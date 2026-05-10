# MAGI — Multi-Perspective Analysis Extension for Gemini CLI

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](#license)

A Gemini CLI extension that implements a **multi-perspective analysis system** inspired by the [MAGI supercomputers](https://evangelion.fandom.com/wiki/Magi) from *Neon Genesis Evangelion*.

Three specialized AI agents independently analyze the same problem from complementary — and deliberately adversarial — perspectives, then synthesize their verdicts via weight-based majority vote.

---

## Why Three Adversarial Perspectives?

### The MAGI in Evangelion

In *Neon Genesis Evangelion* (1995, Hideaki Anno / Gainax), the MAGI are three supercomputers that govern Tokyo-3's critical decisions. Each embodies a different facet of their creator, Dr. Naoko Akagi: **Melchior** (the scientist), **Balthasar** (the mother), and **Caspar** (the woman). Decisions require consensus — no single perspective dominates.

### The Theory in Practice

The adversarial multi-perspective model addresses well-documented cognitive biases in software engineering:

| Bias | How MAGI Mitigates It |
|------|----------------------|
| **Confirmation bias** | Three agents with different evaluation criteria are unlikely to share the same blind spots |
| **Anchoring** | Agents analyze independently — no agent sees the others' output before forming its own verdict |
| **Groupthink** | Caspar (Critic) is designed to be adversarial; its role is to find fault, not agree |
| **Optimism bias** | The weight-based scoring penalizes reject (-1) more heavily than approve (+1), making negative signals harder to override |

The key insight is that **disagreement between agents is a feature, not a failure**. When Melchior (Scientist) approves but Caspar (Critic) rejects, the dissent surfaces a genuine tension between technical correctness and risk tolerance.

---

## Agents

| Agent | Codename | Lens | Personality |
|-------|----------|------|-------------|
| **Melchior** | Scientist | Technical rigor and correctness | Precise, evidence-based, favors proven solutions |
| **Balthasar** | Pragmatist | Practicality and maintainability | Grounded, trade-off oriented, advocates for the team |
| **Caspar** | Critic | Risk, edge cases, and failure modes | Adversarial by design, finds what others miss |

---

## Installation

### From GitHub

```bash
# 1. Clone the repository
git clone https://github.com/BolivarTech/MAGI-Gem.git

# 2. Install the extension
gemini skills install ./MAGI-Gem --scope workspace

# 3. Reload Gemini CLI skills
# Inside your interactive gemini session:
/skills reload
```

---

## Updating the Skill

If you pull new changes from the repository or modify the scripts/prompts, you need to tell Gemini CLI to reload the skill to apply the updates.

### 1. Reload Instructions
Inside your interactive Gemini CLI session, simply run:
```bash
/skills reload
```

### 2. Verify Installation
To confirm the skill is active and recognize the latest version:
```bash
/skills list
```

---

## Usage

Invoke with `gemini magi` or trigger the skill naturally:

```bash
gemini magi "review this code"
gemini "Give me three perspectives on this design"
```

### Modes

| Mode | When to Use | Example |
|------|-------------|---------|
| `code-review` | Reviewing code or diffs | "magi review this PR" |
| `design` | Evaluating architecture decisions | "magi analyze this migration plan" |
| `analysis` | General problem analysis, trade-offs | "magi should we use Redis or Postgres?" |

---

## How It Works

1. **Progressive Disclosure** — The `SKILL.md` identifies the need for deep analysis.
2. **Parallel Dispatch** — The orchestrator `run_magi.py` launches 3x `gemini -p` calls in parallel using your existing CLI authentication.
3. **Synthesis** — Agent outputs are validated, weighted, and synthesized into a final report.

---

## Project Structure

```
gemini-extension.json         -- Extension manifest
skills/magi/
  SKILL.md                    -- Skill entry point and workflow
  agents/                     -- Agent system prompts (.md)
  scripts/                    -- Core Python logic (consensus, reporting, etc.)
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Credits

The MAGI concept originates from *Neon Genesis Evangelion* (1995) by Hideaki Anno / Gainax. This extension is a creative adaptation of that decision-making philosophy for modern software engineering.
