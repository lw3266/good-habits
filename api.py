from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
from database import update_tabs_table, create_tabs_table

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Make sure the tabs table exists.
create_tabs_table()

@app.route('/store_tabs', methods=['POST'])
def store_tabs():
    # Debug: Check if the request is reaching the endpoint
    print("Received a POST request at /store_tabs")
    
    # Attempt to get the JSON data from the request
    try:
        tab_data = request.get_json()
        print("Received tab data:", tab_data)  # Debug: Print the received data
    except Exception as e:
        print("Error parsing JSON:", e)  # Debug: Print any error during parsing
        return jsonify({'status': 'failed', 'message': 'Error parsing tab data'}), 400

    # Check if data was received
    if tab_data:
        # Debug: Print confirmation of received data
        print("Tab data received, calling update_tabs_table")
        update_tabs_table(tab_data)  # Assuming this is working as expected
        return jsonify({'status': 'success'})
    else:
        # Debug: Print if no data was received
        print("No tab data received in request body")
        return jsonify({'status': 'failed', 'message': 'No tab data received'}), 400

if __name__ == '__main__':
    app.run(port=5000)
