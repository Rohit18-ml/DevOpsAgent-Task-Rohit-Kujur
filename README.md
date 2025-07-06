DevOps Agent Task - 
This project implements a DevOps agent that monitors CPU usage, analyzes logs using an LLM (Ollama with tinyllama), performs automated remediation, and sends Slack notifications. The system runs on an AWS EC2 instance (Ubuntu) and uses Docker containers for Prometheus, Loki, Promtail, Ollama, a Flask dashboard, and a sample app. A dashboard at http://<EC2-public-IP>:5000 displays live metrics, logs, and notification history.
Features

CPU Spike Detection: Monitors CPU usage via Prometheus, flagging usage >80% as an anomaly.
LLM Log Analysis: Queries logs from Loki and uses Ollama's tinyllama to analyze issues (e.g., OutOfMemory errors, memory trends).
Automated Remediation: Restarts the app container when actionable issues are detected.
Notification Dispatch: Sends detailed alerts to Slack with anomaly details, logs, and remediation actions.
Dashboard: Flask-based UI showing CPU/memory metrics, logs, and notification history.

Prerequisites

AWS EC2 instance (Ubuntu 20.04 or later) with ports 9090 (Prometheus), 3100 (Loki), 9100 (Node Exporter), 11434 (Ollama), 8080 (App), and 5000 (Dashboard) open.
Docker and Docker Compose installed.
Git installed.
SSH key configured for GitHub.
Slack webhook URL for notifications.

Setup Instructions

Clone the Repository
git clone git@github.com:<your-username>/DevOpsAgentTask-<your-name>.git
cd DevOpsAgentTask-<your-name>


Set Up Environment

Set the Slack webhook URL:export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/XXX/YYY/ZZZ"
echo "export SLACK_WEBHOOK_URL=$SLACK_WEBHOOK_URL" >> ~/.bashrc


Ensure log directory and permissions:mkdir -p logs
touch logs/test_logs.log logs/opsbot.log
chmod 644 logs/test_logs.log logs/opsbot.log
chown ubuntu:ubuntu logs/test_logs.log logs/opsbot.log




Pull Ollama Model
docker exec ollama ollama pull tinyllama


Start Docker Services
docker-compose -f config/docker-compose.yml up -d --build


Verify Services
docker ps

Ensure prometheus, node-exporter, loki, promtail, ollama, app, and dashboard are running.


Demo Commands
Run these commands to demonstrate the DevOps agent in action (for a 15-minute demo video).

Generate Synthetic Logs
python3 tests/test_logs.py
cat logs/test_logs.log

Output:
2025-07-07 00:XX:XX,XXX - ERROR - OutOfMemory in app
2025-07-07 00:XX:XX,XXX - WARNING - Infinite loop detected in app
Synthetic logs generated


Simulate CPU Spike
python3 tests/test_cpu.py &
top

Output: Shows ~100% CPU usage in top.

Run the Agent
python3 agent/orchestrate.py

Output:
2025-07-07 00:XX:XX,XXX - INFO - Starting agent workflow
2025-07-07 00:XX:XX,XXX - INFO - CPU Usage: 100.00%, Memory Usage: 20.XX%
2025-07-07 00:XX:XX,XXX - INFO - Anomaly detected: {'anomaly_detected': True, 'cpu_usage': 100.0, 'memory_usage': 20.XX, 'timestamp': 175190XXXX}
2025-07-07 00:XX:XX,XXX - INFO - [DEBUG] Querying Loki (attempt 1): http://localhost:3100/loki/api/v1/query_range?query={job="varlogs"} |= "ERROR"&start=175190XXXX&end=175190XXXX&limit=100
2025-07-07 00:XX:XX,XXX - INFO - [DEBUG] Logs retrieved: ['2025-07-07 00:XX:XX,XXX - ERROR - OutOfMemory in app']
2025-07-07 00:XX:XX,XXX - INFO - Log analysis completed: {'logs': '2025-07-07 00:XX:XX,XXX - ERROR - OutOfMemory in app', 'analysis': 'Possible causes for high CPU usage include an OutOfMemory error or infinite loop. Memory usage over the last hour: avg 15.XX%, current 20.XX%, trend: increasing. High memory usage detected. Suggest setting Docker memory limits and investigating memory leaks. Suggested remediation: Restart the app container and investigate the application code for memory leaks or infinite loops.', 'actionable': True}
2025-07-07 00:XX:XX,XXX - INFO - Remediation: Restarted app container
2025-07-07 00:XX:XX,XXX - INFO - Notification sent to Slack successfully
2025-07-07 00:XX:XX,XXX - INFO - Saved notification to history
2025-07-07 00:XX:XX,XXX - INFO - LLM Summary: High CPU usage (100%) and increasing memory usage (current 20.XX%) indicate a memory leak or infinite loop. Restarted app container to mitigate. Recommend setting Docker memory limits to 512MB and analyzing application code for inefficiencies.


View Logs
cat logs/opsbot.log


Access Dashboard

Open http://<EC2-public-IP>:5000 in a browser.
Shows CPU/memory metrics, logs, and notification history.
Use the remediation button to manually restart the app container.


Check Slack

Open your Slack channel to view the notification:*Anomaly Detected*
Details: 100.0% CPU usage at 175190XXXX
*Analysis*
Possible causes for high CPU usage include an OutOfMemory error or infinite loop. Memory usage over the last hour: avg 15.XX%, current 20.XX%, trend: increasing. High memory usage detected. Suggest setting Docker memory limits and investigating memory leaks. Suggested remediation: Restart the app container and investigate the application code for memory leaks or infinite loops.
*Logs*
2025-07-07 00:XX:XX,XXX - ERROR - OutOfMemory in app
*Remediation*
Restarted app container




Stop Processes
pkill -f "python3 tests/test_cpu.py"
pkill -f "python3 agent/orchestrate.py"



Project Structure
DevOpsAgentTask-<your-name>/
├── config/
│   ├── docker-compose.yml
│   ├── promtail-config.yml
│   └── prometheus.yml
├── agent/
│   ├── orchestrate.py
│   ├── monitor.py
│   ├── analyze.py
│   ├── remediate.py
│   └── notify.py
├── tests/
│   ├── test_cpu.py
│   └── test_logs.py
├── dashboard/
│   ├── templates/
│   │   └── index.html
│   └── server.py
├── logs/
│   ├── opsbot.log
│   ├── test_logs.log
│   └── notification_history.json
└── README.md

Troubleshooting

No Logs in Loki:
cat logs/test_logs.log
docker logs promtail
curl -G http://localhost:3100/loki/api/v1/query_range --data-urlencode 'query={job="varlogs"} |= "ERROR"' --data-urlencode 'start=$(date --date="5 minutes ago" +%s)000000000' --data-urlencode 'end=$(date +%s)000000000' --data-urlencode 'limit=10'


Dashboard Not Accessible:
docker logs dashboard
curl http://<EC2-public-IP>:5000
aws ec2 authorize-security-group-ingress --group-id <your-security-group-id> --protocol tcp --port 5000 --cidr 0.0.0.0/0


Ollama LLM Failure:
docker logs ollama
docker exec ollama ollama list
docker exec ollama ollama pull tinyllama


Multiple test_cpu.py Instances:
ps aux | grep test_cpu.py
pkill -f "python3 tests/test_cpu.py"



Notes

Replace <your-name> and <your-username> with your actual name and GitHub username.
Ensure the EC2 security group allows inbound traffic on ports 5000, 9090, 3100, 9100, 11434, and 8080.
The GitHub repository is at https://github.com/<your-username>/DevOpsAgentTask-<your-name>.
DevOps Agent Task - 
This project implements a DevOps agent that monitors CPU usage, analyzes logs using an LLM (Ollama with tinyllama), performs automated remediation, and sends Slack notifications. The system runs on an AWS EC2 instance (Ubuntu) and uses Docker containers for Prometheus, Loki, Promtail, Ollama, a Flask dashboard, and a sample app. A dashboard at http://<EC2-public-IP>:5000 displays live metrics, logs, and notification history.
Features

CPU Spike Detection: Monitors CPU usage via Prometheus, flagging usage >80% as an anomaly.
LLM Log Analysis: Queries logs from Loki and uses Ollama's tinyllama to analyze issues (e.g., OutOfMemory errors, memory trends).
Automated Remediation: Restarts the app container when actionable issues are detected.
Notification Dispatch: Sends detailed alerts to Slack with anomaly details, logs, and remediation actions.
Dashboard: Flask-based UI showing CPU/memory metrics, logs, and notification history.

Prerequisites

AWS EC2 instance (Ubuntu 20.04 or later) with ports 9090 (Prometheus), 3100 (Loki), 9100 (Node Exporter), 11434 (Ollama), 8080 (App), and 5000 (Dashboard) open.
Docker and Docker Compose installed.
Git installed.
SSH key configured for GitHub.
Slack webhook URL for notifications.

Setup Instructions

Clone the Repository
git clone git@github.com:<your-username>/DevOpsAgentTask-<your-name>.git
cd DevOpsAgentTask-<your-name>


Set Up Environment

Set the Slack webhook URL:export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/XXX/YYY/ZZZ"
echo "export SLACK_WEBHOOK_URL=$SLACK_WEBHOOK_URL" >> ~/.bashrc


Ensure log directory and permissions:mkdir -p logs
touch logs/test_logs.log logs/opsbot.log
chmod 644 logs/test_logs.log logs/opsbot.log
chown ubuntu:ubuntu logs/test_logs.log logs/opsbot.log




Pull Ollama Model
docker exec ollama ollama pull tinyllama


Start Docker Services
docker-compose -f config/docker-compose.yml up -d --build


Verify Services
docker ps

Ensure prometheus, node-exporter, loki, promtail, ollama, app, and dashboard are running.


Demo Commands
Run these commands to demonstrate the DevOps agent in action (for a 15-minute demo video).

Generate Synthetic Logs
python3 tests/test_logs.py
cat logs/test_logs.log

Output:
2025-07-07 00:XX:XX,XXX - ERROR - OutOfMemory in app
2025-07-07 00:XX:XX,XXX - WARNING - Infinite loop detected in app
Synthetic logs generated


Simulate CPU Spike
python3 tests/test_cpu.py &
top

Output: Shows ~100% CPU usage in top.

Run the Agent
python3 agent/orchestrate.py

Output:
2025-07-07 00:XX:XX,XXX - INFO - Starting agent workflow
2025-07-07 00:XX:XX,XXX - INFO - CPU Usage: 100.00%, Memory Usage: 20.XX%
2025-07-07 00:XX:XX,XXX - INFO - Anomaly detected: {'anomaly_detected': True, 'cpu_usage': 100.0, 'memory_usage': 20.XX, 'timestamp': 175190XXXX}
2025-07-07 00:XX:XX,XXX - INFO - [DEBUG] Querying Loki (attempt 1): http://localhost:3100/loki/api/v1/query_range?query={job="varlogs"} |= "ERROR"&start=175190XXXX&end=175190XXXX&limit=100
2025-07-07 00:XX:XX,XXX - INFO - [DEBUG] Logs retrieved: ['2025-07-07 00:XX:XX,XXX - ERROR - OutOfMemory in app']
2025-07-07 00:XX:XX,XXX - INFO - Log analysis completed: {'logs': '2025-07-07 00:XX:XX,XXX - ERROR - OutOfMemory in app', 'analysis': 'Possible causes for high CPU usage include an OutOfMemory error or infinite loop. Memory usage over the last hour: avg 15.XX%, current 20.XX%, trend: increasing. High memory usage detected. Suggest setting Docker memory limits and investigating memory leaks. Suggested remediation: Restart the app container and investigate the application code for memory leaks or infinite loops.', 'actionable': True}
2025-07-07 00:XX:XX,XXX - INFO - Remediation: Restarted app container
2025-07-07 00:XX:XX,XXX - INFO - Notification sent to Slack successfully
2025-07-07 00:XX:XX,XXX - INFO - Saved notification to history
2025-07-07 00:XX:XX,XXX - INFO - LLM Summary: High CPU usage (100%) and increasing memory usage (current 20.XX%) indicate a memory leak or infinite loop. Restarted app container to mitigate. Recommend setting Docker memory limits to 512MB and analyzing application code for inefficiencies.


View Logs
cat logs/opsbot.log


Access Dashboard

Open http://<EC2-public-IP>:5000 in a browser.
Shows CPU/memory metrics, logs, and notification history.
Use the remediation button to manually restart the app container.


Check Slack

Open your Slack channel to view the notification:*Anomaly Detected*
Details: 100.0% CPU usage at 175190XXXX
*Analysis*
Possible causes for high CPU usage include an OutOfMemory error or infinite loop. Memory usage over the last hour: avg 15.XX%, current 20.XX%, trend: increasing. High memory usage detected. Suggest setting Docker memory limits and investigating memory leaks. Suggested remediation: Restart the app container and investigate the application code for memory leaks or infinite loops.
*Logs*
2025-07-07 00:XX:XX,XXX - ERROR - OutOfMemory in app
*Remediation*
Restarted app container




Stop Processes
pkill -f "python3 tests/test_cpu.py"
pkill -f "python3 agent/orchestrate.py"



Project Structure
DevOpsAgentTask-<your-name>/
├── config/
│   ├── docker-compose.yml
│   ├── promtail-config.yml
│   └── prometheus.yml
├── agent/
│   ├── orchestrate.py
│   ├── monitor.py
│   ├── analyze.py
│   ├── remediate.py
│   └── notify.py
├── tests/
│   ├── test_cpu.py
│   └── test_logs.py
├── dashboard/
│   ├── templates/
│   │   └── index.html
│   └── server.py
├── logs/
│   ├── opsbot.log
│   ├── test_logs.log
│   └── notification_history.json
└── README.md

