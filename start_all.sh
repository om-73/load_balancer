#!/bin/bash

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping all services..."
    kill $WEB_PID 2>/dev/null
    # run_demo.sh handles its own cleanup of java/python processes usually,
    # but we can explicitly call pkill just to be safe if run_demo failed.
    pkill -P $$ # Kill children of this script
    
    # Also standard cleanup 
    pkill -f "run_demo.sh"
    pkill -f "web_server.py"
    pkill -f "java.*LoadBalancer"
    pkill -f "python3.*mock_server.py"
    
    echo "✅ All services stopped."
    exit
}

# Trap Ctrl+C (SIGINT) and SIGTERM
trap cleanup SIGINT SIGTERM

echo "🚀 Starting Full Stack Load Balancer Demo..."

# 1. Kill old stuff first to be clean
pkill -f "run_demo.sh"
pkill -f "web_server.py"
pkill -f "java.*LoadBalancer"
pkill -f "python3.*mock_server.py"
sleep 1

# 2. Start Web Server in Background
echo "🌍 Starting Web Interface..."
python3 web_server.py > /dev/null 2>&1 &
WEB_PID=$!
echo "   -> Web Server running (PID: $WEB_PID)"

# 3. Start Load Balancer & Visualizer (Foreground)
# We run this in foreground so the visualizer takes over the terminal
echo "⚖️  Starting Load Balancer System..."
bash run_demo.sh

# If run_demo.sh exits, we cleanup
cleanup
