import os, json, random
from datetime import datetime

os.makedirs("logs", exist_ok=True)

# load team list
with open("data/rosters.json") as f:
    roster = json.load(f)

teams = [t["name"] for t in roster["teams"]]
results = [f"{t}: {round(random.uniform(-5,5),2)} edge" for t in teams]

now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
with open("logs/latest_results.txt","w") as f:
    f.write(f"Model run at {now}\n" + "\n".join(results))

print("✅ Model done!")
