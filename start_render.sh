#!/bin/bash
set -e

echo "🚀 Starting Load Balancer System on Render..."

# 1. Start Mock Backend Servers (Background)
echo "Starting Mock Servers..."
python3 mock_server.py 9081 > backend1.log 2>&1 &
python3 mock_server.py 9082 > backend2.log 2>&1 &
python3 mock_server.py 9083 > backend3.log 2>&1 &
echo "✅ Mock Servers Started"

# 2. Start Java Load Balancer (Background)
echo "Starting Java Load Balancer..."
# Ensure bin directory exists and classes are compiled (Dockerfile does this, but safety check)
mkdir -p bin
java -cp bin com.loadbalancer.LoadBalancer > lb.log 2>&1 &
echo "✅ Load Balancer Started"

# 3. Start Web Server (Foreground)
# This keeps the container alive and serves the UI/API
echo "🌍 Starting Web Interface on port $PORT..."
python3 web_server.py
