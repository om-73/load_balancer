package com.loadbalancer;
import java.util.List;

public class CustomStrategy implements LoadBalancingStrategy {
    private int counter = 0;
    @Override
    public BackendServer getNextServer(List<BackendServer> servers, String clientIp) {
        if (servers.isEmpty()) return null;
        counter++;
        if (counter % 2 == 0) return servers.get(0);
        return servers.get(counter % servers.size());
    }
}