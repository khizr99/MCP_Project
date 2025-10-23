import requests
import json

"""Simple helper: POST a workflow with a negative credit_limit and print the response."""

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
try:
    print('POST json:', json.dumps(r.json(), indent=2))
except Exception as e:
    print('POST text:', r.text)
