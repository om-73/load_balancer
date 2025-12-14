package com.loadbalancer;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;
import java.util.ArrayList;
import java.util.List;

public class LoadBalancer {

    public static void main(String[] args) {
        // Configuration
        // Listening Ports: 8080, 8081, 8082, 8083 matches the user requirement
        // Backend Ports: 9081, 9082, 9083 are the actual servers
        int[] listeningPorts = { 8080, 8081, 8082, 8083 };

        // Thread-safe list for backend servers
        List<BackendServer> backendServers = new java.util.concurrent.CopyOnWriteArrayList<>();

        // Use args if provided, otherwise default to 9081-9083
        if (args.length > 0) {
            for (String arg : args) {
                try {
                    int port = Integer.parseInt(arg);
                    backendServers.add(new BackendServer("localhost", port));
                } catch (NumberFormatException e) {
                    System.err.println("Invalid port: " + arg);
                }
            }
        } else {
            // Default backends
            backendServers.add(new BackendServer("localhost", 9081));
            backendServers.add(new BackendServer("localhost", 9082));
            backendServers.add(new BackendServer("localhost", 9083));
        }

        // Control Port Listener (8888)
        new Thread(() -> {
            try (ServerSocket controlSocket = new ServerSocket(8888)) {
                System.out.println("🔧 Control Port listening on 8888");
                while (true) {
                    try (Socket client = controlSocket.accept();
                            java.io.BufferedReader in = new java.io.BufferedReader(
                                    new java.io.InputStreamReader(client.getInputStream()));
                            java.io.PrintWriter out = new java.io.PrintWriter(client.getOutputStream(), true)) {

                        String input = in.readLine();
                        if (input != null && input.startsWith("ADD")) {
                            // Format: ADD host port
                            String[] parts = input.split(" ");
                            if (parts.length == 3) {
                                String host = parts[1];
                                int port = Integer.parseInt(parts[2]);
                                backendServers.add(new BackendServer(host, port));
                                System.out.println("✅ Added new backend: " + host + ":" + port);
                                out.println("OK");
                            } else {
                                out.println("ERROR: Usage ADD <host> <port>");
                            }
                        }
                    } catch (Exception e) {
                        e.printStackTrace();
                    }
                }
            } catch (IOException e) {
                System.err.println("Control Port Error: " + e.getMessage());
            }
        }).start();

        if (backendServers.isEmpty()) {
            System.err.println("No valid backend servers configured. Exiting.");
            return;
        }

        // LoadBalancingStrategy strategy = new RoundRobinStrategy();
        // Dynamic Strategy Selection
        LoadBalancingStrategy strategy;
        try {
            Class<?> customClass = Class.forName("com.loadbalancer.CustomStrategy");
            strategy = (LoadBalancingStrategy) customClass.getDeclaredConstructor().newInstance();
            System.out.println("✨ Custom Strategy Loaded: " + customClass.getSimpleName());
        } catch (Exception e) {
            System.out.println("Using Default Adaptive Strategy (No Custom Strategy found)");
            strategy = new AdaptiveStrategy();
        }

        // Initialize and start Health Check Service
        HealthCheckService healthCheckService = new HealthCheckService(backendServers);
        healthCheckService.start();

        System.out.println("Load Balancer starting on ports: 8080, 8081, 8082, 8083");
        System.out.println("Backend Servers: " + backendServers);

        // Optimizing with a Thread Pool
        java.util.concurrent.ExecutorService threadPool = java.util.concurrent.Executors.newCachedThreadPool();

        // Final variable for lambda capture
        final LoadBalancingStrategy finalStrategy = strategy;

        // Start a listener for each port
        for (int port : listeningPorts) {
            new Thread(() -> {
                try (ServerSocket serverSocket = new ServerSocket(port)) {
                    System.out.println("Listening on port " + port);
                    while (true) {
                        Socket clientSocket = serverSocket.accept();
                        ClientHandler p = new ClientHandler(clientSocket, finalStrategy, backendServers, threadPool);
                        threadPool.submit(p);
                    }
                } catch (IOException e) {
                    System.err.println("Error on port " + port + ": " + e.getMessage());
                }
            }).start();
        }
    }
}
