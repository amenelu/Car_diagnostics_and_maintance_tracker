# Car Diagnostics and Maintenance Tracker

A hybrid Python application designed to help car owners track maintenance history, mileage, and diagnostic issues. This project features both a **Command Line Interface (CLI)** for quick management and a **Flask Web Interface** for a visual dashboard.

## Features

- **Vehicle Management**: Add, edit, and delete cars from the system.
- **Maintenance Tracking**: Log services (oil changes, tire rotations, etc.) with costs and dates.
- **Diagnostics**: Log and resolve diagnostic trouble codes (DTCs) and issues.
- **Service Reminders**: Check if a car is due for specific services based on mileage or time intervals.
- **Search & Filter**: Find cars by VIN, license plate, or filter by year, mileage, and open issues.
- **Undo/Redo**: (CLI only) Revert accidental changes to car data.
- **Data Persistence**: All data is stored in a local SQLite database.

## Project Structure

```text
/project-root
├── /data                   # Stores the SQLite database (car_tracker.db)
├── /src                    # Source code
│   ├── /cli                # Command Line Interface logic
│   ├── /web                # Flask Web Application logic
│   ├── car.py              # Core Car model
│   ├── database.py         # Database interactions
│   └── ...                 # Helper modules (maintenance, search, history)
├── /tests                  # Unit tests
├── requirements.txt        # Python dependencies
└── README.md
```

## Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd Car_diagnostics_and_maintance_tracker
   ```

2. **Create a virtual environment** (Recommended):

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Ensure you are in the root directory of the project before running these commands.

### Running the CLI

To use the text-based interface:

```bash
python -m src.cli.main
```

### Running the Web App

To start the Flask web server:

```bash
python -m src.web.app
```

Then open your browser and navigate to: `http://127.0.0.1:5000`

## Running Tests

This project includes a suite of unit tests to ensure data integrity and logic correctness.

Run all tests using `unittest`:

```bash
python -m unittest discover tests
```
