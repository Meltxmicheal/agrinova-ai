"""
AgriNova AI - Live API Smoke Test
Tests the running server at http://localhost:5000
"""
import requests
import json
import sys

BASE = "http://localhost:5000"

def test(name, passed, response=None):
    status = "[PASS]" if passed else "[FAIL]"
    info = ""
    if not passed and response is not None:
        try:
            info = f" (Status: {response.status_code}, Body: {response.text})"
        except Exception:
            info = f" (Status: {response.status_code})"
    print(f"  {status} - {name}{info}")
    return passed

results = []

print("=" * 55)
print("  AgriNova AI - Live API Smoke Tests")
print("=" * 55)

# 1. Landing page
print("\n[1] Landing Page")
r = requests.get(f"{BASE}/")
results.append(test("GET / returns 200", r.status_code == 200))
results.append(test("Contains AgriNova", "AgriNova" in r.text))

# 2. Register
print("\n[2] Auth: Register")
r = requests.post(f"{BASE}/api/auth/register", json={
    "full_name": "Smoke Test User",
    "email": "smoketest@agrinova.ai",
    "phone": "9000000000",
    "password": "SmokeTest@123",
    "confirm_password": "SmokeTest@123"
})
data = r.json()
results.append(test(f"Register status: {r.status_code}", r.status_code in [201, 409]))

# 3. Login
print("\n[3] Auth: Login")
r = requests.post(f"{BASE}/api/auth/login", json={
    "email": "smoketest@agrinova.ai",
    "password": "SmokeTest@123"
})
data = r.json()
results.append(test("Login status: 200", r.status_code == 200))
results.append(test("Has access_token", "access_token" in data))
token = data.get("access_token", "")
headers = {"Authorization": f"Bearer {token}"}

# 4. Profile
print("\n[4] Auth: Profile")
r = requests.get(f"{BASE}/api/auth/profile", headers=headers)
data = r.json()
results.append(test("Profile status: 200", r.status_code == 200))
results.append(test("Email matches", data.get("user", {}).get("email") == "smoketest@agrinova.ai"))

# 5. Create Farm
print("\n[5] Farm: Create")
r = requests.post(f"{BASE}/api/farms/", json={
    "farm_name": "Smoke Test Farm",
    "state": "Karnataka",
    "district": "Bangalore",
    "village": "Yelahanka",
    "soil_type": "Loamy",
    "farm_size": 2.5,
    "latitude": 13.0827,
    "longitude": 77.5877
}, headers=headers)
data = r.json()
results.append(test("Create Farm status: 201", r.status_code == 201))
farm_id = data.get("farm", {}).get("id", "")

# 6. Get Farms
print("\n[6] Farm: List")
r = requests.get(f"{BASE}/api/farms/", headers=headers)
data = r.json()
results.append(test("List Farms status: 200", r.status_code == 200))
results.append(test("Farms count >= 1", len(data.get("farms", [])) >= 1))

# 7. Weather
print("\n[7] Weather: Fetch")
r = requests.get(f"{BASE}/api/weather/?farm_id={farm_id}", headers=headers)
data = r.json()
results.append(test("Weather status: 200", r.status_code == 200))
results.append(test("Has current data", "current" in data.get("weather", {})))

# 8. Crop Recommendation
print("\n[8] AI: Crop Recommendation")
r = requests.post(f"{BASE}/api/crop/recommend", json={
    "farm_id": farm_id, "season": "Kharif", "farming_goal": "Maximum Yield"
}, headers=headers)
data = r.json()
results.append(test("Crop Rec status: 200", r.status_code == 200, r))
results.append(test(f"Recommended: {data.get('recommended_crop', 'N/A')}", data.get("success", False), r))

# 9. Yield Prediction
print("\n[9] AI: Yield Prediction")
r = requests.post(f"{BASE}/api/prediction/yield", json={
    "farm_id": farm_id, "crop": "rice", "season": "Kharif"
}, headers=headers)
data = r.json()
results.append(test("Yield status: 200", r.status_code == 200, r))
results.append(test(f"Yield: {data.get('predicted_yield', 'N/A')} tonnes", data.get("success", False), r))

# 10. Fertilizer
print("\n[10] AI: Fertilizer Recommendation")
r = requests.post(f"{BASE}/api/ai/fertilizer", json={
    "farm_id": farm_id, "crop_type": "rice", "season": "Kharif"
}, headers=headers)
data = r.json()
results.append(test("Fertilizer status: 200", r.status_code == 200, r))
results.append(test(f"Fertilizer: {data.get('recommended_fertilizer', 'N/A')}", data.get("success", False), r))

# 11. Market Price
print("\n[11] AI: Market Price Prediction")
r = requests.post(f"{BASE}/api/prediction/price", json={
    "farm_id": farm_id, "commodity": "Rice", "month": 7
}, headers=headers)
data = r.json()
results.append(test("Price status: 200", r.status_code == 200, r))
results.append(test(f"Price: Rs.{data.get('predicted_price', 'N/A')}/qt", data.get("success", False), r))

# 12. Dashboard Stats
print("\n[12] Dashboard: Stats")
r = requests.get(f"{BASE}/api/dashboard/stats", headers=headers)
data = r.json()
results.append(test("Dashboard status: 200", r.status_code == 200))
results.append(test("Has stats", "stats" in data))

# 13. Reports Export
print("\n[13] Reports: CSV Export")
r = requests.get(f"{BASE}/api/reports/export?format=csv&report_type=predictions", headers=headers)
results.append(test(f"CSV Export status: {r.status_code}", r.status_code == 200, r))

# 14. Cleanup - Delete Farm
print("\n[14] Farm: Delete")
if farm_id:
    r = requests.delete(f"{BASE}/api/farms/{farm_id}", headers=headers)
    results.append(test("Delete Farm status: 200", r.status_code == 200, r))

# Summary
print("\n" + "=" * 55)
passed = sum(results)
total = len(results)
print(f"  Results: {passed}/{total} tests passed")
print("=" * 55)

sys.exit(0 if passed == total else 1)
