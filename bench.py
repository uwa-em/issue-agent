import json, shutil, subprocess, sys, tempfile, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "agent"))
import tools, loop

def tests_pass(repo):
    r = subprocess.run([sys.executable, "-m", "pytest", "-q"], cwd=repo,
                       capture_output=True, text=True, timeout=60)
    return r.returncode == 0

results = []
only = sys.argv[1] if len(sys.argv) > 1 else None
for case in sorted((ROOT / "cases").iterdir()):
    if only and only not in case.name:
        continue
    issue = (case / "issue.txt").read_text().strip()
    work = Path(tempfile.mkdtemp()) / "repo"
    shutil.copytree(case / "repo", work)
    tools.REPO = work.resolve()          # point the agent at a fresh copy

    print(f"\n=== {case.name} ===")
    start = time.time()
    try:
        info = loop.run(issue)
    except Exception as e:
        info = {"steps": 0, "stopped": f"error: {e}"}
    results.append({"case": case.name,
                    "passed": tests_pass(work),   # verified independently of the agent
                    "steps": info["steps"], "stopped": info["stopped"],
                    "seconds": round(time.time() - start, 1)})
    time.sleep(3)                        # be gentle with free-tier limits

print("\n" + "=" * 60)
for r in results:
    print(f"{'PASS' if r['passed'] else 'FAIL'}  {r['case']:<20} "
          f"steps={r['steps']:<3} {r['seconds']}s  ({r['stopped']})")
print(f"\nSolved {sum(r['passed'] for r in results)}/{len(results)}")
Path("results.json").write_text(json.dumps(results, indent=2))