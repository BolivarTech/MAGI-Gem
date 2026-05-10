# Plan: Final Verification of MAGI Orchestrator

## Objective

To conduct a final technical verification of the MAGI orchestrator, ensuring all fixes are in place and the system is technically sound, with a focus on rigor and correctness.

## Phase 1: Research and Exploration

This phase involves understanding the current state of the MAGI orchestrator and identifying potential areas for technical scrutiny.

1.  **Identify Core Components:**
    *   Determine the primary files and modules responsible for the MAGI orchestrator's functionality. Based on the project context, these are likely to include:
        *   `skills/magi/scripts/run_magi.py` (Orchestration logic)
        *   `skills/magi/scripts/validate.py` (Schema validation)
        *   `skills/magi/scripts/consensus.py` (Verdict synthesis)
        *   `skills/magi/scripts/parse_agent_output.py` (Output parsing)
    *   *Tool:* `list_directory` to confirm the existence and location of these files.

2.  **Understand "All Fixes":**
    *   Review the project's commit history or relevant issue tracker items (if accessible) to understand the specific bugs or issues that have been addressed. This context is crucial for verifying the effectiveness of the fixes.
    *   *Note:* In a real execution, this would involve `git log` or similar. In Plan Mode, we assume this context is understood or would be gathered.

3.  **Review Version Synchronization:**
    *   Identify files that contain version information (e.g., `pyproject.toml`, `gemini-extension.json`).
    *   Read the content of these files to extract version numbers.
    *   *Tool:* `read_file` for each version-defining file.
    *   *Verification:* Confirm that all version numbers are consistent.

## Phase 2: Technical Rigor and Correctness Analysis

This phase focuses on evaluating the code against principles of technical correctness and robustness.

1.  **Asynchronous Operations (`asyncio`):**
    *   Examine `run_magi.py` for proper `async`/`await` usage.
    *   Identify any instances of blocking I/O or synchronous calls within asynchronous functions that could hinder performance or stability.
    *   Check for potential race conditions or deadlocks in the parallel execution of agents.
    *   *Tool:* `read_file` to examine `skills/magi/scripts/run_magi.py`. Use `grep_search` for patterns like `time.sleep` (if not awaited), synchronous network calls, or incorrect task management.

2.  **Error Handling:**
    *   Scrutinize error handling mechanisms across all identified core components.
    *   Look for explicit `try-except` blocks that catch specific exceptions rather than bare `except:` clauses.
    *   Verify that failures in agent execution (e.g., `gemini` CLI errors), JSON parsing, or validation result in graceful degradation or informative error reporting.
    *   *Tool:* `read_file` on relevant Python files. `grep_search` for common error handling anti-patterns (e.g., `except Exception as e:`, bare `except:`).

3.  **Agent Interaction and Output Parsing:**
    *   Review the logic for constructing `gemini` CLI commands and parsing their JSON output.
    *   Ensure that the `--output-format json` flag is consistently used and that the JSON parsing is robust against malformed or unexpected output.
    *   Verify that the extracted data conforms to expected schemas (`skills/magi/scripts/validate.py`).
    *   *Tool:* `read_file` on `skills/magi/scripts/parse_agent_output.py` and relevant parts of `run_magi.py`.

## Phase 3: Test Coverage and Final Assessment

1.  **Test Suite Review:**
    *   Locate the test directory (e.g., `skills/magi/tests/`).
    *   List test files to understand the scope of existing tests.
    *   Examine the content of key test files (e.g., `test_run_magi.py`) to assess coverage of the orchestrator's functionality, including successful runs, error scenarios, and validation failures.
    *   *Tool:* `list_directory` for `skills/magi/tests/`. `read_file` for sample test files.

2.  **Synthesize Findings and Formulate Verdict:**
    *   Consolidate all observations from the analysis phases.
    *   Assign severity levels (critical, warning, info) to each finding.
    *   Determine an overall verdict: "approve", "conditional", or "reject" based on the technical rigor and correctness.
    *   Provide actionable recommendations for any required improvements.

3.  **Prepare Final Output:**
    *   Structure the findings, reasoning, and recommendation into the specified JSON format for the Melchior agent.

**Plan Filename:** `magi_orchestrator_verification_plan.md`
