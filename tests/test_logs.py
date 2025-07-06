import time
import logging
import os

# Setup logging
log_dir = "/home/ubuntu/devops-agent/logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, 'test_logs.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def generate_synthetic_logs():
    logging.error("OutOfMemory in app")
    logging.warning("Infinite loop detected in app")
    print("Synthetic logs generated")

if __name__ == "__main__":
    generate_synthetic_logs()
