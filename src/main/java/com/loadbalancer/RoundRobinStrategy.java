package com.loadbalancer;

import java.util.List;
import java.util.concurrent.atomic.AtomicInteger;

public class RoundRobinStrategy implements LoadBalancingStrategy {
    private AtomicInteger counter = new AtomicInteger(0);

    @Override
    public BackendServer getNextServer(List<BackendServer> servers) {
        if (servers == null || servers.isEmpty()) {
            return null;
        }

        // Try to find a healthy server (limit attempts to size of list to avoid
        // infinite loop)
        for (int i = 0; i < servers.size(); i++) {
            int index = getNextIndex(servers.size());
            BackendServer server = servers.get(index);
            if (server.isHealthy()) {
                return server;
            }
        }

        System.err.println("❌ No healthy backend servers available!");
        return null; // No healthy servers found
    }

    private int getNextIndex(int size) {
        int index = counter.getAndIncrement() % size;
        if (index < 0) {
            index = Math.abs(index);
        }
        return index;
    }
}
