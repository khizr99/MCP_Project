import requests, time, json

"""Helper: POST a workflow and poll GET /api/workflows/{id} several times printing responses."""

BASE = "http://localhost:8000"
body = {
    "name": "Validator Debug - negative credit",
    "description": "Debugging create_workflow response",
    "operation": "update",
    "target_customer_id": "CUST001",
    "parameters": {"credit_limit": -999}
}

r = requests.post(f"{BASE}/api/workflows", json=body)
print('POST status:', r.status_code)
print('POST body:', r.text)
if r.status_code != 200:
    raise SystemExit()
workflow_id = r.json().get('workflow_id')
print('workflow_id:', workflow_id)

for i in range(10):
    r2 = requests.get(f"{BASE}/api/workflows/{workflow_id}")
    print(f'GET attempt {i+1}:', r2.status_code)
    try:
        print('GET json:', json.dumps(r2.json(), indent=2))
    except Exception:
        print('GET text:', r2.text)
    if r2.status_code == 200:
        break
    time.sleep(0.5)
