# ⚖️ Advanced Multi-threaded Load Balancer

A production-grade **Layer 4 Load Balancer** built from scratch in Java, featuring **Auto-Scaling**, **Fault Tolerance**, and **Real-Time Visualization**.

![Load Balancer Logic](https://placehold.co/600x200?text=Java+Load+Balancer+v2.0)

## 🚀 Key Features

### 1. 📈 Auto-Scaling ("Port Increase")
- **Intelligent Scaling**: The system monitors **Requests Per Second (RPS)** in real-time.
- **Trigger**: If `Avg RPS > 10`, it automatically spawns a **new backend server** on the next available port (e.g., 9084, 9085...).
- **Cooldown**: Prevents rapid-fire scaling with a 20-second cooldown period.

### 2. 🛡️ Fault Tolerance ("Prevent Failure")
- **Automatic Retries**: If a backend server crashes or disconnects, the LB **automatically retries** the request on a different server (up to 3 times).
- **Fast Failure Detection**: Instantly marks failed servers as `DOWN` to prevent further traffic distribution.
- **Zero Downtime**: Clients experience seamless service even during backend failures.

### 3. 🔌 Multi-Port Listening
- **Architecture**: The Load Balancer listens on **multiple ports simultaneously**: `8080`, `8081`, `8082`, `8083`.
- **Unified Balancing**: Traffic from *any* of these ports is distributed across the *shared* pool of backend servers (9081+).

### 4. 🎛️ Dynamic Control & Metrics
- **Runtime Addition**: Add servers dynamically via the Control Port (8888).
  - `echo "ADD localhost 9090" | nc localhost 8888`
- **Precision Metrics**: Tracks Min/Max RPS and Latency with **timestamps**.
  - Example: `Min Requests: Port 9084 (758) | Avg RPS: 15.2 (at 12:05:01)`

## 🛠 Tech Stack

- **Core**: Java (Multithreaded, Socket Programming)
- **Visualizer**: Python (Real-time Curses Dashboard)
- **Scripting**: Bash (Orchestration)

## 🏃‍♂️ How to Run

1. **Start the System**:
   ```bash
   ./start_all.sh
   ```
   *This compiles the code, starts 3 mock backends (9081-9083), launches the LB (8080-8083), and opens the dashboard.*

2. **Test Auto-Scaling**:
   ```bash
   # Blast the server with traffic
   while true; do curl http://localhost:8080 > /dev/null; done
   ```
   *Watch the dashboard: You will see "🚀 Scaling up!" and a new backend (9084) will appear.*

3. **Test Fault Tolerance**:
   ```bash
   # Kill a backend (e.g., on port 9081)
   kill <PID_OF_9081>
   ```
   *Send a request. It will succeed! The logs will show a seamless retry to another server.*

## 📂 Project Structure

```
├── src/main/java    # Java Source Code
│   ├── LoadBalancer.java       # Main Entry Point & Control Port
│   ├── HealthCheckService.java # Auto-Scaling & Monitoring Logic
│   ├── ClientHandler.java      # Fault Tolerant Request Forwarding
│   ├── BackendServer.java      # Server State & Metrics
│   └── ...
├── visualizer.py    # Python Dashboard
├── mock_server.py   # Python Mock Backend
└── start_all.sh     # One-click startup
```
