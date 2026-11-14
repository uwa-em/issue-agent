import json, os, time
import requests
from dotenv import load_dotenv
import tools

load_dotenv()
BASE_URL = os.environ["LLM_BASE_URL"].rstrip("/")
API_KEY = os.environ["LLM_API_KEY"]
MODEL = os.environ["LLM_MODEL"]
MAX_STEPS = 15

SYSTEM = ("You are a coding agent. Fix the issue in the repo. Explore first, "
          "make minimal edits, and run the tests to verify. When the tests pass, "
          "reply with a short summary and make no further tool calls.")

def call_llm(messages):
    for attempt in range(5):
        r = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"model": MODEL, "messages": messages, "tools": tools.SCHEMAS},
            timeout=120,
        )
        if r.status_code == 429:           # rate limited: wait and retry
            wait = 5 * (attempt + 1)
            print(f"rate limited, waiting {wait}s...")
            time.sleep(wait)
            continue
        if r.status_code != 200:
            raise RuntimeError(f"API error {r.status_code}: {r.text[:500]}")
        return r.json()["choices"][0]["message"]
    raise RuntimeError("Too many rate-limit retries")

def run(issue: str):
    messages = [{"role": "system", "content": SYSTEM},
                {"role": "user", "content": issue}]
    seen = {}
    for step in range(MAX_STEPS):
        msg = call_llm(messages)
        tool_calls = msg.get("tool_calls")
        assistant = {"role": "assistant", "content": msg.get("content") or ""}
        if tool_calls:
            assistant["tool_calls"] = tool_calls
        messages.append(assistant)

        if not tool_calls:
            print("\nDONE:", msg.get("content"))
            return {"steps": step + 1, "stopped": "model_done"}

        for call in tool_calls:
            name = call["function"]["name"]
            args = json.loads(call["function"].get("arguments") or "{}")
            key = (name, json.dumps(args, sort_keys=True))
            seen[key] = seen.get(key, 0) + 1
            if seen[key] >= 3:
                print("Stuck: same call repeated 3 times, stopping.")
                return {"steps": step + 1, "stopped": "repeat_loop"}
            print(f"[{step}] {name}({args})")
            try:
                result = tools.REGISTRY[name](**args)
            except Exception as e:
                result = f"ERROR: {e}"
            print(f"    -> {str(result)[:300]}")
            messages.append({"role": "tool", "tool_call_id": call["id"],
                             "content": str(result)})
            if name == "edit_file" and str(result) == "ok":
                seen.clear()
            if name == "run_tests" and str(result).startswith("ALL TESTS PASSED"):
                print("\nDONE: tests pass, stopping.")
                return {"steps": step + 1, "stopped": "tests_pass"}
    print("Hit max steps without finishing")
    return {"steps": MAX_STEPS, "stopped": "max_steps"}
if __name__ == "__main__":
    run("Login fails for users who type their email with capital letters. "
        "normalize_email should return a lowercase, trimmed email.")