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

def save_notification_to_history(data):
    try:
        history_file = os.path.join(log_dir, 'notification_history.json')
        history = []
        if os.path.exists(history_file):
            with open(history_file, 'r') as f:
                history = json.load(f)
        history.append({
            "timestamp": data["anomaly"].get("timestamp", int(time.time())),
            "cpu_usage": data["anomaly"].get("cpu_usage", "N/A"),
            "analysis": data["analysis"].get("analysis", "No analysis available"),
            "logs": data["analysis"].get("logs", "No logs available"),
            "remediation": data["remediation"].get("action", "No action taken")
        })
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2)
        logging.info("Saved notification to history")
    except Exception as e:
        logging.error(f"Save notification history error: {str(e)}", exc_info=True)

def send_notification(data):
    try:
        if not all(key in data for key in ["anomaly", "analysis", "remediation"]):
            logging.error("send_notification: Missing required keys in data")
            return "Failed: Missing required keys"

        anomaly = data.get("anomaly", {})
        analysis = data.get("analysis", {})
        remediation = data.get("remediation", {})
        remediation_message = remediation.get("action", "No action taken") if isinstance(remediation, dict) else str(remediation)

        webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
        if not webhook_url:
            logging.error("send_notification: SLACK_WEBHOOK_URL not set")
            return "Failed: SLACK_WEBHOOK_URL not set"

        message = (
            f"*Anomaly Detected*\n"
            f"Details: {anomaly.get('cpu_usage', 'N/A')}% CPU usage at {anomaly.get('timestamp', 'N/A')}\n"
            f"*Analysis*\n{analysis.get('analysis', 'No analysis available')}\n"
            f"*Logs*\n{analysis.get('logs', 'No logs available')}\n"
            f"*Remediation*\n{remediation_message}"
        )

        payload = {
            "text": message,
            "username": "DevOpsBot",
            "icon_emoji": ":robot_face:"
        }

        response = requests.post(webhook_url, json=payload)
        if response.status_code == 200:
            logging.info("Notification sent to Slack successfully")
            save_notification_to_history(data)
            return "Sent to Slack"
        else:
            logging.error(f"Failed to send Slack notification: {response.status_code} - {response.text}")
            return f"Failed: {response.status_code} - {response.text}"

    except Exception as e:
        logging.error(f"send_notification error: {str(e)}", exc_info=True)
        return f"Failed: {str(e)}"
