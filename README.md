# MAGI — Multi-Perspective Analysis Extension for Gemini CLI

[![Verify](https://github.com/BolivarTech/MAGI-Gem/actions/workflows/verify.yml/badge.svg)](https://github.com/BolivarTech/MAGI-Gem/actions/workflows/verify.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-16%20passing-brightgreen.svg)](#tests)
[![Ruff](https://img.shields.io/badge/linter-ruff-orange.svg)](https://docs.astral.sh/ruff/)
[![License](https://img.shields.io/badge/license-MIT%20OR%20Apache--2.0-blue.svg)](#license)

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

### Official Method (Recommended)

Install the extension directly from the official repository with auto-updates enabled:

```powershell
gemini extensions install https://github.com/BolivarTech/MAGI-Gem.git --consent --auto-update
```

### Development Method

If you want to contribute or modify the extension:

```powershell
git clone https://github.com/BolivarTech/MAGI-Gem.git
cd MAGI-Gem
gemini extensions install . --consent
```

---

## Updating

To update the extension to the latest version (e.g., v0.1.9) from the official repository:

```powershell
gemini extensions update magi
```

If you are using the **Development Method**, just pull the latest changes and reinstall:
```powershell
git pull origin main
gemini extensions uninstall magi
gemini extensions install . --consent
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
