import os
import time
import requests

base = os.environ.get("BASE_URL", "http://127.0.0.1:8081")

for i in range(6):
    r = requests.get(f"{base}/")
    print(i, r.json())
    time.sleep(0.1)