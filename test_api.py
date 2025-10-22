"""
API Testing Script
Simple script to test the MCP Multi-Agent Orchestration API
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"


def print_section(title):
    """Print a section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def test_health_check():
    """Test health check endpoint"""
    print_section("Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")


def test_list_customers():
    """Test listing customers"""
    print_section("List Customers")
    
    response = requests.get(f"{BASE_URL}/api/customers?limit=5")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        customers = response.json()
        print(f"Found {len(customers)} customers")
        for customer in customers[:3]:
            print(f"  - {customer['mcp_id']}: {customer['customer_name']}")
        return customers[0]['mcp_id'] if customers else None
    return None


def test_get_customer(customer_id):
    """Test getting a specific customer"""
    print_section(f"Get Customer: {customer_id}")
    
    response = requests.get(f"{BASE_URL}/api/customers/{customer_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        customer = response.json()
        print(f"Customer: {customer['customer_name']}")
        print(f"Email: {customer['email']}")
        print(f"Status: {customer['status']}")
        print(f"Subscription: {customer['subscription_plan']}")
        print(f"Credit Limit: ${customer['credit_limit']:,.2f}")
    else:
        print(f"Error: {response.text}")


def test_create_workflow(customer_id):
    """Test creating a workflow"""
    print_section("Create Workflow")
    
    workflow_data = {
        "name": "Test Update Customer Subscription",
        "description": "Upgrade customer subscription as a test",
        "operation": "update",
        "target_customer_id": customer_id,
        "parameters": {
            "subscription_plan": "Premium",
            "credit_limit": 75000
        }
    }
    
    print(f"Creating workflow for customer: {customer_id}")
    print(f"Request: {json.dumps(workflow_data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/api/workflows", json=workflow_data)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        workflow = response.json()
        print(f"Workflow created: {workflow['workflow_id']}")
        print(f"Status: {workflow['status']}")
        print(f"Message: {workflow['message']}")
        return workflow['workflow_id']
    else:
        print(f"Error: {response.text}")
        return None


def test_workflow_status(workflow_id):
    """Test getting workflow status"""
    print_section(f"Workflow Status: {workflow_id}")
    
    # Wait a moment for workflow to process
    time.sleep(2)
    
    response = requests.get(f"{BASE_URL}/api/workflows/{workflow_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        workflow = response.json()
        print(f"Workflow ID: {workflow['workflow_id']}")
        print(f"Status: {workflow['status']}")
        print(f"Progress: {workflow['progress']:.1f}%")
        
        if workflow.get('current_task'):
            task = workflow['current_task']
            print(f"\nCurrent Task:")
            print(f"  - Description: {task['description']}")
            print(f"  - Status: {task['status']}")
    else:
        print(f"Error: {response.text}")


def test_list_workflows():
    """Test listing all workflows"""
    print_section("List All Workflows")
    
    response = requests.get(f"{BASE_URL}/api/workflows")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        workflows = response.json()
        print(f"Total workflows: {len(workflows)}")
        for wf in workflows[:5]:
            print(f"\n  Workflow: {wf['workflow_id']}")
            print(f"    Name: {wf['name']}")
            print(f"    Status: {wf['status']}")
            print(f"    Progress: {wf['tasks_completed']}/{wf['tasks_total']} tasks")


def test_agent_status():
    """Test getting agent status"""
    print_section("Agent Status")
    
    response = requests.get(f"{BASE_URL}/api/agents/status")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        agents = response.json()
        for agent_type, info in agents.items():
            print(f"\n{agent_type.upper()} Agent:")
            print(f"  ID: {info['agent_id']}")
            print(f"  Type: {info['type']}")
            print(f"  Status: {info['status']}")


def test_quick_upgrade(customer_id):
    """Test quick upgrade endpoint"""
    print_section("Quick Upgrade")
    
    response = requests.post(
        f"{BASE_URL}/api/customers/{customer_id}/upgrade",
        params={"subscription_plan": "Premium"}
    )
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"Workflow created: {result['workflow_id']}")
        return result['workflow_id']
    else:
        print(f"Error: {response.text}")
        return None


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "MCP Multi-Agent Orchestration - API Tests" + " " * 7 + "║")
    print("╚" + "═" * 58 + "╝")
    
    try:
        # Test 1: Health check
        test_health_check()
        
        # Test 2: List customers
        customer_id = test_list_customers()
        
        if not customer_id:
            print("\nNo customers found. Please check database.")
            return
        
        # Test 3: Get specific customer
        test_get_customer(customer_id)
        
        # Test 4: Get agent status
        test_agent_status()
        
        # Test 5: Create workflow
        workflow_id = test_create_workflow(customer_id)
        
        if workflow_id:
            # Test 6: Check workflow status
            test_workflow_status(workflow_id)
        
        # Test 7: List all workflows
        test_list_workflows()
        
        # Test 8: Quick upgrade
        quick_workflow_id = test_quick_upgrade(customer_id)
        if quick_workflow_id:
            test_workflow_status(quick_workflow_id)
        
        print_section("All Tests Completed!")
        print("\n✓ API is working correctly!")
        
    except requests.exceptions.ConnectionError:
        print("\n✗ Error: Cannot connect to the API server.")
        print("  Make sure the server is running: python main.py")
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")


if __name__ == "__main__":
    main()
