# Issue Agent

An autonomous coding agent that reads an issue, finds the bug, edits the code,
and verifies the fix by running the tests. It comes with a benchmark harness and
an MCP server, so the same tools also work inside Trae, Cursor, and Antigravity.

![demo](demo.gif)

## How it works

```
issue text ─► LLM ─► tool call ─► tools.py ─► result ─► LLM ─► ... ─► tests pass
```

- `agent/loop.py`: the agent loop. It calls any OpenAI-compatible API directly
  with `requests` (no SDK). It has a max-steps cap, a stop condition when tests
  pass, a repeated-call guard, and retry on rate limits.
- `agent/tools.py`: `list_files`, `read_file`, `search_code`, `edit_file`,
  `run_tests`. All paths are confined to the target repo, and the agent can't edit test files.
- `mcp_server.py`: a dependency-free MCP server (JSON-RPC over stdio) that exposes the same tools.
- `bench.py`: runs the agent on each case in a fresh temp copy, then re-runs the
  tests independently, so pass/fail never depends on the agent's own claim.

## Results

Model: `nvidia/nemotron-3.5-lightning:free` (free tier) · single run · <date>

| Case | What's wrong | Result | Steps | Time |
|---|---|---|---|---|
| case1_email | missing `.lower()` | PASS | 5 | 12.6s |
| case2_pagination | off-by-one on 1-indexed pages | PASS | 5 | 17.3s |
| case3_average | divide by zero on empty list | PASS | 5 | 19.0s |
| case4_palindrome | ignores case, spaces, punctuation | PASS | 6 | 19.2s |
| case5_wordcount | `split(" ")` miscounts spaces | PASS | 5 | 21.8s |
| case6_two_files | root cause in `pricing.py`, not `cart.py` | PASS | 7 | 34.0s |
| case7_vague | symptom-only issue (regex rejects `+`) | PASS | 5 | 13.6s |
| case8_traceback | traceback points at `report.py`, bug is in `data.py` | PASS | 7 | 18.4s |

**Solved 8/8** · average 5.6 steps and 19.5s per case.

Pass/fail is decided by `bench.py` re-running the tests itself in a fresh copy,
not by the agent's own claim. The agent can't edit test files.

**Caveats:** this is one run on a free model, so results vary between runs.
The cases are small hand-written bugs, so this shows the loop works, not general
ability on real repositories.

## Run it

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install requests python-dotenv pytest
copy .env.example .env      # then add your key
python make_cases.py
python make_cases_hard.py
python bench.py
```

`.env` needs `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` (any OpenAI-compatible endpoint with tool calling).

## Use the tools in your editor (MCP)

Add this to your editor's MCP config (Trae: MCP → Add → Manually):

```json
{
  "mcpServers": {
    "issue-agent-tools": {
      "command": "<path>/.venv/Scripts/python.exe",
      "args": ["<path>/mcp_server.py"],
      "env": { "TARGET_REPO": "<path to a repo to work on>" }
    }
  }
}
```

## Limitations

- The benchmark is 8 hand-written bugs, not SWE-bench. It shows the loop works;
  it doesn't measure general ability.
- Bugs are in small Python repos with pytest tests.
- Tests run on the host, with no sandbox yet.

## Roadmap

- [ ] `--repo` / `--issue` mode: clone from GitHub and open a PR
- [ ] Docker sandbox for running tests
- [ ] Dashboard replaying runs from `results.json`