package com.loadbalancer;

import java.io.*;
import java.net.Socket;
import java.util.List;

public class ClientHandler implements Runnable {
    private Socket clientSocket;
    private LoadBalancingStrategy strategy;
    private List<BackendServer> backendServers;

    public ClientHandler(Socket clientSocket, LoadBalancingStrategy strategy, List<BackendServer> backendServers) {
        this.clientSocket = clientSocket;
        this.strategy = strategy;
        this.backendServers = backendServers;
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
            // Forwarding threads
            Thread clientToBackend = new Thread(
                    new DataTransfer(clientSocket.getInputStream(), backendSocket.getOutputStream()));
            Thread backendToClient = new Thread(
                    new DataTransfer(backendSocket.getInputStream(), clientSocket.getOutputStream()));

            clientToBackend.start();
            backendToClient.start();

            clientToBackend.join();
            backendToClient.join();

        } catch (IOException | InterruptedException e) {
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
