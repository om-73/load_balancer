package com.loadbalancer;

import java.util.ArrayList;
import java.util.List;

public class BackendServer {
    private String host;
    private int port;
    private boolean isHealthy;
    private long lastCheckTime;
    private int successfulChecks;
    private int failedChecks;
    private int consecutiveFailures;
    private List<Long> failureTimestamps;
    private java.util.concurrent.atomic.AtomicInteger requestCount;
    private java.util.concurrent.atomic.AtomicInteger activeRequests;

    // Metrics
    private int maxRPS;
    private long maxRPSTimestamp;
    private int minRPS;
    private long minRPSTimestamp;

    private int previousRequestCount;
    private long minLatency;
    private long maxLatency;

    public BackendServer(String host, int port) {
        this.host = host;
        this.port = port;
        this.isHealthy = true; // Assume healthy by default for now
        this.lastCheckTime = System.currentTimeMillis();
        this.successfulChecks = 0;
        this.failedChecks = 0;
        this.consecutiveFailures = 0;
        this.failureTimestamps = new ArrayList<>();
        this.failureTimestamps = new ArrayList<>();
        this.requestCount = new java.util.concurrent.atomic.AtomicInteger(0);
        this.activeRequests = new java.util.concurrent.atomic.AtomicInteger(0);

        this.maxRPS = 0;
        this.maxRPSTimestamp = 0;
        this.minRPS = -1;
        this.minRPSTimestamp = 0;

        this.previousRequestCount = 0;
        this.minLatency = -1;
        this.maxLatency = 0;
    }

    public String getHost() {
        return host;
    }

    public int getPort() {
        return port;
    }

    public boolean isHealthy() {
        return isHealthy;
    }

    public void setHealthy(boolean healthy) {
        this.isHealthy = healthy;
    }

    public long getLastCheckTime() {
        return lastCheckTime;
    }

    public void setLastCheckTime(long lastCheckTime) {
        this.lastCheckTime = lastCheckTime;
    }

    public int getSuccessfulChecks() {
        return successfulChecks;
    }

    public void incrementSuccessfulChecks() {
        this.successfulChecks++;
    }

    public int getFailedChecks() {
        return failedChecks;
    }

    public void incrementFailedChecks() {
        this.failedChecks++;
    }

    public int getConsecutiveFailures() {
        return consecutiveFailures;
    }

    public void setConsecutiveFailures(int consecutiveFailures) {
        this.consecutiveFailures = consecutiveFailures;
    }

    public void incrementConsecutiveFailures() {
        this.consecutiveFailures++;
    }

    public void resetConsecutiveFailures() {
        this.consecutiveFailures = 0;
    }

    public void addFailureTimestamp(long timestamp) {
        failureTimestamps.add(timestamp);
        // Keep only last 50 failures to avoid memory growth
        if (failureTimestamps.size() > 50) {
            failureTimestamps.remove(0);
        }
    }

    public List<Long> getFailureTimestamps() {
        return new ArrayList<>(failureTimestamps);
    }

    public void incrementRequestCount() {
        requestCount.incrementAndGet();
    }

    public int getRequestCount() {
        return requestCount.get();
    }

    public void incrementActiveRequests() {
        activeRequests.incrementAndGet();
    }

    public void decrementActiveRequests() {
        activeRequests.decrementAndGet();
    }

    public int getActiveRequests() {
        return activeRequests.get();
    }

    public synchronized void recordLatency(long latency) {
        if (minLatency == -1 || latency < minLatency) {
            minLatency = latency;
        }
        if (latency > maxLatency) {
            maxLatency = latency;
        }
    }

    public synchronized void updateRPS(int currentRPS, long timestamp) {
        if (currentRPS > maxRPS) {
            maxRPS = currentRPS;
            maxRPSTimestamp = timestamp;
        }
        if (minRPS == -1 || currentRPS < minRPS) {
            minRPS = currentRPS;
            minRPSTimestamp = timestamp;
        }
    }

    public int getPreviousRequestCount() {
        return previousRequestCount;
    }

    public void setPreviousRequestCount(int previousRequestCount) {
        this.previousRequestCount = previousRequestCount;
    }

    // Helper to format time
    private String formatTime(long ts) {
        if (ts == 0)
            return "N/A";
        java.text.SimpleDateFormat sdf = new java.text.SimpleDateFormat("HH:mm:ss");
        return sdf.format(new java.util.Date(ts));
    }

    @Override
    public String toString() {
        String lastFail = failureTimestamps.isEmpty() ? "None"
                : String.valueOf(failureTimestamps.get(failureTimestamps.size() - 1));

        String latStr = (minLatency == -1) ? "N/A" : (minLatency + "-" + maxLatency + "ms");

        String rpsStr;
        if (minRPS == -1) {
            rpsStr = "N/A";
        } else {
            rpsStr = minRPS + " (at " + formatTime(minRPSTimestamp) + ") - " +
                    maxRPS + " (at " + formatTime(maxRPSTimestamp) + ")";
        }

        return host + ":" + port + " [Health: " + (isHealthy ? "UP" : "DOWN") +
                ", Active: " + activeRequests.get() +
                ", Req: " + requestCount.get() +
                ", RPS Range: " + rpsStr +
                ", Latency Range: " + latStr +
                ", Fails: " + consecutiveFailures +
                ", LastFail: " + lastFail + "]";
    }
}
