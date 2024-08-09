"""
This file contains the Flask application.
"""

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Sample data
data = {"message": "Hello, from Flask!"}

@app.route('/api/data', methods=['GET'])
def get_data():
    """
    The get_data function to return a response
    """
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
