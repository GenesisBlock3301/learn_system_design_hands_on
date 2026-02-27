import requests
import threading
import time

def send_request(request_id, path):
    start_time = time.time()
    print(f"🚀 Thread {request_id}: Sending request to {path}...")
    try:
        response = requests.get(f"http://127.0.0.1:8080{path}")
        end_time = time.time()
        print(f"✅ Thread {request_id}: Received response from {path} after {end_time - start_time:.2f} seconds")
    except Exception as e:
        print(f"❌ Thread {request_id}: Failed! {e}")

def run_test():
    print("🏁 Starting Async Concurrency Test...")
    print("Scenario: One 'slow' request and two 'fast' requests sent simultaneously.")
    
    threads = []
    
    # 1. One slow request (takes 5 seconds on the server)
    t_slow = threading.Thread(target=send_request, args=(1, "/slow"))
    threads.append(t_slow)
    
    # 2. Two fast requests (should return instantly)
    t_fast1 = threading.Thread(target=send_request, args=(2, "/fast"))
    t_fast2 = threading.Thread(target=send_request, args=(3, "/fast-again"))
    threads.append(t_fast1)
    threads.append(t_fast2)

    # Start all threads
    for t in threads:
        t.start()
        time.sleep(0.1) # Tiny gap for clean terminal output

    for t in threads:
        t.join()
        
    print("\n🏁 Test Finished.")
    print("Insight: In a successful Async server, Thread 2 and 3 should finish in < 1 second,")
    print("even while Thread 1 is still waiting for its 5-second sleep.")

if __name__ == "__main__":
    run_test()
