import requests
import threading
import time

def send_request(request_id):
    start_time = time.time()
    print(f"🚀 Thread {request_id}: Sending request...")
    try:
        # We send a request to our local server
        response = requests.get("http://127.0.0.1:8080/test")
        end_time = time.time()
        print(f"✅ Thread {request_id}: Received response after {end_time - start_time:.2f} seconds")
    except Exception as e:
        print(f"❌ Thread {request_id}: Failed! {e}")

def run_test():
    print("🏁 Starting Concurrency Test (sending 3 simultaneous requests)...")
    threads = []
    
    # Create 3 threads to send requests at the same time
    for i in range(1, 4):
        t = threading.Thread(target=send_request, args=(i,))
        threads.append(t)
        t.start()
        # Small delay to ensure order in terminal, but effectively simultaneous
        time.sleep(0.1)

    for t in threads:
        t.join()
    print("🏁 Test Finished.")

if __name__ == "__main__":
    run_test()
