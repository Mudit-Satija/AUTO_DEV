import requests, time, json
body = json.load(open("D:/projects/AUTO_DEV/_timer_body.json"))
start = time.time()
r = requests.post("http://localhost:8000/generate-from-srs", json=body, timeout=600)
t = time.time() - start
data = r.json()
print(f"Time: {t:.0f}s ({t/60:.1f} min)")
print(f"Files: {data['files_generated']}")
print(f"Validations pass: {data.get('all_validations_pass', 'N/A')}")
