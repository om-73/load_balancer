#!/bin/bash
echo "♻️ Restarting Load Balancer to apply new Strategy..."

# Find and kill the MAIN LoadBalancer java process (not the mock servers or web server)
pkill -f "java -cp bin com.loadbalancer.LoadBalancer"

# Compile everything just in case
javac -d bin src/main/java/com/loadbalancer/*.java

# Start it back up in background, logging to lb.log
nohup java -cp bin com.loadbalancer.LoadBalancer > lb.log 2>&1 &

echo "✅ Restarted!"
