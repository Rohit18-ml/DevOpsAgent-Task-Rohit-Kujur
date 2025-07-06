from flask import Flask, render_template, request, jsonify
import requests
import json
import os
import time
import subprocess
import logging

app = Flask(__name__)

# Setup logging
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'opsbot.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    force=True
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
console.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(console)

def fetch_metrics():
    try:
        cpu_query = "100 - (avg by(instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[1m])) * 100)"
        memory_query = "100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))"
        prometheus_url = "http://localhost:9090/api/v1/query"

        cpu_response = requests.get(prometheus_url, params={"query": cpu_query}, timeout=10)
        cpu_response.raise_for_status()
        cpu_data = cpu_response.json()
        cpu_usage = float(cpu_data['data']['result'][0]['value'][1]) if cpu_data['data']['result'] else 0

        memory_response = requests.get(prometheus_url, params={"query": memory_query}, timeout=10)
        memory_response.raise_for_status()
        memory_data = memory_response.json()
        memory_usage = float(memory_data['data']['result'][0]['value'][1]) if memory_data['data']['result'] else 0

        return {
            "cpu_usage": round(cpu_usage, 2),
            "memory_usage": round(memory_usage, 2),
            "timestamp": int(time.time())
        }
    except Exception as e:
        logging.error(f"Fetch metrics error: {str(e)}", exc_info=True)
        return {"cpu_usage": 0, "memory_usage": 0, "timestamp": int(time.time())}

def fetch_logs():
    try:
        loki_url = "http://localhost:3100/loki/api/v1/query_range"
        query = '{job="varlogs"} |= "ERROR"'
        params = {
            "query": query,
            "start": str(int(time.time()) - 900),
            "end": str(int(time.time())),
            "limit": 10
        }
        response = requests.get(loki_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        logs = [entry[1] for stream in data['data']['result'] for entry in stream['values']]
        return logs
    except Exception as e:
        logging.error(f"Fetch logs error: {str(e)}", exc_info=True)
        return ["No logs available"]

def manual_remediation(action):
    try:
        if action == "restart_app":
            result = subprocess.run(["docker", "restart", "app"], capture_output=True, text=True)
            if result.returncode == 0:
                logging.info("Manual remediation: Restarted app container")
                return "Restarted app container"
            else:
                logging.error(f"Manual remediation failed: {result.stderr}")
                return f"Failed to restart app container: {result.stderr}"
        else:
            return "No action taken"
    except Exception as e:
        logging.error(f"Manual remediation error: {str(e)}", exc_info=True)
        return f"Remediation failed: {str(e)}"

def fetch_notification_history():
    try:
        history_file = os.path.join(log_dir, 'notification_history.json')
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                return json.load(f)
        return []
    except Exception as e:
        logging.error(f"Fetch notification history error: {str(e)}", exc_info=True)
        return []

@app.route('/')
def dashboard():
    metrics = fetch_metrics()
    logs = fetch_logs()
    history = fetch_notification_history()
    return render_template('index.html', metrics=metrics, logs=logs, history=history)

@app.route('/remediate', methods=['POST'])
def remediate():
    action = request.form.get('action')
    result = manual_remediation(action)
    return jsonify({"result": result})

if __name__ == "__main__":
    if not os.path.exists(os.path.join(log_dir, 'notification_history.json')):
        with open(os.path.join(log_dir, 'notification_history.json'), 'w') as f:
            json.dump([], f)
    app.run(host='0.0.0.0', port=5000)
