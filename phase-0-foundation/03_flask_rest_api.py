from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory "database" for our books
# In a real application, this would be a proper database (SQL or NoSQL)
books = [
    {"id": "1", "title": "The Hitchhiker's Guide to the Galaxy", "author": "Douglas Adams"},
    {"id": "2", "title": "Pride and Prejudice", "author": "Jane Austen"}
]
next_id = 3

@app.route('/books', methods=['GET'])
def get_books():
    """
    Handles GET requests to /books.
    Returns a list of all books.
    """
    print(f"Received GET request for /books from {request.remote_addr}")
    return jsonify(books)

@app.route('/books', methods=['POST'])
def add_book():
    """
    Handles POST requests to /books.
    Adds a new book to the list.
    Expects JSON payload like: {"title": "New Book", "author": "New Author"}
    """
    global next_id
    print(f"Received POST request for /books from {request.remote_addr}")
    
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    new_book_data = request.get_json()
    if not new_book_data or 'title' not in new_book_data or 'author' not in new_book_data:
        return jsonify({"error": "Missing title or author"}), 400

    new_book = {
        "id": str(next_id),
        "title": new_book_data['title'],
        "author": new_book_data['author']
    }
    books.append(new_book)
    next_id += 1
    
    print(f"Added new book: {new_book}")
    return jsonify(new_book), 201 # 201 Created status code

if __name__ == '__main__':
    # Flask runs a development server by default.
    # In production, you'd use a WSGI server like Gunicorn or uWSGI.
    app.run(debug=True, port=8080)