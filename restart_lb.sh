#!/bin/bash
echo "🔄 Hot Swapping Load Balancer..."

# Find PID of Java LoadBalancer process
LBPID=$(pgrep -f "com.loadbalancer.LoadBalancer")

if [ -n "$LBPID" ]; then
    echo "Killing old process $LBPID..."
    kill -9 $LBPID
else
    echo "No running Load Balancer found."
fi

# Restart it (using same settings as start_render.sh)
# Ensure binary dir exists
mkdir -p bin

echo "Starting new Load Balancer..."
# Launch in background, use tee for logs, limit memory
nohup java -Xmx256m -cp bin com.loadbalancer.LoadBalancer 2>&1 | tee lb.log &

echo "✅ Load Balancer Restarted with New Strategy!"
