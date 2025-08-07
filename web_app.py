from flask import Flask, render_template, jsonify
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from collections import Counter
import re
import json

app = Flask(__name__)

def get_basic_analysis():
    """Perform basic log analysis"""
    log_file = "error_logs.txt"
    
    log_entries = []
    with open(log_file, "r") as file:
        for line in file:
            match = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) (\w+) (.+)", line.strip())
            if match:
                timestamp, level, message = match.groups()
                log_entries.append([timestamp, level, message])

    # Convert to DataFrame
    df = pd.DataFrame(log_entries, columns=["timestamp", "level", "message"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Count errors in the last 30 seconds
    error_counts = Counter(df[df["level"] == "ERROR"]["timestamp"].dt.floor("30s"))

    # Threshold for detecting an anomaly
    threshold = 3

    # Detect error spikes
    anomalies = []
    for time, count in error_counts.items():
        if count > threshold:
            anomalies.append({
                'time': time.strftime('%Y-%m-%d %H:%M:%S'),
                'count': count,
                'message': f'{count} ERROR logs in 30 seconds'
            })

    # Get log level distribution
    level_counts = df['level'].value_counts().to_dict()
    
    return {
        'anomalies': anomalies,
        'total_logs': len(df),
        'level_distribution': level_counts,
        'recent_logs': df.tail(10).to_dict('records')
    }

def get_ai_analysis():
    """Perform AI-powered log analysis"""
    log_file_path = "error_logs.txt"
    with open(log_file_path, "r") as file:
        logs = file.readlines()

    # Parse logs into a structured DataFrame
    data = []
    for log in logs:
        parts = log.strip().split(" ", 3)
        if len(parts) < 4:
            continue
        timestamp = parts[0] + " " + parts[1]
        level = parts[2]
        message = parts[3]
        data.append([timestamp, level, message])

    df = pd.DataFrame(data, columns=["timestamp", "level", "message"])
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # Assign numeric scores to log levels
    level_mapping = {"INFO": 1, "WARNING": 2, "ERROR": 3, "CRITICAL": 4}
    df["level_score"] = df["level"].map(level_mapping)

    # Add message length as a feature
    df["message_length"] = df["message"].apply(len)

    # AI Model for Anomaly Detection
    model = IsolationForest(contamination=0.1, random_state=42)
    df["anomaly"] = model.fit_predict(df[["level_score", "message_length"]])

    # Get anomalies
    anomalies = df[df["anomaly"] == -1]
    
    return {
        'total_anomalies': len(anomalies),
        'anomaly_percentage': round((len(anomalies) / len(df)) * 100, 2),
        'anomalies': anomalies.head(20).to_dict('records'),
        'model_info': {
            'algorithm': 'Isolation Forest',
            'contamination': 0.1,
            'features': ['log_level_score', 'message_length']
        }
    }

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/basic-analysis')
def api_basic_analysis():
    """API endpoint for basic analysis"""
    try:
        result = get_basic_analysis()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ai-analysis')
def api_ai_analysis():
    """API endpoint for AI analysis"""
    try:
        result = get_ai_analysis()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)