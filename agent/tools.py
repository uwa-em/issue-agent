import subprocess
from pathlib import Path

REPO = (Path(__file__).resolve().parent.parent / "sandbox_repo")

def _safe(path: str) -> Path:
    p = (REPO / path).resolve()
    if not p.is_relative_to(REPO):
        raise ValueError("path outside repo")
    return p

def list_files() -> str:
    return "\n".join(str(p.relative_to(REPO)) for p in REPO.rglob("*.py"))

def read_file(path: str) -> str:
    return _safe(path).read_text()

def search_code(query: str) -> str:
    hits = []
    for p in REPO.rglob("*.py"):
        for i, line in enumerate(p.read_text().splitlines(), 1):
            if query.lower() in line.lower():
                hits.append(f"{p.relative_to(REPO)}:{i}: {line.strip()}")
    return "\n".join(hits[:20]) or "no matches"

def edit_file(path: str, old: str, new: str) -> str:
    p = _safe(path)
    text = p.read_text()
    if text.count(old) != 1:
        return f"ERROR: old text must appear exactly once (found {text.count(old)})"
    p.write_text(text.replace(old, new))
    return "ok"

def run_tests() -> str:
    r = subprocess.run(["python", "-m", "pytest", "-x", "-q"],
                       cwd=REPO, capture_output=True, text=True, timeout=60)
    return (r.stdout + r.stderr)[-2000:]

REGISTRY = {f.__name__: f for f in
            [list_files, read_file, search_code, edit_file, run_tests]}

def _schema(name, desc, props=None):
    props = props or {}
    return {"type": "function", "function": {
        "name": name, "description": desc,
        "parameters": {"type": "object",
                       "properties": {k: {"type": "string", "description": v}
                                      for k, v in props.items()},
                       "required": list(props)}}}

SCHEMAS = [
    _schema("list_files", "List all Python files in the repo"),
    _schema("read_file", "Read a file", {"path": "relative file path"}),
    _schema("search_code", "Case-insensitive text search across the repo",
            {"query": "text to find"}),
    _schema("edit_file", "Replace exact text in a file. 'old' must appear exactly once.",
            {"path": "relative file path", "old": "exact text to replace",
             "new": "replacement text"}),
    _schema("run_tests", "Run the test suite and return the output"),
]