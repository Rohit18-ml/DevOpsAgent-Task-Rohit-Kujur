import requests
import json
import logging
import os
import time

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

def monitor_metrics():
    try:
        # Delay to ensure CPU spike is captured
        time.sleep(10)
        cpu_query = "100 - (avg by(instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[1m])) * 100)"
        memory_query = "100 * (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes))"
        prometheus_url = "http://localhost:9090/api/v1/query"

        for attempt in range(3):
            try:
                cpu_response = requests.get(prometheus_url, params={"query": cpu_query}, timeout=10)
                cpu_response.raise_for_status()
                cpu_data = cpu_response.json()
                cpu_usage = float(cpu_data['data']['result'][0]['value'][1]) if cpu_data['data']['result'] else 0

                memory_response = requests.get(prometheus_url, params={"query": memory_query}, timeout=10)
                memory_response.raise_for_status()
                memory_data = memory_response.json()
                memory_usage = float(memory_data['data']['result'][0]['value'][1]) if memory_data['data']['result'] else 0

                anomaly_detected = cpu_usage > 80 or memory_usage > 80
                result = {
                    "anomaly_detected": anomaly_detected,
                    "cpu_usage": cpu_usage,
                    "memory_usage": memory_usage,
                    "timestamp": int(cpu_data['data']['result'][0]['value'][0]) if cpu_data['data']['result'] else int(time.time())
                }
                logging.info(f"CPU Usage: {cpu_usage}%, Memory Usage: {memory_usage}%")
                return result

            except requests.exceptions.RequestException as e:
                logging.warning(f"Prometheus query attempt {attempt + 1} failed: {str(e)}")
                time.sleep(2)
        logging.error("All Prometheus query attempts failed")
        return None

    except Exception as e:
        logging.error(f"Monitor error: {str(e)}", exc_info=True)
        return None
