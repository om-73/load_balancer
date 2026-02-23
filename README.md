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
- **🧠 Smart Routing**: Adaptive strategies including **Least Connections** and **Latency-Aware** routing.
- **🛠️ Extensible Architecture**: Upload and hot-reload custom Java load balancing strategies via the UI.
- **🔍 Integrated Port Scanner**: Diagnose connectivity issues directly from the dashboard.
- **🐳 Docker Ready**: Seamlessly deployable on Render, AWS, or any Docker-compatible environment.
- **📊 Comprehensive Logging**: Detailed logs (`lb.log`) for historical analysis and debugging.

---

## 🏗 System Architecture

The project follows a hybrid multi-language architecture:

1.  **Core (Java)**: The heavy lifter. A multi-threaded socket-level load balancer handling raw TCP traffic.
2.  **API Layer (Python)**: A lightweight `http.server` that parses real-time logs, calculates metrics, and provides an interface for the frontend.
3.  **Frontend (Vanilla JS)**: A responsive, zero-dependency dashboard using CSS Glassmorphism and modern UI patterns.

---

## 🚀 Quick Start

### Local Development

**Prerequisites:**
- Java JDK 17+
- Python 3.11+
- Bash environment (Linux/macOS)

**Steps:**
1. Clone the repository.
2. Run the one-click startup script:
   ```bash
   ./start_all.sh
   ```
3. Open [http://localhost:8000](http://localhost:8000) in your browser.

---

## 📡 API Endpoints

The Python backend provides the following JSON endpoints:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/stats` | Returns real-time metrics (RPS, count, backend health). |
| `POST` | `/run-test` | Triggers a load test (Params: `requests`, `concurrency`). |
| `POST` | `/scan-ports` | Scans common ports on a target host (Params: `host`). |
| `POST` | `/upload-strategy` | Hot-reloads custom Java strategy code. |
| `GET` | `/network-ip` | Retrieves the server's local network IP. |

---

## 🐳 Deployment

### Render (Recommended)
This project is configured for one-click deployment on [Render](https://render.com).

1. Connect your GitHub repo to Render.
2. Use the following settings:
   - **Environment**: Docker
   - **Plan**: Free / Individual
3. The `render.yaml` and `Dockerfile` will handle the rest.

### Docker Manual
```bash
docker build -t load-balancer .
docker run -p 8000:8000 load-balancer
```

---

## 📂 Project Structure

```text
├── src/main/java/com/loadbalancer
│   ├── LoadBalancer.java       # Core TCP routing engine
│   ├── AdaptiveStrategy.java   # Smart routing logic
│   ├── ClientHandler.java      # Request processor & logger
│   └── PortScanner.java        # Networking utility
├── web_server.py               # Python API & Static Server
├── index.html                  # Dashboard Frontend
├── load_generator.py           # Benchmarking tool
├── Dockerfile                  # Containerization config
├── render.yaml                 # Render Blueprint
└── start_all.sh                # Local entry point
```

---

## 🛠 Tech Stack

- **Frontend**: HTML5, Vanilla CSS (Glassmorphism), JavaScript (Fetch API).
- **Backend**: Python 3.11 (HTTP Server, Subprocess management).
- **Core Ops**: Java 17 (Socket Programming, Multi-threading).
- **CI/CD**: Docker, Render.

---

## 🤝 Contributing

1. Fork the project.
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

---

