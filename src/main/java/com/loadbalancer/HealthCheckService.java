package com.loadbalancer;

import java.io.IOException;
import java.net.Socket;
import java.util.List;
import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

public class HealthCheckService {
    private final List<BackendServer> backendServers;
    private final ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);

    public HealthCheckService(List<BackendServer> backendServers) {
        this.backendServers = backendServers;
    }

    public void start() {
        System.out.println("🩺 Health Check Service started...");
        scheduler.scheduleAtFixedRate(this::checkHealth, 0, 5, TimeUnit.SECONDS);
    }

    public void stop() {
        scheduler.shutdown();
    }

    private long lastScaleTime = 0;
    private int nextPort = 9084;
    private static final int SCALE_COOLDOWN_MS = 20000;
    private static final int RPS_THRESHOLD = 10;

    private void checkHealth() {
        BackendServer maxReqServer = null;
        BackendServer minReqServer = null;
        int maxReq = -1;
        int minReq = Integer.MAX_VALUE;

        long totalCurrentRPS = 0;
        int healthyServerCount = 0;

        for (BackendServer server : backendServers) {
            boolean isAlive = ping(server.getHost(), server.getPort());

            server.setLastCheckTime(System.currentTimeMillis());

            if (isAlive) {
                server.incrementSuccessfulChecks();
                server.resetConsecutiveFailures();
                if (server.isHealthy())
                    healthyServerCount++;
            } else {
                server.incrementFailedChecks();
                server.incrementConsecutiveFailures();
                server.addFailureTimestamp(System.currentTimeMillis());
            }

            if (server.isHealthy() != isAlive) {
                System.out
                        .println("⚠️  Server " + server + " status changed to: " + (isAlive ? "HEALTHY" : "UNHEALTHY"));
                server.setHealthy(isAlive);
            }

            // Track Max/Min
            int count = server.getRequestCount();
            int prevCount = server.getPreviousRequestCount();
            int currentRPS = (int) ((count - prevCount) / 5.0); // 5 sec interval
            if (currentRPS < 0)
                currentRPS = 0; // Just in case

            totalCurrentRPS += currentRPS;

            server.updateRPS(currentRPS, System.currentTimeMillis());
            server.setPreviousRequestCount(count);

            if (count > maxReq) {
                maxReq = count;
                maxReqServer = server;
            }
            if (count < minReq) {
                minReq = count;
                minReqServer = server;
            }
        }

        // Auto-Scaling Logic
        double avgRPS = (healthyServerCount > 0) ? (double) totalCurrentRPS / healthyServerCount : 0;

        if (avgRPS > RPS_THRESHOLD && (System.currentTimeMillis() - lastScaleTime) > SCALE_COOLDOWN_MS) {
            scaleUp(avgRPS);
        }

        if (maxReqServer != null && minReqServer != null) {
            StringBuilder distribution = new StringBuilder();
            distribution.append("[");
            for (int i = 0; i < backendServers.size(); i++) {
                BackendServer s = backendServers.get(i);
                distribution.append(s.toString()); // Uses updated toString with RPS/Latency
                if (i < backendServers.size() - 1) {
                    distribution.append(", ");
                }
            }
            distribution.append("]");

            System.out.println("📊 Stats - Max Requests: Port " + maxReqServer.getPort() + " (" + maxReq + ")" +
                    " | Min Requests: Port " + minReqServer.getPort() + " (" + minReq + ")" +
                    " | Avg RPS: " + String.format("%.2f", avgRPS) +
                    " | Details: " + distribution.toString());
        }
    }

    private void scaleUp(double avgRPS) {
        System.out.println("🚀 High Load Detected (Avg RPS: " + String.format("%.2f", avgRPS) + "). Scaling up!");
        try {
            // Spawn new backend process
            new ProcessBuilder("python3", "mock_server.py", String.valueOf(nextPort))
                    .redirectErrorStream(true)
                    .inheritIO() // Let it print to console if needed, or we might want to silence it
                    .start();

            // Register it
            BackendServer newServer = new BackendServer("localhost", nextPort);
            // Give it a moment to start? No, health check will pick it up next cycle
            backendServers.add(newServer);

            System.out.println("✅ Spawned new backend server on port " + nextPort);

            lastScaleTime = System.currentTimeMillis();
            nextPort++;

        } catch (IOException e) {
            System.err.println("❌ Failed to scale up: " + e.getMessage());
        }
    }

    private boolean ping(String host, int port) {
        try (Socket socket = new Socket(host, port)) {
            return true;
        } catch (IOException e) {
            return false;
        }
    }
}
