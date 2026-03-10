# ⚡️ Advanced Load Balancer (v3.5)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Java Version](https://img.shields.io/badge/Java-17%2B-blue)](https://www.oracle.com/java/technologies/downloads/)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Build Status](https://img.shields.io/badge/Build-Passing-brightgreen)]()

A high-performance, cloud-ready **Layer 4 Load Balancer** built with Java and Python. It features a **Real-Time Web Dashboard**, **Adaptive Load Balancing Strategies**, and a **Built-in Port Scanner**.

![Dashboard Preview](https://placehold.co/800x400?text=Web+Dashboard+v3.5)

---

## ✨ Features

- **🖥️ Real-Time Dashboard**: Monitor traffic, RPS (Requests Per Second), and server health with zero-latency updates.
- **🧠 Smart Routing**: Multiple dynamic load balancing strategies built into the core:
  - Adaptive Load Balancing (Latency-aware & Least Connections combined)
  - Round Robin Strategy
  - Consistent Hashing Strategy
  - Custom Strategy Hot-reloading
- **🛠️ Extensible Architecture**: Upload and hot-reload custom Java load balancing strategies via the UI.
- **🔍 Integrated Port Scanner**: Diagnose connectivity issues directly from the dashboard via the backend API.
- **🐳 Docker Ready**: Seamlessly deployable on Render, Vercel, AWS, or any Docker-compatible environment.
- **📊 Comprehensive Logging & Visualization**: Detailed logs (`lb.log`) combined with a custom CLI `visualizer.py` for real-time terminal traffic tracking.

---

## 🏗 System Architecture

The project follows a hybrid multi-language architecture:

1.  **Core (Java)**: The heavy lifter. A multi-threaded socket-level load balancer handling raw TCP traffic. Uses various routing strategies (`AdaptiveStrategy`, `RoundRobinStrategy`, etc.) and a `HealthCheckService`.
2.  **API Layer (Python)**: Provides JSON interfaces for the frontend dashboard. Supports local running via `web_server.py` and cloud serverless deployment via the `api/` directory (Vercel ready).
3.  **Frontend (Vanilla JS)**: Responsive, zero-dependency dashboards (`index.html` and `index_neon.html`). Features CSS Glassmorphism or sleek neon aesthetics.

---

## 🚀 Quick Start

### Local Development

**Prerequisites:**
- Java JDK 17+
- Python 3.11+
- Bash environment (Linux/macOS)

**Steps:**
1. Clone the repository.
2. Run the one-click startup script (starts backends, load balancer, visualizer, and web dashboard):
   ```bash
   ./start_all.sh
   ```
3. Open [http://localhost:8000](http://localhost:8000) in your browser.
4. (Optional) Run just the CLI demo without the web server:
   ```bash
   ./run_demo.sh
   ```

---

## 📡 API Endpoints

The Python backend provides the following JSON endpoints (available via `web_server.py` or the `api/` Vercel functions):

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/stats` | Returns real-time metrics (RPS, count, backend health). |
| `POST` | `/api/run-test` | Triggers a load test (Params: `requests`, `concurrency`). |
| `POST` | `/api/scan` | Scans common ports on a target host (Params: `host`). |
| `POST` | `/api/upload-strategy` | Hot-reloads custom Java strategy code. |
| `GET` | `/api/network-ip` | Retrieves the server's local network IP. |

*(Note: When running locally via `web_server.py`, endpoints might not have the `/api/` prefix depending on environment configuration. Vercel maps everything under `/api/`.)*

---

## 🐳 Deployment

### Render (Docker - Core Services)
This project is configured for one-click deployment on [Render](https://render.com) utilizing the included Docker image.

1. Connect your GitHub repo to Render.
2. Use the following settings:
   - **Environment**: Docker
   - **Plan**: Free / Individual
3. The `render.yaml` and `Dockerfile` will handle building both the Java and Python layers.

### Vercel (Serverless - Frontend & API)
The frontend and Python APIs can also be easily deployed to Vercel via Serverless functions:
1. Import the project into Vercel.
2. The `vercel.json` ensures correctly mapped static rewrites to `index.html`.
3. The serverless functions are automatically loaded from the `api/` directory.

### Docker Manual
```bash
docker build -t load-balancer .
docker run -p 8000:8000 load-balancer
```

---

## 📂 Project Structure

```text
├── src/main/java/com/loadbalancer
│   ├── LoadBalancer.java          # Core TCP routing engine
│   ├── ClientHandler.java         # Request processor & logger
│   ├── BackendServer.java         # Backend instance representation
│   ├── HealthCheckService.java    # Uptime tracker
│   ├── PortScanner.java           # Networking utility
│   ├── AdaptiveStrategy.java      # Smart routing logic
│   ├── RoundRobinStrategy.java    # Basic routing logic
│   ├── ConsistentHashStrategy.java# Distributed hash routing
│   └── CustomStrategy.java        # Hot-reloadable template
├── api/                           # Vercel Serverless Functions
│   ├── scan.py                    
│   ├── stats.py                   
│   └── run_test.py                
├── web_server.py                  # Local Python server wrapper
├── visualizer.py                  # Local CLI log visualizer
├── index.html                     # Main Dashboard
├── index_neon.html                # Alternative Neon Dashboard
├── load_generator.py              # Benchmarking tool
├── Dockerfile                     # Containerization config
├── render.yaml                    # Render Blueprint
├── vercel.json                    # Vercel Deployment config
├── start_all.sh                   # Full stack startup script
└── run_demo.sh                    # CLI-only load test visualization
```

---

## 🛠 Tech Stack

- **Frontend**: HTML5, Vanilla CSS (Glassmorphism & Neon options), JavaScript (Fetch API).
- **Backend**: Python 3.11 (HTTP Server, Vercel Serverless).
- **Core Ops**: Java 17 (Socket Programming, Multi-threading).
- **CI/CD**: Docker, Render, Vercel.

---

## 🤝 Contributing

1. Fork the project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.
