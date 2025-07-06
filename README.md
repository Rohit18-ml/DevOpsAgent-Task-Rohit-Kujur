DevOps Agent Task - 
This project implements an automated DevOps agent for monitoring, analyzing, and remediating system issues on an AWS EC2 instance running Ubuntu. It uses Docker containers (Prometheus, Loki, Promtail, Ollama, Flask dashboard, and a sample app) to detect CPU spikes, analyze logs with an LLM (tinyllama), perform automated remediation, and send Slack notifications. A dashboard at http://<EC2-public-IP>:5000 displays live metrics, logs, and notification history.
Features

CPU Spike Detection: Monitors CPU usage via Prometheus, flagging >80% as an anomaly.
LLM Log Analysis: Queries logs from Loki, analyzes memory trends via Prometheus, and uses Ollama's tinyllama for insights (e.g., OutOfMemory errors).
Automated Remediation: Restarts the app container when issues like memory leaks are detected.
Notification Dispatch: Sends detailed Slack notifications with anomaly details, logs, and remediation actions.
Dashboard: Flask-based UI showing CPU/memory metrics, incident logs, and notification history.

Prerequisites

AWS EC2 instance (Ubuntu 20.04 or later) with ports 9090 (Prometheus), 3100 (Loki), 9100 (Node Exporter), 11434 (Ollama), 8080 (App), and 5000 (Dashboard) open in the security group.
Docker and Docker Compose installed:sudo apt update
sudo apt install -y docker.io docker-compose
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ubuntu


Git installed:sudo apt install -y git


SSH key configured for GitHub:ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
cat ~/.ssh/id_rsa.pub

Add the public key to GitHub under Settings > SSH and GPG keys.
Slack webhook URL for notifications.

Setup Instructions

Clone the Repository
git clone git@github.com:<your-username>/DevOpsAgentTask-<your-name>.git
cd DevOpsAgentTask-<your-name>


Set Up Environment

Configure the Slack webhook URL:export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/XXX/YYY/ZZZ"
echo "export SLACK_WEBHOOK_URL=$SLACK_WEBHOOK_URL" >> ~/.bashrc
source ~/.bashrc


Create and set permissions for log files:mkdir -p logs
touch logs/test_logs.log logs/opsbot.log
chmod 644 logs/test_logs.log logs/opsbot.log
chown ubuntu:ubuntu logs/test_logs.log logs/opsbot.log




Pull Ollama Model
docker exec ollama ollama pull tinyllama


Start Docker Services
docker-compose -f config/docker-compose.yml up -d --build


Verify Services
docker ps

Ensure containers prometheus, node-exporter, loki, promtail, ollama, app, and dashboard are running.


Demo Commands
Run these commands to demonstrate the DevOps agent in a 15-minute video, showcasing CPU spike detection, LLM analysis, remediation, and notifications.

Verify Directory Structure
ls -l
ls -l config/ agent/ tests/ dashboard/templates/

Expected structure:
config/
  docker-compose.yml
  promtail-config.yml
  prometheus.yml
agent/
  orchestrate.py
  monitor.py
  analyze.py
  remediate.py
  notify.py
tests/
  test_cpu.py
  test_logs.py
dashboard/
  templates/
    index.html
  server.py
logs/
  opsbot.log
  test_logs.log
  notification_history.json


Generate Synthetic Logs
python3 tests/test_logs.py
cat logs/test_logs.log

Expected Output:
2025-07-07 00:XX:XX,XXX - ERROR - OutOfMemory in app
2025-07-07 00:XX:XX,XXX - WARNING - Infinite loop detected in app
Synthetic logs generated


Simulate CPU Spike
python3 tests/test_cpu.py &
top

Expected Output: top shows ~100% CPU usage.

Run the Agent
python3 agent/orchestrate.py

Expected Output:
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
2025-07-07 00:XX:XX,XXX - INFO - Agent cycle completed, sleeping for 30 seconds


View Logs
cat logs/opsbot.log


Access Dashboard

Open http://<EC2-public-IP>:5000 in a browser (e.g., http://54.242.197.161:5000).
Displays:
Live CPU/memory metrics (line chart).
Incident logs (e.g., 2025-07-07 00:XX:XX,XXX - ERROR - OutOfMemory in app).
Notification history table (timestamp, CPU usage, analysis, logs, remediation).
Manual remediation button to restart the app container.


Verify port 5000:aws ec2 authorize-security-group-ingress --group-id <your-security-group-id> --protocol tcp --port 5000 --cidr 0.0.0.0/0




Check Slack Notification

Open your Slack channel to view:*Anomaly Detected*
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


Git Push Issues:
git remote -v
git status
ssh -T git@github.com
cat ~/.ssh/id_rsa.pub



Notes

Replace <your-name> with your actual name (e.g., JohnDoe) and <your-username> with your GitHub username.
Replace <EC2-public-IP> with your EC2 instance’s public IP (e.g., 54.242.197.161).
The repository is hosted at https://github.com/<your-username>/DevOpsAgentTask-<your-name>.
Ensure .gitignore excludes sensitive files:echo -e "logs/\n*.pem\n*.log" > .gitignore
git add .gitignore
git commit -m "Update .gitignore"
git push origin main


For the demo video, mention: “The README in the GitHub repo provides all setup and demo instructions.”
