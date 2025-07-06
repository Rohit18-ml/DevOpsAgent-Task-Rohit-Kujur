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

def analyze_memory_patterns(timestamp, current_memory_usage):
    try:
        start_time = timestamp - 3600  # Last hour
        end_time = timestamp
        step = "60s"  # 1-minute intervals
        query = '100 - (avg by(instance) (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes) * 100)'
        prometheus_url = f"http://localhost:9090/api/v1/query_range?query={query}&start={start_time}&end={end_time}&step={step}"
        
        response = requests.get(prometheus_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        values = data['data']['result'][0]['values'] if data['data']['result'] else []
        if not values:
            return "No memory usage data available from Prometheus"
        
        memory_usages = [float(v[1]) for v in values]
        avg_memory = sum(memory_usages) / len(memory_usages)
        trend = "increasing" if memory_usages[-1] > memory_usages[0] else "stable or decreasing"
        
        analysis = f"Memory usage over the last hour: avg {avg_memory:.2f}%, current {current_memory_usage:.2f}%, trend: {trend}."
        if memory_usages[-1] > 20:
            analysis += " High memory usage detected. Suggest setting Docker memory limits and investigating memory leaks."
        return analysis
    except Exception as e:
        logging.error(f"Memory pattern analysis error: {str(e)}")
        return f"Error analyzing memory patterns: {str(e)}"

def analyze_logs(input_data):
    try:
        data = json.loads(input_data) if isinstance(input_data, str) else input_data
        timestamp = data.get("timestamp", int(time.time()))
        memory_usage = data.get("memory_usage", 0)

        # Query logs within 5 minutes to ensure freshness
        start_time = timestamp - 300
        end_time = timestamp + 300
        loki_url = f"http://localhost:3100/loki/api/v1/query_range?query={{job=\"varlogs\"}} |= \"ERROR\"&start={start_time}&end={end_time}&limit=100"
        
        for attempt in range(3):
            try:
                logging.info(f"[DEBUG] Querying Loki (attempt {attempt + 1}): {loki_url}")
                response = requests.get(loki_url, timeout=10)
                response.raise_for_status()
                logs_data = response.json()
                
                logs = [entry[1] for stream in logs_data['data']['result'] for entry in stream['values']]
                logging.info(f"[DEBUG] Logs retrieved: {logs}")

                if not logs:
                    logging.info("No logs found in Loki")
                    return {"logs": "", "analysis": "No recent logs available, check Loki and Promtail configurations", "actionable": False}

                logs_str = "\n".join(logs)
                analysis = "Possible causes for high CPU usage include an OutOfMemory error or infinite loop. "
                analysis += analyze_memory_patterns(timestamp, memory_usage)
                analysis += " Suggested remediation: Restart the app container and investigate the application code for memory leaks or infinite loops."
                logging.info(f"Log analysis completed: {{'logs': '{logs_str}', 'analysis': '{analysis}', 'actionable': True}}")
                return {"logs": logs_str, "analysis": analysis, "actionable": True}

            except requests.exceptions.RequestException as e:
                logging.warning(f"Loki query attempt {attempt + 1} failed: {str(e)}")
                time.sleep(2)
        
        logging.error("All Loki query attempts failed")
        return {"logs": "", "analysis": "Failed to query Loki after multiple attempts", "actionable": False}

    except Exception as e:
        logging.error(f"Analyze logs error: {str(e)}", exc_info=True)
        return {"logs": "", "analysis": f"Error analyzing logs: {str(e)}", "actionable": False}
