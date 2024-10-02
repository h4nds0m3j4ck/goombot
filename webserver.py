from flask import Flask  # 'Flask' needs to be capitalized
from threading import Thread

# Initialize the Flask app
app = Flask(__name__)  # '__name__' is usually passed to Flask for proper routing

# Define the root route
@app.route('/')
def home():
    return "Discord Bot Status: OK"

# Function to run the web server
def run():
    app.run(host="0.0.0.0", port=8080)

# Function to keep the web server alive
def keep_alive():
    t = Thread(target=run)
    t.start()
