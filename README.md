# Spirent Test Automation Tool

A web-based automation tool for running Spirent test center configurations. This tool provides a user-friendly interface for managing test configurations, executing tests, and visualizing results.

## Features

- Web-based UI for test management
- Upload and manage .tcc test configuration files
- Execute tests via Python shell
- Real-time test execution status
- Results visualization with charts and tables
- CSV export for test results

## Setup

1. Clone the repository:
```bash
git clone https://github.com/Royfargeon/spirent-test-automation.git
cd spirent-test-automation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
.
├── static/          # Static files (CSS, JS)
├── templates/       # HTML templates
├── test_configs/    # Test configuration files
├── results/         # Test results and CSV files
├── app.py          # Main Flask application
└── requirements.txt # Python dependencies
```

## Usage

1. Upload test configurations (.tcc files)
2. Select a test from the dropdown
3. Run the test
4. View results in charts and tables
5. Export results as CSV

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
