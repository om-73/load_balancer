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

        try (ServerSocket serverSocket = new ServerSocket(PORT)) {
            while (true) {
                Socket clientSocket = serverSocket.accept();
                System.out.println("Accepted connection from " + clientSocket.getRemoteSocketAddress());
                ClientHandler p = new ClientHandler(clientSocket, strategy, backendServers);
                new Thread(p).start();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
