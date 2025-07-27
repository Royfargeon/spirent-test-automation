from flask import Flask, render_template, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import csv
from datetime import datetime
import subprocess
import json

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'test_configs'
RESULTS_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'tcc'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Create required directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

@app.route('/')
def index():
    # Get list of test configurations
    test_files = [f for f in os.listdir(UPLOAD_FOLDER) if f.endswith('.tcc')]
    return render_template('index.html', test_files=test_files)

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