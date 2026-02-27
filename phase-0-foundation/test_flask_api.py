import requests
import json

BASE_URL = "http://127.0.0.1:8080"

def test_get_books():
    print("\n🔍 Testing GET /books...")
    response = requests.get(f"{BASE_URL}/books")
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")

def test_post_book():
    print("\n📝 Testing POST /books...")
    new_book = {
        "title": "Clean Code",
        "author": "Robert C. Martin"
    }
    response = requests.post(f"{BASE_URL}/books", json=new_book)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    try:
        # 1. Get initial books
        test_get_books()
        
        # 2. Add a new book
        test_post_book()
        
        # 3. Get books again to verify the addition
        test_get_books()
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to the server.")
        print("Make sure your Flask server is running on http://127.0.0.1:8080")
