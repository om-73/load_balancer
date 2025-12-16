#!/bin/bash
echo "🔄 Restarting Load Balancer..."

# 1. Find and Kill the running Load Balancer Java Process
pkill -f "com.loadbalancer.LoadBalancer" || true

# 2. Wait a moment
sleep 1

# 3. Start it again (using same command as start_render.sh)
# Ensure bin exists
mkdir -p bin

# Start in background, piping output to log AND stdout
nohup java -Xmx256m -cp bin com.loadbalancer.LoadBalancer 2>&1 | tee -a lb.log &

echo "✅ Load Balancer Restarted (New PID: $!)"
