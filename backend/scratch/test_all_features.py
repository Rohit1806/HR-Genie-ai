import httpx
import sys
import json

BASE_URL = "http://localhost:8000/api/v1"

def print_result(feature_name, success, info="", error=None):
    status_str = "SUCCESS" if success else "FAILED"
    print(f"| {feature_name:<40} | {status_str:<10} | {info:<35} | {str(error)[:40] if error else '':<40} |")

def test_all():
    print(f"\nHRGenie AI Feature Verification Report")
    print(f"="*140)
    print(f"| {'Feature/Endpoint Name':<40} | {'Status':<10} | {'Additional Information':<35} | {'Error Details':<40} |")
    print(f"|{'-'*42}|{'-'*12}|{'-'*37}|{'-'*42}|")

    client = httpx.Client(timeout=10.0)

    # 1. Login
    token = None
    try:
        r = client.post(f"{BASE_URL}/auth/login", json={
            "email": "admin@demo.hrgenie.ai",
            "password": "Demo@1234"
        })
        if r.status_code == 200:
            res_data = r.json()
            token = res_data.get("access_token")
            print_result("1. Auth - Admin Login", True, f"Token obtained (role: {res_data['user']['role']})")
        else:
            print_result("1. Auth - Admin Login", False, f"HTTP Status {r.status_code}", r.text)
    except Exception as e:
        print_result("1. Auth - Admin Login", False, "Connection Error", e)

    if not token:
        print("\n[CRITICAL] Login failed. Skipping remaining tests that require authentication.")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Auth - Get Me
    try:
        r = client.get(f"{BASE_URL}/auth/me", headers=headers)
        if r.status_code == 200:
            print_result("2. Auth - Profile (/auth/me)", True, f"Logged in as: {r.json()['full_name']}")
        else:
            print_result("2. Auth - Profile (/auth/me)", False, f"HTTP Status {r.status_code}", r.text)
    except Exception as e:
        print_result("2. Auth - Profile (/auth/me)", False, "Request failed", e)

    # 3. Employees - List Employees
    try:
        r = client.get(f"{BASE_URL}/employees/", headers=headers)
        if r.status_code == 200:
            data = r.json()
            print_result("3. Employees - List", True, f"Fetched {data.get('total', 0)} employees successfully")
        else:
            print_result("3. Employees - List", False, f"HTTP Status {r.status_code}", r.text)
    except Exception as e:
        print_result("3. Employees - List", False, "Request failed", e)

    # 4. Employees - Org Chart
    try:
        r = client.get(f"{BASE_URL}/employees/org-chart", headers=headers)
        if r.status_code == 200:
            print_result("4. Employees - Org Chart", True, f"Fetched chart (nodes: {len(r.json())})")
        else:
            print_result("4. Employees - Org Chart", False, f"HTTP Status {r.status_code}", r.text)
    except Exception as e:
        print_result("4. Employees - Org Chart", False, "Request failed", e)

    # 5. Leaves - List Types
    try:
        r = client.get(f"{BASE_URL}/leaves/types", headers=headers)
        if r.status_code == 200:
            print_result("5. Leaves - Leave Types", True, f"Found types: {[t['name'] for t in r.json()]}")
        else:
            print_result("5. Leaves - Leave Types", False, f"HTTP Status {r.status_code}", r.text)
    except Exception as e:
        print_result("5. Leaves - Leave Types", False, "Request failed", e)

    # 6. Leaves - Holidays List
    try:
        r = client.get(f"{BASE_URL}/leaves/holidays", headers=headers)
        if r.status_code == 200:
            print_result("6. Leaves - Holidays Calendar", True, f"Found {len(r.json())} holidays")
        else:
            print_result("6. Leaves - Holidays Calendar", False, f"HTTP Status {r.status_code}", r.text)
    except Exception as e:
        print_result("6. Leaves - Holidays Calendar", False, "Request failed", e)

    # 7. Leaves - Pending Approvals
    try:
        r = client.get(f"{BASE_URL}/leaves/pending-approvals", headers=headers)
        if r.status_code == 200:
            print_result("7. Leaves - Pending Approvals", True, f"Found {r.json().get('total', 0)} requests")
        else:
            print_result("7. Leaves - Pending Approvals", False, f"HTTP Status {r.status_code}", r.text)
    except Exception as e:
        print_result("7. Leaves - Pending Approvals", False, "Request failed", e)

    # 8. Payroll - List Runs
    try:
        r = client.get(f"{BASE_URL}/payroll/runs", headers=headers)
        if r.status_code == 200:
            print_result("8. Payroll - List Runs", True, f"Found {r.json().get('total', 0)} runs")
        else:
            print_result("8. Payroll - List Runs", False, f"HTTP Status {r.status_code}", r.text)
    except Exception as e:
        print_result("8. Payroll - List Runs", False, "Request failed", e)

    # 9. Performance - Cycles List
    try:
        r = client.get(f"{BASE_URL}/performance/cycles", headers=headers)
        if r.status_code == 200:
            print_result("9. Performance - Active Cycles", True, f"Found {len(r.json())} cycles")
        else:
            print_result("9. Performance - Active Cycles", False, f"HTTP Status {r.status_code}", r.text)
    except Exception as e:
        print_result("9. Performance - Active Cycles", False, "Request failed", e)

    # 10. Recruitment - Jobs Postings
    try:
        r = client.get(f"{BASE_URL}/recruitment/jobs", headers=headers)
        if r.status_code == 200:
            print_result("10. Recruitment - Job Postings", True, f"Found {r.json().get('total', 0)} open jobs")
        else:
            print_result("10. Recruitment - Job Postings", False, f"HTTP Status {r.status_code}", r.text)
    except Exception as e:
        print_result("10. Recruitment - Job Postings", False, "Request failed", e)

    # 11. Recruitment - Applications
    try:
        r = client.get(f"{BASE_URL}/recruitment/applications", headers=headers)
        if r.status_code == 200:
            print_result("11. Recruitment - Candidates Pipeline", True, f"Found {r.json().get('total', 0)} applications")
        else:
            print_result("11. Recruitment - Candidates Pipeline", False, f"HTTP Status {r.status_code}", r.text)
    except Exception as e:
        print_result("11. Recruitment - Candidates Pipeline", False, "Request failed", e)

    # 12. Analytics - Admin Dashboard
    try:
        r = client.get(f"{BASE_URL}/analytics/dashboard/admin", headers=headers)
        if r.status_code == 200:
            res = r.json()
            print_result("12. Analytics - Dashboard Overview", True, f"Headcount: {res.get('total_employees', 0)}")
        else:
            print_result("12. Analytics - Dashboard Overview", False, f"HTTP Status {r.status_code}", r.text)
    except Exception as e:
        print_result("12. Analytics - Dashboard Overview", False, "Request failed", e)

    # 13. Analytics - Payroll Trend
    try:
        r = client.get(f"{BASE_URL}/analytics/payroll-cost-trend", headers=headers)
        if r.status_code == 200:
            print_result("13. Analytics - Payroll Trends", True, f"Found trend (months: {len(r.json().get('months', []))})")
        else:
            print_result("13. Analytics - Payroll Trends", False, f"HTTP Status {r.status_code}", r.text)
    except Exception as e:
        print_result("13. Analytics - Payroll Trends", False, "Request failed", e)

    # 14. Employees - Create New Employee (Onboarding Wizard POST)
    # Use fixed department and designation IDs matching the seeded ones
    dept_id = "20ae9523-14d6-4363-b1ef-d7bc49655052" # Engineering
    desg_id = "c8512f18-38c5-480b-ba86-05f595a21370" # Software Engineer
    try:
        if dept_id and desg_id:
            import time
            payload = {
                "first_name": "VerifyNew",
                "last_name": "Tester",
                "personal_email": f"verify_tester_{int(time.time())}@example.com",
                "phone": "9876543210",
                "date_of_birth": "1992-05-15",
                "gender": "male",
                "department_id": dept_id,
                "designation_id": desg_id,
                "employment_type": "full_time",
                "date_of_joining": "2026-06-01",
                "work_location": "Remote",
                "address": {
                    "street": "123 Test St",
                    "city": "TestCity",
                    "state": "TestState",
                    "zip": "123456",
                    "country": "USA"
                },
                "emergency_contact": {
                    "name": "Jane Contact",
                    "relationship": "Spouse",
                    "phone": "9998887776"
                }
            }
            create_r = client.post(f"{BASE_URL}/employees/", json=payload, headers=headers)
            if create_r.status_code == 201:
                print_result("14. Employees - Onboard (POST)", True, f"Successfully created employee code: {create_r.json().get('employee_code')}")
            else:
                print_result("14. Employees - Onboard (POST)", False, f"HTTP Status {create_r.status_code}", create_r.text)
        else:
            print_result("14. Employees - Onboard (POST)", False, "Skipped: Could not find valid department/designation ID")
    except Exception as e:
        print_result("14. Employees - Onboard (POST)", False, "Request failed", e)

if __name__ == "__main__":
    test_all()
