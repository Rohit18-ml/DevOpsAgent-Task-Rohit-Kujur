from flask import Flask
import logging
import time
import random
import threading
import os

app = Flask(__name__)

# Log to a file for traceability
logging.basicConfig(
    filename='/var/log/app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.route('/')
def home():
    logging.info("Received request to home endpoint")
    return "Hello from App"

@app.route('/stress')
def stress():
    logging.warning("Simulating CPU spike")

    def burn_cpu():
        end = time.time() + 20  # Run for 20 seconds
        while time.time() < end:
            _ = [random.random() for _ in range(1000000)]

    threads = []
    for _ in range(os.cpu_count()):  # One thread per CPU core
        t = threading.Thread(target=burn_cpu)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    logging.error("High CPU usage detected in stress endpoint")
    return "CPU stress test completed"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
