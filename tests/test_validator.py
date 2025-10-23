# tests/test_validator.py
import time
import requests

BASE = "http://localhost:8000"

def test_validator_blocks_negative_credit_limit():
    body = {
        "name": "Validator Unit Test - negative credit",
        "description": "Should be blocked by validator pre-exec",
        "operation": "update",
        "target_customer_id": "CUST001",
        "parameters": {"credit_limit": -999}
    }

    # create workflow
    r = requests.post(f"{BASE}/api/workflows", json=body)
    assert r.status_code == 200
    data = r.json()
    workflow_id = data["workflow_id"]

    # poll for terminal status
    for _ in range(15):
        r2 = requests.get(f"{BASE}/api/workflows/{workflow_id}")
        assert r2.status_code == 200
        w = r2.json()
        if w["status"] not in ["pending", "running"]:
            break
        time.sleep(0.5)

    # Check the validator task result
    assert w["status"] in ("failed", "completed", "failed")  # allow either but validator should have failed task
    current = w.get("current_task") or {}
    # Ensure validator ran and produced an invalid result
    assert current.get("agent_type") == "validator"
    result = current.get("result") or {}
    assert result.get("result", {}).get("valid") is False
    assert "credit_limit cannot be negative" in (result.get("result", {}).get("errors") or [])