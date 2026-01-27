# ⚡️ Advanced Load Balancer (v3.3)

A cloud-ready **Layer 4 Load Balancer** featuring a **Real-Time Web Dashboard**, **Adaptive Load Balancing Strategies**, and **Built-in Port Scanner**.

![Dashboard Preview](https://placehold.co/800x400?text=Web+Dashboard+v3.3)

## 🚀 New in v3.0

*   **🖥️ Web Dashboard**: A beautiful, real-time HTML5/JS interface to monitor traffic, response times, and server health.
*   **🧠 Adaptive Strategy**: Load balancing based on **Least Connections** and **Latency Constraints**, not just Round Robin.
*   **🔍 Port Scanner**: Built-in tool to scan external hosts for open ports directly from the UI.
*   **🛡️ Robust Logging**: Persistent logs (`lb.log`) that survive restarts for historical analysis.

---

## 🏗 Architecture

The system consists of three main components:

1.  **Java Load Balancer**: Multi-threaded core parsing traffic on `localhost:8080`.
    *   *Strategies*: Round Robin, Adaptive (Least Conn).
    *   *Fault Tolerance*: Retries failed requests automatically.
2.  **Python Web Server**: Serves the dashboard (`localhost:8000`) and provides a JSON API (`/stats`, `/run-test`) by parsing the load balancer logs in real-time.
3.  **Frontend**: A responsive web app (`index.html`) using Vanilla JS for zero-dependency speed.

---

## 🏃‍♂️ Quick Start

### Prerequisites
*   Java (JDK 8+)
*   Python 3
*   Bash (Mac/Linux)

### One-Click Launch
```bash
./start_all.sh
```

This will:
1.  Compile the Java Load Balancer.
2.  Start 3 mock backend servers (Python) on ports 9081, 9082, 9083.
3.  Launch the Load Balancer on port 8080.
4.  Start the Web Dashboard on port 8000.

**👉 Open [http://localhost:8000](http://localhost:8000) to view the dashboard.**

---

## 🕹 features & Usage

### 1. 🔥 Load Testing
*   Use the **"Load Launcher"** card on the dashboard.
*   Set **Total Requests** (e.g., 1000) and **Concurrency** (e.g., 50).
*   Click **FIRE LOAD TEST**.
*   *Watch the bars dance!*

### 2. 📊 Live Monitoring
*   **RPS (Requests Per Second)**: Real-time throughput.
*   **Backend Distribution**: Visual progress bars showing how traffic is split.
    *   *Note: In Adaptive Mode, faster servers get more traffic!*
*   **Recent Activity**: Live stream of "Forwarding..." events.

### 3. 🔌 Port Scanning
*   Enter a domain (e.g., `google.com`) in the **"Port Scanner"** card.
*   Click **SCAN PORTS**.
*   The system will check common ports (80, 443, 21, 22, etc.) and report status.

### 4. 🎛️ Control
*   **Disconnect/Pause**: Toggle the button in the header to pause dashboard updates.
*   **Debug Mode**: If things go wrong, the dashboard dumps raw JSON data for easy debugging.

---

## 📂 Project Structure

```bash
├── src/main/java/com/loadbalancer
│   ├── LoadBalancer.java       # Main Loop & Socket Handling
│   ├── AdaptiveStrategy.java   # Intelligent Routing Logic
│   ├── ClientHandler.java      # Request Forwarding & Logging
│   └── PortScanner.java        # Scanner Utility
├── web_server.py               # Backend API & Static Server
├── index.html                  # Frontend Dashboard
├── load_generator.py           # Load Testing Tool
├── run_demo.sh                 # Orchestrator
└── start_all.sh                # Entry Point
```

---

## 🤝 Contributing
1.  Fork the repo.
2.  Run `./start_all.sh` to test your changes.
3.  Submit a Pull Request.

---


