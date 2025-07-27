from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import csv
from datetime import datetime
import subprocess
import json
import threading
# Configuration
CONFIG_FILE = 'stc_server_config.json'

# --- Configuration ---
app = Flask(__name__, template_folder='templates', static_folder='static')
UPLOAD_FOLDER = 'test_configs'
RESULTS_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'tcc', 'xml'}
CONFIG_FILE = 'stc_server_config.json'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER

# --- Utility Functions ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_stc_server_ip():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            return data.get('stc_server_ip', '')
    return ''

def set_stc_server_ip(ip):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'stc_server_ip': ip}, f)
def get_stc_server_info():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            data = json.load(f)
            return {
                'ip': data.get('stc_server_ip', ''),
                'username': data.get('stc_server_username', ''),
                'password': data.get('stc_server_password', '')
            }
    return {'ip': '', 'username': '', 'password': ''}

def set_stc_server_info(ip, username, password):
    # For demo, store password as plain text. For production, hash or encrypt!
    with open(CONFIG_FILE, 'w') as f:
        json.dump({
            'stc_server_ip': ip,
            'stc_server_username': username,
            'stc_server_password': password
        }, f)

# --- Create required directories ---
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# --- Routes ---
@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error loading index.html: {e}. Make sure 'templates/index.html' exists.", 500

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        return jsonify({'success': True, 'filename': filename})
    return jsonify({'error': 'Invalid file type'})

@app.route('/run-test', methods=['POST'])
def run_test():
    test_file = request.json.get('test_file')
    if not test_file:
        return jsonify({'error': 'No test file specified'})
    test_path = os.path.join(app.config['UPLOAD_FOLDER'], test_file)
    if not os.path.exists(test_path):
        return jsonify({'error': 'Test file not found'})
    try:
        # Execute test using Python shell
        result = execute_test(test_path)
        # Save results to CSV
        csv_filename = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        csv_path = os.path.join(app.config['RESULTS_FOLDER'], csv_filename)
        with open(csv_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=result.keys())
            writer.writeheader()
            writer.writerow(result)
        return jsonify({
            'status': 'success',
            'data': result,
            'csv_file': csv_filename
        })
    except Exception as e:
        return jsonify({'error': str(e)})

# ...existing code...
@app.route('/set-stc-server', methods=['POST'])
def set_stc_server():
    ip = request.json.get('ip')
    username = request.json.get('username')
    password = request.json.get('password')
    if not ip or not username or not password:
        return jsonify({'error': 'IP, username, and password required'}), 400
    set_stc_server_info(ip, username, password)
    return jsonify({'success': True, 'ip': ip, 'username': username})

@app.route('/get-stc-server', methods=['GET'])
def get_stc_server():
    info = get_stc_server_info()
    return jsonify({'ip': info['ip'], 'username': info['username']})

# --- Test Execution Function ---
def execute_test(test_path):
    """Execute the test configuration using Python shell"""
    try:
        # Run the test using Python shell
        cmd = ['python', test_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        # Parse the output and create result dictionary
        return {
            'timestamp': datetime.now().isoformat(),
            'test_file': os.path.basename(test_path),
            'status': 'completed' if result.returncode == 0 else 'failed',
            'output': result.stdout,
            'error': result.stderr,
            'return_code': result.returncode
        }
    except Exception as e:
        raise Exception(f"Test execution failed: {str(e)}")

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=8080)
    except OSError as e:
        print(f"Error: {e}")
        print("The port 8080 might be in use. Try using a different port:")
        print("1. Edit app.py and change the port number")
        print("2. Or run with a different port: export FLASK_RUN_PORT=3000 && python app.py")
        app.run(debug=True, host='0.0.0.0', port=8080)
    except OSError as e:
        print(f"Error: {e}")
        print("The port 8080 might be in use. Try using a different port:")
        print("1. Edit app.py and change the port number")
        print("2. Or run with a different port: export FLASK_RUN_PORT=3000 && python app.py")