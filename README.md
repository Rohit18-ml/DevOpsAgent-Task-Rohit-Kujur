# 🚀 DevOps Agent Task – Rohit Kujur

This project implements an AI-powered DevOps Agent that monitors CPU usage, analyzes logs using an LLM (Ollama with TinyLlama), performs automated remediation, and sends Slack notifications. It includes a live dashboard to visualize metrics, logs, and actions.

---

## 📆 Features

- **CPU Spike Detection** – Monitors CPU via Prometheus, flags usage >80%.
- **LLM Log Analysis** – Uses Ollama + TinyLlama to analyze logs from Loki (e.g., OOM, infinite loops).
- **Automated Remediation** – Restarts app containers/services when actionable issues are detected.
- **Notification Dispatch** – Sends alerts to Slack with root cause, logs, and remediation actions.
- **Dashboard UI** – Flask-based dashboard on `http://<EC2-IP>:5000` for live monitoring.

---

## ✅ Prerequisites

- AWS EC2 instance (Ubuntu 20.04+)
- Open inbound ports: `9090`, `3100`, `9100`, `11434`, `8080`, `5000`
- Installed: Docker, Docker Compose, Git
- Slack Webhook URL
- SSH key for GitHub (if using Git over SSH)

---

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/DevOpsAgentTask-Rohit-Kujur.git
cd DevOpsAgentTask-Rohit-Kujur
```

### 2. Set Up Environment

```bash
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/XXX/YYY/ZZZ"
echo "export SLACK_WEBHOOK_URL=$SLACK_WEBHOOK_URL" >> ~/.bashrc
source ~/.bashrc
```

### 3. Create Logs Directory

```bash
mkdir -p logs
touch logs/test_logs.log logs/opsbot.log
chmod 644 logs/*.log
chown ubuntu:ubuntu logs/*.log
```

---

### 4. Pull Ollama Model

```bash
docker exec ollama ollama pull tinyllama
```

---

### 5. Start Docker Services

```bash
docker-compose -f config/docker-compose.yml up -d --build
```

---

### 6. Verify Services

```bash
docker ps
```

Ensure the following are running:
- `prometheus`
- `node-exporter`
- `loki`
- `promtail`
- `ollama`
- `app`
- `dashboard`

---

## 🧪 Demo Workflow

### 🔹 Generate Synthetic Logs

```bash
python3 tests/test_logs.py
cat logs/test_logs.log
```

**Expected output:**

```text
ERROR - OutOfMemory in app
WARNING - Infinite loop detected in app
```

---

### 🔹 Simulate CPU Spike

```bash
python3 tests/test_cpu.py &
top
```

**Expected in `top`:** ~100% CPU usage

---

### 🔹 Run the Agent

```bash
python3 agent/orchestrate.py
```

**Expected log output:**

```text
[INFO] Anomaly detected: 100% CPU
[INFO] Logs retrieved from Loki
[INFO] LLM Analysis: OutOfMemory/infinite loop
[INFO] Restarted app container
[INFO] Slack notification sent
```

---

## 📊 Access Dashboard

Open in browser:

```
http://<your-EC2-public-IP>:5000
```

Displays:
- CPU/Memory metrics
- Logs
- Notification history
- Manual remediation button

---

## 🔔 Check Slack

Slack message should contain:

```text
*Anomaly Detected*
Details: 100% CPU at <timestamp>
*Analysis:* Likely OutOfMemory error
*Logs:* ERROR - OutOfMemory in app
*Remediation:* Restarted app container
```

---

## 🚫 Stop Test Processes

```bash
pkill -f "python3 tests/test_cpu.py"
pkill -f "python3 agent/orchestrate.py"
```

---

## 📂 Project Structure

```text
DevOpsAgentTask-Rohit-Kujur/
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
│   ├── server.py
│   └── templates/
│       └── index.html
├── logs/
│   ├── opsbot.log
│   ├── test_logs.log
│   └── notification_history.json
└── README.md
```

---

## 🛠 Troubleshooting

### 🚧 Loki has no logs?

```bash
cat logs/test_logs.log
docker logs promtail
```

Query logs directly:

```bash
curl -G http://localhost:3100/loki/api/v1/query_range \
--data-urlencode 'query={job="varlogs"} |= "ERROR"' \
--data-urlencode "start=$(date --date='5 minutes ago' +%s)000000000" \
--data-urlencode "end=$(date +%s)000000000" \
--data-urlencode 'limit=10'
```

---

### ❌ Dashboard not accessible?

```bash
docker logs dashboard
curl http://<EC2-public-IP>:5000
```

Open port 5000 in security group:

```bash
aws ec2 authorize-security-group-ingress \
--group-id <your-sg-id> \
--protocol tcp \
--port 5000 \
--cidr 0.0.0.0/0
```

---

### 💣 Ollama issues?

```bash
docker logs ollama
docker exec ollama ollama list
docker exec ollama ollama pull tinyllama
```

---

### 🧹 Too many test CPU loops?

```bash
ps aux | grep test_cpu.py
pkill -f "python3 tests/test_cpu.py"
```

---

## 🙌 Final Notes

- Replace `<your-username>` and `<your-name>` accordingly
- Ensure EC2 ports are open for Prometheus, Loki, Ollama, and dashboard
- GitHub repo: `https://github.com/<your-username>/DevOpsAgentTask-<your-name>`

---
