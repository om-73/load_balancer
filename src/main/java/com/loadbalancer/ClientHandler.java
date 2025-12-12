package com.loadbalancer;

import java.io.*;
import java.net.Socket;
import java.util.List;

public class ClientHandler implements Runnable {
    private Socket clientSocket;
    private LoadBalancingStrategy strategy;
    private List<BackendServer> backendServers;
    private java.util.concurrent.ExecutorService threadPool;

    public ClientHandler(Socket clientSocket, LoadBalancingStrategy strategy, List<BackendServer> backendServers,
            java.util.concurrent.ExecutorService threadPool) {
        this.clientSocket = clientSocket;
        this.strategy = strategy;
        this.backendServers = backendServers;
        this.threadPool = threadPool;
    }

    @Override
    public void run() {
        BackendServer targetServer = strategy.getNextServer(backendServers);
        if (targetServer == null) {
            System.err.println("No backend servers available.");
            closeClientSocket();
            return;
        }

        System.out.println("Forwarding request to " + targetServer);

        try (Socket backendSocket = new Socket(targetServer.getHost(), targetServer.getPort())) {
            // Forwarding via Thread Pool
            java.util.concurrent.Future<?> f1 = threadPool.submit(
                    new DataTransfer(clientSocket.getInputStream(), backendSocket.getOutputStream()));
            java.util.concurrent.Future<?> f2 = threadPool.submit(
                    new DataTransfer(backendSocket.getInputStream(), clientSocket.getOutputStream()));

            try {
                // Wait for both to complete (or one to fail/close)
                f1.get();
                f2.get();
            } catch (java.util.concurrent.ExecutionException | java.util.concurrent.CancellationException e) {
                // Ignore
            }

        } catch (IOException | InterruptedException e) {
            System.out.println("Error forwarding to backend: " + e.getMessage());
            e.printStackTrace();
        } finally {
            closeClientSocket();
        }
    }

    private void closeClientSocket() {
        try {
            if (clientSocket != null && !clientSocket.isClosed()) {
                clientSocket.close();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    // Helper class for data transfer
    private static class DataTransfer implements Runnable {
        private InputStream input;
        private OutputStream output;

        public DataTransfer(InputStream input, OutputStream output) {
            this.input = input;
            this.output = output;
        }

        @Override
        public void run() {
            byte[] buffer = new byte[4096];
            int bytesRead;
            try {
                while ((bytesRead = input.read(buffer)) != -1) {
                    output.write(buffer, 0, bytesRead);
                    output.flush();
                }
            } catch (IOException e) {
                // Connection closed or error
            }
        }
    }
}
