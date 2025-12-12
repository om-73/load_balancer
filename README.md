# ⚖️ Multi-threaded Load Balancer & Visualizer

A custom implementation of a **Layer 4 Load Balancer** built from scratch using Java Sockets, featuring a real-time terminal visualizer and a web-based control panel.

![Load Balancer Logic](https://placehold.co/600x200?text=Java+Load+Balancer)

## 🚀 Features

- **Java Core**: Multi-threaded Load Balancer using raw `ServerSocket` and `CachedThreadPool`.
- **Round Robin Strategy**: Custom implementation of the Round Robin algorithm.
- **Terminal Visualizer**: Python-based CLI dashboard showing live traffic stats (RPS, Active Connections).
- **Web Dashboard**: A clean HTML/JS interface to "fire" load tests with configurable concurrency.
- **Hybrid Architecture**: Uses UDP signals to sync the Web UI resets with the Terminal Visualizer.

## 🛠 Tech Stack

- **Backend**: Java (No frameworks, pure JDK)
- **Visualizer**: Python (Curses/Rich)
- **Web Server**: Python `http.server` extended
- **Frontend**: Vanilla HTML5/CSS3/JavaScript

## 📋 Prerequisites

- **Java JDK** (11 or higher)
- **Python 3.x**

## 🏃‍♂️ How to Run

1. **Make scripts executable**:
   ```bash
   chmod +x start_all.sh run_demo.sh
   ```

2. **Start the System**:
   ```bash
   ./start_all.sh
   ```
   *This will compile the Java code, start the Mock Backend Servers, launch the Load Balancer, open the Terminal Visualizer, and host the Web Interface.*

3. **Access the Dashboard**:
   Open your browser to: **[http://localhost:8000](http://localhost:8000)**

4. **Fire a Test**:
   - Enter target URL (default: `http://localhost:8080`)
   - Set number of requests and concurrency.
   - Click **FIRE LOAD TEST**. request stats will appear in the web UI, and the terminal will show real-time distribution!

## 📂 Project Structure

```
├── src/main/java    # Java Load Balancer Source
├── visualizer.py    # Python Terminal Visualizer
├── web_server.py    # Python Web Interface Backend
├── index.html       # Web Dashboard Frontend
├── load_generator.py# Python Load Testing Tool
├── start_all.sh     # Main Entry Point (Orchestrator)
└── run_demo.sh      # Helper script for Java compilation/execution
```
