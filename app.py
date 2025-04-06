from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os
import logging

app = Flask(__name__)

# Optional: Restrict CORS to specific origins (e.g., frontend URL)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Change "*" to your frontend URL if needed

# Set up logging
logging.basicConfig(level=logging.INFO)

# Path to the CSV file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "computed_data.csv")

def read_csv_data():
    """Reads CSV and returns data for line and bar charts."""
    if not os.path.exists(CSV_FILE):
        logging.error("CSV file not found.")
        return {"error": "CSV file not found"}

    try:
        df = pd.read_csv(CSV_FILE, encoding="utf-8")

        if "year_month" not in df.columns:
            logging.error("'year_month' column missing in CSV.")
            return {"error": "'year_month' column is missing in the CSV"}

        data = {"year_month": df["year_month"].astype(str).tolist()}

        for col in df.columns[1:]:  # Skip 'year_month'
            data[col] = df[col].fillna(0).tolist()

        return data

    except Exception as e:
        logging.exception("Error while reading CSV:")
        return {"error": str(e)}

@app.route('/')
def index():
    """Root endpoint to check API status."""
    return jsonify({"message": "Flask API is running!"})

@app.route('/api/data', methods=['GET'])
def get_data():
    """Returns line and bar chart data."""
    return jsonify(read_csv_data())

@app.route('/pie_data', methods=['GET'])
def get_pie_data():
    """Returns pie chart data for a specific month."""
    if not os.path.exists(CSV_FILE):
        logging.error("CSV file not found.")
        return jsonify({"error": "CSV file not found"}), 500

    try:
        df = pd.read_csv(CSV_FILE)
        month = request.args.get("month", df["year_month"].iloc[-1])  # Use latest month if not provided

        if month not in df["year_month"].values:
            logging.warning(f"Month '{month}' not found in data.")
            return jsonify({"error": "Month not found"}), 400

        row = df[df["year_month"] == month].iloc[0]

        pie_data = {
            "labels": row.index[1:].tolist(),
            "values": row.values[1:].astype(float).tolist()
        }

        return jsonify(pie_data)

    except Exception as e:
        logging.exception("Error while fetching pie chart data:")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
