import requests
import json
from datetime import datetime, timedelta
import sys

BASE_URL = "http://127.0.0.1:8000"

def print_result(test_name, passed, error_msg=""):
    if passed:
        print(f"[PASS] {test_name}")
    else:
        print(f"[FAIL] {test_name}")
        if error_msg:
            print(f"       -> Error: {error_msg}")

def test_1_inventory_update():
    test_name = "Test 1: Inventory Update (POST /update)"
    url = f"{BASE_URL}/api/v1/inventory/update"
    payload = {
        "phc_id": "PHC-01",
        "medicine_name": "Paracetamol",
        "quantity": 500,
        "timestamp": "2026-07-06T12:00:00Z"
    }
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print_result(test_name, True)
        else:
            print_result(test_name, False, f"Expected status 200, got {response.status_code} - {response.text}")
    except Exception as e:
        print_result(test_name, False, str(e))

def test_2_inventory_status():
    test_name = "Test 2: Inventory Status (GET /status/PHC-01)"
    url = f"{BASE_URL}/api/v1/inventory/status/PHC-01"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            stock = data.get('stock', {})
            required_keys = ['Paracetamol', 'ORS', 'Anti-venom']
            missing_keys = [key for key in required_keys if key not in stock]
            if not missing_keys:
                print_result(test_name, True)
            else:
                print_result(test_name, False, f"Missing keys in stock response: {missing_keys}")
        else:
            print_result(test_name, False, f"Expected status 200, got {response.status_code} - {response.text}")
    except Exception as e:
        print_result(test_name, False, str(e))

def test_3_predict_prophet():
    test_name = "Test 3: AI Prediction Engine - Prophet Path (POST /predict)"
    url = f"{BASE_URL}/api/predict"
    
    # 30 days of mock data
    mock_data = []
    base_date = datetime.strptime("2026-07-06", "%Y-%m-%d")
    for i in range(30):
        date_str = (base_date - timedelta(days=30-i)).strftime("%Y-%m-%d")
        mock_data.append({"phc_id": "PHC-01", "date": date_str, "patient_count": 50 + i % 20})
        
    payload = {
        "footfall_data": mock_data
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            predictions = data.get('predictions', [])
            if isinstance(predictions, list) and len(predictions) == 7:
                missing_keys = []
                for idx, day in enumerate(predictions):
                    keys = ['predicted_count', 'lower_bound', 'upper_bound']
                    missing = [k for k in keys if k not in day]
                    if missing:
                        missing_keys.append(f"Day {idx+1} missing: {missing}")
                if not missing_keys:
                    print_result(test_name, True)
                else:
                    print_result(test_name, False, " | ".join(missing_keys))
            else:
                print_result(test_name, False, f"Expected 7 days of predictions, got {len(predictions) if isinstance(predictions, list) else type(predictions)}")
        else:
            print_result(test_name, False, f"Expected status 200, got {response.status_code} - {response.text}")
    except Exception as e:
        print_result(test_name, False, str(e))

def test_4_predict_fallback():
    test_name = "Test 4: AI Prediction Engine - Fallback Path (POST /predict)"
    url = f"{BASE_URL}/api/predict"
    
    # 5 days of mock data
    mock_data = []
    base_date = datetime.strptime("2026-07-06", "%Y-%m-%d")
    for i in range(5):
        date_str = (base_date - timedelta(days=5-i)).strftime("%Y-%m-%d")
        mock_data.append({"phc_id": "PHC-01", "date": date_str, "patient_count": 50 + i % 20})
        
    payload = {
        "footfall_data": mock_data
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            data = response.json()
            predictions = data.get('predictions', [])
            if isinstance(predictions, list) and len(predictions) == 7:
                missing_keys = []
                for idx, day in enumerate(predictions):
                    keys = ['predicted_count', 'lower_bound', 'upper_bound']
                    missing = [k for k in keys if k not in day]
                    if missing:
                        missing_keys.append(f"Day {idx+1} missing: {missing}")
                if not missing_keys:
                    print_result(test_name, True)
                else:
                    print_result(test_name, False, " | ".join(missing_keys))
            else:
                print_result(test_name, False, f"Expected 7 days of predictions, got {len(predictions) if isinstance(predictions, list) else type(predictions)}")
        else:
            print_result(test_name, False, f"Expected status 200, got {response.status_code} - {response.text}")
    except Exception as e:
        print_result(test_name, False, str(e))

if __name__ == "__main__":
    print("Running Final Backend Checks...\n")
    try:
        requests.get(f"{BASE_URL}/")
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the backend server at http://127.0.0.1:8000")
        print("Please ensure the FastAPI server is running before running this script.")
        sys.exit(1)
        
    test_1_inventory_update()
    test_2_inventory_status()
    test_3_predict_prophet()
    test_4_predict_fallback()
    print("\nChecks completed.")
