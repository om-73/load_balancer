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
        int index = counter.getAndIncrement() % servers.size();
        if (index < 0) {
            index = Math.abs(index);
        }
        return servers.get(index);
    }
}
