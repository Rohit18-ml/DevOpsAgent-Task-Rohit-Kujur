import json
import logging
import os
import subprocess

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

def remediate_service(analysis):
    try:
        analysis = json.loads(analysis) if isinstance(analysis, str) else analysis
        if not analysis.get("actionable", False):
            logging.info("No actionable remediation identified")
            return {"action": "No action taken", "stable": False}

        if "OutOfMemory" in analysis.get("logs", "") or "Infinite loop" in analysis.get("logs", ""):
            result = subprocess.run(["docker", "restart", "app"], capture_output=True, text=True)
            if result.returncode == 0:
                logging.info("Remediation: Restarted app container")
                return {"action": "Restarted app container", "stable": True}
            else:
                logging.error(f"Remediation failed: {result.stderr}")
                return {"action": f"Failed to restart app container: {result.stderr}", "stable": False}
        else:
            logging.info("No actionable remediation identified")
            return {"action": "No action taken", "stable": False}

    except Exception as e:
        logging.error(f"Remediate error: {str(e)}", exc_info=True)
        return {"action": f"Remediation failed: {str(e)}", "stable": False}
