# Project Overview: MAGI — Multi-Perspective Analysis for Gemini CLI

MAGI is a multi-perspective agent analysis system for Gemini CLI, inspired by the fictional MAGI supercomputers from *Neon Genesis Evangelion*. It allows the user to analyze code, designs, or complex decisions by dispatching three independent AI agents (Melchior, Balthasar, and Caspar) that evaluate the problem from different lenses (Technical Rigor, Pragmatism, and Critical Risk).

## Architecture

The project is structured as a Gemini CLI Extension/Skill.
- **Manifest:** `gemini-extension.json` defines the extension metadata and command contributions.
- **Skill:** `skills/magi/SKILL.md` is the entry point for the Gemini CLI, providing instructional context and triggering logic.
- **Agents:** `skills/magi/agents/` contains the system prompts (Markdown) for Melchior, Balthasar, and Caspar.
- **Orchestrator:** `skills/magi/scripts/run_magi.py` is an asynchronous Python script that manages the execution of the three agents in parallel using the `gemini` CLI in headless mode.
- **Logic:** `skills/magi/scripts/` contains the core business logic for:
  - `consensus.py`: Mathematical synthesis of agent verdicts using weight-based voting.
  - `validate.py`: Strict schema validation for agent JSON outputs.
  - `reporting.py`: Markdown report generation.
  - `parse_agent_output.py`: Extraction of JSON payloads from Gemini CLI responses.

## Tech Stack
- **Language:** Python 3.9+
- **CLI Engine:** Gemini CLI (used for agent calls and authentication)
- **Testing:** pytest with pytest-asyncio
- **Quality Tools:** Ruff (linting/formatting), Mypy (type checking)

## Building and Running

### Installation
To install the skill in the current workspace:
```bash
gemini skills install ./skills/magi --scope workspace
```
Then reload skills in your interactive session:
```bash
/skills reload
```

### Running Analysis
Analysis can be triggered via the `magi` command or naturally through the skill:
```bash
gemini magi code-review "path/to/file"
```

### Development Commands (Makefile)
- **Run tests:** `make test`
- **Lint code:** `make lint`
- **Format code:** `python -m ruff format .`
- **Type check:** `make typecheck`
- **Verify all:** `make verify`

## Development Conventions

1. **Async-First:** The orchestrator and subprocess management must be non-blocking using `asyncio`.
2. **Headless Integration:** Agent calls use `gemini -p "<prompt>" --output-format json -` to leverage the user's existing CLI authentication.
3. **Strict Validation:** Every agent response must be a valid JSON object matching the schema defined in `validate.py`. The orchestrator implements a one-time retry logic for malformed JSON.
4. **Consensus Math:** Verdicts are weighted: `approve` (+1.0), `conditional` (+0.5), `reject` (-1.0). A negative score results in a HOLD/REJECT consensus.
5. **Type Safety:** All Python code should include type hints and pass Mypy checks.
6. **Linting:** Code must be formatted using Ruff and follow PEP 8 standards (as enforced by the CI pipeline).
