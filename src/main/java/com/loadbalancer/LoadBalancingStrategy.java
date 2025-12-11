package com.loadbalancer;

import java.util.List;

public interface LoadBalancingStrategy {
    BackendServer getNextServer(List<BackendServer> servers);
}
