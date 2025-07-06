import logging
import os
import time
import json
from langchain_ollama import ChatOllama

# Local modules
from monitor import monitor_metrics
from analyze import analyze_logs
from remediate import remediate_service
from notify import send_notification

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

# Initialize Ollama model
try:
    llm = ChatOllama(
        base_url="http://localhost:11434",
        model="llama2"
    )
except Exception as e:
    logging.error(f"Failed to initialize Ollama: {str(e)}")
    llm = None

def run_agent():
    try:
        logging.info("Starting agent workflow")
        anomaly = monitor_metrics()
        if not anomaly:
            logging.info("No anomalies detected.")
            return {"status": "healthy"}

        anomaly = json.loads(anomaly) if isinstance(anomaly, str) else anomaly
        if not anomaly.get("anomaly_detected", False):
            logging.info(f"No anomaly detected: CPU Usage: {anomaly.get('cpu_usage', 0)}%, Memory Usage: {anomaly.get('memory_usage', 0)}%")
            return {"status": "healthy", "anomaly": anomaly}

        logging.info(f"Anomaly detected: {anomaly}")

        analysis = analyze_logs(json.dumps({"timestamp": anomaly.get("timestamp", int(time.time())), "memory_usage": anomaly.get("memory_usage", 0)}))
        analysis = json.loads(analysis) if isinstance(analysis, str) else analysis
        logging.info(f"Analysis result: {analysis}")

        remediation = remediate_service(analysis)
        logging.info(f"Remediation result: {remediation}")

        notification = send_notification({
            "anomaly": anomaly,
            "analysis": analysis,
            "remediation": remediation
        })
        logging.info(f"Notification result: {notification}")

        summary = "No LLM summary available"
        if llm:
            try:
                prompt = f"""
                You are an AI DevOps assistant. Given the following information, identify possible causes for the detected anomaly and suggest remediation steps. Include analysis of memory usage patterns if available.

                Anomaly: {json.dumps(anomaly)}
                Logs: {analysis.get('logs', 'No logs available')}
                Analysis: {analysis.get('analysis', 'No analysis available')}
                Remediation: {remediation.get('action', 'No action taken')}

                If CPU usage is >80%, recommend restarting the app container and investigating code for inefficiencies or memory leaks. If memory usage is increasing over time, suggest setting Docker resource limits. If no logs are available, suggest checking Loki and Promtail configurations.
                """
                response = llm.invoke(prompt)
                summary = response.content
                logging.info(f"LLM Summary: {summary}")
            except Exception as e:
                logging.error(f"LLM invocation error: {str(e)}")
                summary = f"LLM error: {str(e)}"

        result = {
            "anomaly": anomaly,
            "analysis": analysis,
            "remediation": remediation,
            "notification": notification,
            "summary": summary
        }
        logging.info(f"Agent cycle result: {result}")
        return result

    except Exception as e:
        logging.error(f"Agent error: {str(e)}", exc_info=True)
        return {"error": str(e)}

if __name__ == "__main__":
    while True:
        try:
            result = run_agent()
            logging.info(f"Agent cycle result: {result}")
            logging.info("Agent cycle completed, sleeping for 30 seconds")
            time.sleep(30)
        except KeyboardInterrupt:
            logging.info("Agent stopped by user")
            break
        except Exception as e:
            logging.error(f"Main loop error: {str(e)}", exc_info=True)
            time.sleep(30)
