import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime
import os

def generate_anomaly_webpage():
    # Read log file
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
    df["message_length"] = df["message"].apply(len)

    # AI Model for Anomaly Detection
    model = IsolationForest(contamination=0.1, random_state=42)
    df["anomaly"] = model.fit_predict(df[["level_score", "message_length"]])
    df["is_anomaly"] = df["anomaly"].apply(lambda x: "Anomaly" if x == -1 else "Normal")

    # Get anomalies
    anomalies = df[df["is_anomaly"] == "Anomaly"].copy()
    anomalies = anomalies.sort_values("timestamp")
    
    # Generate HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AIOps Log Anomaly Detection Results</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
                font-weight: 300;
            }}
            .header p {{
                margin: 10px 0 0 0;
                opacity: 0.9;
                font-size: 1.1em;
            }}
            .stats {{
                display: flex;
                justify-content: space-around;
                padding: 30px;
                background: #f8f9fa;
                border-bottom: 1px solid #e9ecef;
            }}
            .stat-card {{
                text-align: center;
                padding: 20px;
                background: white;
                border-radius: 10px;
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
                min-width: 150px;
            }}
            .stat-number {{
                font-size: 2.5em;
                font-weight: bold;
                color: #ff6b6b;
                margin-bottom: 5px;
            }}
            .stat-label {{
                color: #666;
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .content {{
                padding: 30px;
            }}
            .anomaly-table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                background: white;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            }}
            .anomaly-table th {{
                background: linear-gradient(135deg, #667eea, #764ba2);
                color: white;
                padding: 15px;
                text-align: left;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1px;
                font-size: 0.9em;
            }}
            .anomaly-table td {{
                padding: 15px;
                border-bottom: 1px solid #f1f3f4;
                vertical-align: top;
            }}
            .anomaly-table tr:hover {{
                background-color: #f8f9fa;
            }}
            .level-badge {{
                padding: 5px 12px;
                border-radius: 20px;
                font-size: 0.8em;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .level-warning {{
                background: #fff3cd;
                color: #856404;
            }}
            .level-error {{
                background: #f8d7da;
                color: #721c24;
            }}
            .level-critical {{
                background: #d1ecf1;
                color: #0c5460;
            }}
            .level-info {{
                background: #d4edda;
                color: #155724;
            }}
            .timestamp {{
                font-family: 'Courier New', monospace;
                font-size: 0.9em;
                color: #666;
            }}
            .message {{
                max-width: 400px;
                word-wrap: break-word;
                line-height: 1.4;
            }}
            .anomaly-icon {{
                font-size: 1.2em;
                color: #ff6b6b;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                background: #f8f9fa;
                color: #666;
                border-top: 1px solid #e9ecef;
            }}
            .no-anomalies {{
                text-align: center;
                padding: 60px 20px;
                color: #28a745;
            }}
            .no-anomalies h3 {{
                font-size: 1.5em;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔍 AIOps Log Anomaly Detection</h1>
                <p>AI-Powered Log Analysis Results</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{len(df)}</div>
                    <div class="stat-label">Total Logs</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(anomalies)}</div>
                    <div class="stat-label">Anomalies Found</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{len(anomalies)/len(df)*100:.1f}%</div>
                    <div class="stat-label">Anomaly Rate</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{datetime.now().strftime('%H:%M')}</div>
                    <div class="stat-label">Analysis Time</div>
                </div>
            </div>
            
            <div class="content">
    """
    
    if len(anomalies) > 0:
        html_content += """
                <h2>🚨 Detected Anomalies</h2>
                <table class="anomaly-table">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Level</th>
                            <th>Message</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for _, row in anomalies.iterrows():
            level_class = f"level-{row['level'].lower()}"
            html_content += f"""
                        <tr>
                            <td class="timestamp">{row['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</td>
                            <td><span class="level-badge {level_class}">{row['level']}</span></td>
                            <td class="message">{row['message']}</td>
                            <td><span class="anomaly-icon">⚠️</span> Anomaly</td>
                        </tr>
            """
        
        html_content += """
                    </tbody>
                </table>
        """
    else:
        html_content += """
                <div class="no-anomalies">
                    <h3>✅ No Anomalies Detected</h3>
                    <p>All logs appear to be within normal parameters.</p>
                </div>
        """
    
    html_content += f"""
            </div>
            
            <div class="footer">
                <p>Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')} | 
                Powered by Isolation Forest ML Algorithm</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Write HTML file
    output_file = "anomaly_results.html"
    with open(output_file, "w") as f:
        f.write(html_content)
    
    print(f"✅ Anomaly detection webpage generated: {output_file}")
    print(f"📊 Found {len(anomalies)} anomalies out of {len(df)} total logs")
    return output_file

if __name__ == "__main__":
    generate_anomaly_webpage()