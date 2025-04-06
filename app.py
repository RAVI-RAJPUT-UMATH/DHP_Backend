from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests

# Path to your CSV file
CSV_FILE = "computed_data.csv"

def read_csv_data():
    """Reads data from CSV for line/bar charts."""
    if not os.path.exists(CSV_FILE):
        return {"error": "CSV file not found"}

    try:
        df = pd.read_csv(CSV_FILE)

        if "year_month" not in df.columns:
            return {"error": "'year_month' column is missing in the CSV"}

        # Create the response dictionary
        data = {"year_month": df["year_month"].astype(str).tolist()}
        for col in df.columns[1:]:
            data[col] = df[col].fillna(0).tolist()

        return data

    except Exception as e:
        return {"error": f"Error reading CSV: {str(e)}"}

@app.route('/api/data', methods=['GET'])
def get_data():
    """Endpoint to fetch line/bar chart data."""
    data = read_csv_data()
    return jsonify(data)

@app.route('/api/pie_data', methods=['GET'])
def get_pie_data():
    """Endpoint to fetch pie chart data for a selected month."""
    if not os.path.exists(CSV_FILE):
        return jsonify({"error": "CSV file not found"}), 500

    try:
        df = pd.read_csv(CSV_FILE)

        # Get month from query param or fallback to last available
        month = request.args.get("month", df["year_month"].iloc[-1])

        if month not in df["year_month"].values:
            return jsonify({"error": "Month not found"}), 400

        row = df[df["year_month"] == month].iloc[0]
        labels = list(row.index[1:])  # exclude 'year_month'
        values = list(row.values[1:].astype(float))

        return jsonify({
            "labels": labels,
            "values": values
        })

    except Exception as e:
        return jsonify({"error": f"Error processing pie chart data: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
