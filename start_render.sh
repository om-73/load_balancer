#!/bin/bash
set -e

echo "🚀 Starting Load Balancer System on Render..."

# 1. Start Mock Backend Servers (Background)
echo "Starting Mock Servers..."
python3 mock_server.py 9081 2>&1 | tee backend1.log &
python3 mock_server.py 9082 2>&1 | tee backend2.log &
python3 mock_server.py 9083 2>&1 | tee backend3.log &
echo "✅ Mock Servers Started"

# 2. Start Java Load Balancer (Background)
echo "Starting Java Load Balancer..."
# Ensure bin directory exists and classes are compiled (Dockerfile does this, but safety check)
mkdir -p bin
# pipe logs to file AND stdout so they show up in Render Dashboard
java -cp bin com.loadbalancer.LoadBalancer 2>&1 | tee lb.log &
echo "✅ Load Balancer Started"

# 3. Start Web Server (Foreground)
# This keeps the container alive and serves the UI/API
echo "🌍 Starting Web Interface on port $PORT..."
python3 web_server.py
