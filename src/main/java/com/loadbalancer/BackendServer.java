package com.loadbalancer;

public class BackendServer {
    private String host;
    private int port;
    private boolean isHealthy;

    public BackendServer(String host, int port) {
        this.host = host;
        this.port = port;
        this.isHealthy = true; // Assume healthy by default for now
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
        isHealthy = healthy;
    }

    @Override
    public String toString() {
        return host + ":" + port;
    }
}
