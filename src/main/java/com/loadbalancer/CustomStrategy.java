package com.loadbalancer;
import java.util.List;
import java.util.Random;

public class CustomStrategy implements LoadBalancingStrategy {
    private Random random = new Random();

    @Override
    public BackendServer getNextServer(List<BackendServer> servers) {
        if (servers.isEmpty()) return null;
        return servers.get(random.nextInt(servers.size()));
    }
}