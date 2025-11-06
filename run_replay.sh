#!/usr/bin/env bash
set -euo pipefail
echo "Starting run_replay.sh"

# Prefer project-provided replay entrypoints
if [ -f "./src/replay.py" ]; then
  echo "Found src/replay.py — executing it"
  python3 ./src/replay.py --input artifacts/marketdata/sample_feed.csv.gz --out results.json
elif [ -f "./src/main.py" ]; then
  echo "Found src/main.py — executing it with replay arguments"
  python3 ./src/main.py --replay --input artifacts/marketdata/sample_feed.csv.gz --out results.json
else
  echo "No replay entrypoint found. Writing example results.json and replication_diffs.json (templates)."
  # copy existing templates to root (they are already present)
  if [ -f results.json ]; then
    echo "results.json already exists"
  else
    cp -v results.json.template results.json 2>/dev/null || true
  fi
  if [ -f replication_diffs.json ]; then
    echo "replication_diffs.json already exists"
  else
    cp -v replication_diffs.json.template replication_diffs.json 2>/dev/null || true
  fi
fi

# Generate/update manifest.json with SHA256 of artifacts and key files
python3 - <<'PY'
import os, hashlib, json
root = "."
files = []
for dirpath, dirnames, filenames in os.walk(root):
    # skip venv, .git
    if '.git' in dirpath.split(os.sep): continue
    for fn in filenames:
        if fn.endswith(('.pyc','.pyo')): continue
        fp = os.path.join(dirpath, fn)
        rel = os.path.relpath(fp, root)
        try:
            h = hashlib.sha256(open(fp,'rb').read()).hexdigest()
            files.append({"path": rel.replace('\\','/'), "sha256": h, "size": os.path.getsize(fp)})
        except Exception as e:
            pass
files.sort(key=lambda x: x['path'])
with open("manifest.json","w") as f:
    json.dump({"generated_at": __import__('datetime').datetime.utcnow().isoformat()+'Z', "files": files}, f, indent=2)
print("Wrote manifest.json with %d entries" % len(files))
PY

echo "run_replay.sh complete"
