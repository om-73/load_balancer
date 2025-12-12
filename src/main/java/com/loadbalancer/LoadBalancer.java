package com.loadbalancer;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;
import java.util.List;

public class LoadBalancer {
    private static final int PORT = 8080;

    public static void main(String[] args) {
        List<BackendServer> backendServers = new ArrayList<>();
        // Hardcoded backends for demonstration
        backendServers.add(new BackendServer("localhost", 8081));
        backendServers.add(new BackendServer("localhost", 8082));
        backendServers.add(new BackendServer("localhost", 8083));

        LoadBalancingStrategy strategy = new RoundRobinStrategy();

        System.out.println("Load Balancer started on port " + PORT);

        // Optimizing with a Thread Pool
        java.util.concurrent.ExecutorService threadPool = java.util.concurrent.Executors.newCachedThreadPool();

        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            while (true) {
                Socket clientSocket = serverSocket.accept();
                System.out.println("Accepted connection from " + clientSocket.getRemoteSocketAddress());
                // Submit main handler to pool (it will use the same pool for its sub-tasks)
                // Note: We use the same pool for everything. Be careful of exhaustion if we
                // used FixedThreadPool.
                // CachedThreadPool grows as needed so it's safer against deadlocks here.
                ClientHandler p = new ClientHandler(clientSocket, strategy, backendServers, threadPool);
                threadPool.submit(p);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
