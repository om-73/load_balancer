package com.loadbalancer;

import java.util.List;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

public class ConsistentHashStrategy implements LoadBalancingStrategy {

    @Override
    public BackendServer getNextServer(List<BackendServer> servers, String clientIp) {
        if (servers.isEmpty()) {
            return null;
        }

        // Robust Stateless Hashing
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(clientIp.getBytes(StandardCharsets.UTF_8));

            // Convert first 4 bytes to integer
            int hashInt = 0;
            for (int i = 0; i < 4; i++) {
                hashInt = (hashInt << 8) | (hash[i] & 0xFF);
            }

            // Map to server index
            int index = Math.abs(hashInt) % servers.size();
            return servers.get(index);

        } catch (Exception e) {
            // Fallback to simple hash if SHA-256 fails (unlikely)
            return servers.get(Math.abs(clientIp.hashCode()) % servers.size());
        }
    }
}
