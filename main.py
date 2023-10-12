# [START gae_python38_app]
# [START gae_python3_app]]
import requests
from flask import Flask, request, jsonify, redirect
import sqlite3
import string
import time
import string
import random

# Define the base62 character set
BASE62_CHARS = string.ascii_letters + string.digits

def base62_encode(number):
    if number == 0:
        return BASE62_CHARS[0]

    base62 = []
    while number:
        number, i = divmod(number, 62)
        base62.append(BASE62_CHARS[i])
    return ''.join(reversed(base62))

def base62_decode(base62_str):
    number = 0
    for char in base62_str:
        number = number * 62 + BASE62_CHARS.index(char)
    return number


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)


# Initialize SQLite database
conn = sqlite3.connect('url_shortener.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS urls (
        id INTEGER PRIMARY KEY,
        original_url TEXT,
        short_url TEXTa
    )
''')
conn.commit()
conn.close()


# Function to validate a URL
def is_valid_url(url):
    try:
        response = requests.get(url)
        return True  # Return True if the URL is reachable (status code 200)
    except requests.exceptions.RequestException:
        print(f"Original URL is not reachable")
        return False  # Return False if the URL is not reachable


# Endpoint to purge (delete) all records from the database using a GET request
@app.route('/purge', methods=['GET'])
def purge_database():
    conn = sqlite3.connect('url_shortener.db')
    cursor = conn.cursor()
    
    # Delete all records in the 'urls' table
    cursor.execute('DELETE FROM urls')
    
    conn.commit()
    conn.close()
    
    return jsonify({"message": "All records purged from the database"})

# Function to generate a random shortened URL
def generate_short_url(original_url):
    conn = sqlite3.connect('url_shortener.db')
    cursor = conn.cursor()

    # Create a table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY,
            original_url TEXT,
            short_url TEXT
        )
    ''')

    while True:
        # Generate a short URL based on a timestamp
        timestamp = int(time.time())
        random_component = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
        short_url = base62_encode(timestamp) + random_component

        # Check if the generated short URL already exists in the database
        cursor.execute('SELECT COUNT(*) FROM urls WHERE short_url = ?', (short_url,))
        count = cursor.fetchone()[0]

        # If the short URL is unique, insert the record and return it
        if count == 0:
            conn.close()
            return short_url


@app.route('/')
def home():
    return app.send_static_file("url_short.html")

# Endpoint to shorten a URL using a GET request
@app.route('/shorten', methods=['GET'])
def shorten_url():
    original_url = request.args.get('original_url')
    
    if original_url and is_valid_url(original_url):
        # Generate a unique shortened URL
        short_url = generate_short_url(original_url)
        
        # Store the mapping in the database
        conn = sqlite3.connect('url_shortener.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO urls (original_url, short_url) VALUES (?, ?)', (original_url, short_url))
        conn.commit()
        conn.close()
        
        # Print debug messages
        print(f"Original URL: {original_url}")
        print(f"Shortened URL: {short_url}")
        
        # Prepare and return the response
        response_data = {"short_url": short_url}
        print(f"Response: {response_data}")
        return jsonify(response_data)
    else:
        return jsonify({"error": "Invalid URL"}), 400



# Endpoint to redirect to the original URL using a GET request
@app.route('/<short_url>', methods=['GET'])
def redirect_to_original(short_url):
    # Look up the mapping in the database
    conn = sqlite3.connect('url_shortener.db')
    cursor = conn.cursor()
    cursor.execute('SELECT original_url FROM urls WHERE short_url = ?', (short_url,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        original_url = result[0]
        print(f"Redirecting to Original URL: {original_url}")
        return redirect(original_url, code=302)
    
    print("Short URL not found")

    # Short URL not found, render the error.html page
    return app.send_static_file("error.html")






# Endpoint to list all URLs using a GET request
@app.route('/list', methods=['GET'])
def list_urls():
    conn = sqlite3.connect('url_shortener.db')
    cursor = conn.cursor()
    cursor.execute('SELECT original_url, short_url FROM urls')
    result = cursor.fetchall()
    conn.close()
    
    urls = [{"original_url": row[0], "short_url": row[1]} for row in result]
    
    print("List of URLs:")
    for url in urls:
        print(f"Original URL: {url['original_url']}, Short URL: {url['short_url']}")
    
    # Prepare and return the response
    response_data = {"urls": urls}
    print(f"Response: {response_data}")
    return jsonify(response_data)

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. You
    # can configure startup instructions by adding `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python3_app]
# [END gae_python38_app]