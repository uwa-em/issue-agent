import json, os, subprocess, sys

env = dict(os.environ, TARGET_REPO=os.path.abspath("cases/case1_email/repo"))
p = subprocess.Popen([sys.executable, "mcp_server.py"], stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE, text=True, env=env)

def send(obj):
    p.stdin.write(json.dumps(obj) + "\n")
    p.stdin.flush()

def recv():
    return json.loads(p.stdout.readline())

send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
      "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                 "clientInfo": {"name": "test", "version": "0"}}})
print(recv()["result"]["serverInfo"])
send({"jsonrpc": "2.0", "method": "notifications/initialized"})
send({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
print([t["name"] for t in recv()["result"]["tools"]])
send({"jsonrpc": "2.0", "id": 3, "method": "tools/call",
      "params": {"name": "list_files", "arguments": {}}})
print(recv()["result"]["content"][0]["text"])
p.terminate()