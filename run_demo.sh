#!/bin/bash
set -e

# Cleanup function to kill background processes on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $PID1 $PID2 $PID3 $LBPID $TAIL_PID 2>/dev/null || true
    rm backend1.log backend2.log backend3.log 2>/dev/null || true
    # We keep lb.log for the web dashboard to consume even if this script stops
    # rm lb.log 2>/dev/null || true
}
trap cleanup EXIT

# Compile
echo "Compiling..."
javac src/main/java/com/loadbalancer/*.java

# Start backends
echo "Starting 3 backend servers on ports 9081, 9082, 9083..."
python3 mock_server.py 9081 > backend1.log 2>&1 &
PID1=$!
python3 mock_server.py 9082 > backend2.log 2>&1 &
PID2=$!
python3 mock_server.py 9083 > backend3.log 2>&1 &
PID3=$!

# Start LB
echo "Starting Load Balancer..."
# Read Strategy from file (if exists), default to AdaptiveStrategy
STRATEGY_CLASS="com.loadbalancer.AdaptiveStrategy"
if [ -f "current_strategy.txt" ]; then
    STRATEGY_CLASS=$(cat current_strategy.txt)
    echo "🔄 Configuration found: Using $STRATEGY_CLASS"
fi

# Start Load Balancer with dynamic strategy
# Pass 8080..8083 ports if needed, but main() handles defaults
# We pipe stderr/stdout to lb.log AND also to the visualizer
# But python buffering might be an issue. Using unbuffer (expect) would be nice, but maybe not available.
# We will just tail -f the log file into the visualizer.
java -cp src/main/java -Dstrategy.class="$STRATEGY_CLASS" com.loadbalancer.LoadBalancer > lb.log 2>&1 &
LBPID=$!

# Wait for startup
sleep 2

# Stream LB logs to visualizer
tail -f lb.log | python3 visualizer.py &
TAIL_PID=$!

# Give visualizer a moment to clear screen
sleep 1

# Send requests continuously in background to animate the chart
(
    for i in {1..30}; do
        curl -s http://localhost:8080 > /dev/null
        sleep 0.2
    done
) &

# Bring visualizer to foreground (wait for the background curl loop essentially)
wait $TAIL_PID


