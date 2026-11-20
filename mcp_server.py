import json, os, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "agent"))
import tools

if os.environ.get("TARGET_REPO"):
    tools.REPO = Path(os.environ["TARGET_REPO"]).resolve()

sys.stdin.reconfigure(encoding="utf-8")
sys.stdout.reconfigure(encoding="utf-8")

# Reuse the schemas from tools.py, converted to MCP's format
MCP_TOOLS = [{"name": s["function"]["name"],
              "description": s["function"]["description"],
              "inputSchema": s["function"]["parameters"]}
             for s in tools.SCHEMAS]

def reply(msg_id, result=None, error=None):
    msg = {"jsonrpc": "2.0", "id": msg_id}
    if error:
        msg["error"] = error
    else:
        msg["result"] = result
    sys.stdout.write(json.dumps(msg) + "\n")
    sys.stdout.flush()

def handle(req):
    method, msg_id = req.get("method"), req.get("id")
    params = req.get("params") or {}
    if method == "initialize":
        reply(msg_id, {
            "protocolVersion": params.get("protocolVersion", "2024-11-05"),
            "capabilities": {"tools": {}},
            "serverInfo": {"name": "issue-agent-tools", "version": "0.1.0"}})
    elif method == "tools/list":
        reply(msg_id, {"tools": MCP_TOOLS})
    elif method == "tools/call":
        name, args = params.get("name"), params.get("arguments") or {}
        try:
            text, is_err = str(tools.REGISTRY[name](**args)), False
        except Exception as e:
            text, is_err = f"ERROR: {e}", True
        reply(msg_id, {"content": [{"type": "text", "text": text}],
                       "isError": is_err})
    elif method == "ping":
        reply(msg_id, {})
    elif msg_id is not None:
        reply(msg_id, error={"code": -32601, "message": f"Method not found: {method}"})
    # messages without an id are notifications and need no reply

for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        handle(json.loads(line))
    except Exception as e:
        print(f"server error: {e}", file=sys.stderr)   # never print to stdout