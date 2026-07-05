import subprocess
import time
import requests
import json
import random
from datetime import datetime, timedelta
import sys
import socket
import os

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def main():
    server_process = None
    if not is_port_in_use(8000):
        print("Starting FastAPI server...")
        server_process = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        print("Waiting 5 seconds for server to boot...")
        time.sleep(5)
    else:
        print("Server is already running on port 8000.")

    try:
        # Generate mock data
        history = []
        base_date = datetime.now() - timedelta(days=5)
        for i in range(5):
            date_str = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
            history.append({
                "date": date_str,
                "count": random.randint(50, 150)
            })
        
        payload = {"history": history}
        
        url = "http://127.0.0.1:8000/api/predict-shortage"
        print(f"Making POST request to {url}...")
        
        response = requests.post(url, json=payload)
        
        print("\n--- Response ---")
        print(f"Status Code: {response.status_code}")
        try:
            resp_json = response.json()
            print("Response JSON:")
            print(json.dumps(resp_json, indent=2))
        except ValueError:
            print("Raw Response:", response.text)
            print("\nFAILURE: Response is not valid JSON.")
            return

        success = True
        
        if response.status_code != 200:
            print("\nFAILURE: Status code is not 200.")
            success = False
            
        if "predictions" not in resp_json:
            print("\nFAILURE: 'predictions' key not found in response.")
            success = False
        else:
            predictions = resp_json["predictions"]
            if len(predictions) != 7:
                print(f"\nFAILURE: Expected exactly 7 days of predictions, got {len(predictions)}.")
                success = False
                
            for i, p in enumerate(predictions):
                # The prompt mentioned confidence_interval, but our actual implementation uses lower_bound and upper_bound
                for key in ["date", "predicted_count", "lower_bound", "upper_bound"]:
                    if key not in p:
                        print(f"\nFAILURE: Key '{key}' not found in prediction {i}.")
                        success = False

        if success:
            print("\nSUCCESS: All checks passed.")
        else:
            print("\nFAILURE: One or more checks failed.")
            
    except Exception as e:
        print(f"\nFAILURE: An exception occurred: {e}")
        
    finally:
        if server_process:
            print("Terminating server...")
            server_process.terminate()
            server_process.wait()

if __name__ == "__main__":
    main()
