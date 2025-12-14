package com.loadbalancer;

import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.*;

public class PortScanner {

    private static final int TIMEOUT_MS = 200;
    private static final int THREAD_POOL_SIZE = 20;

    public static void main(String[] args) {
        if (args.length < 1) {
            System.out.println("Usage:");
            System.out.println("  java com.loadbalancer.PortScanner <host>                (Scans common ports)");
            System.out.println("  java com.loadbalancer.PortScanner <host> <start> <end>  (Scans range)");
            return;
        }

        String host = extractHost(args[0]);
        PortScanner scanner = new PortScanner();

        System.out.println("Starting scan for " + host + "...");
        long startTime = System.currentTimeMillis();

        if (args.length == 3) {
            try {
                int startPort = Integer.parseInt(args[1]);
                int endPort = Integer.parseInt(args[2]);
                scanner.scanPorts(host, startPort, endPort);
            } catch (NumberFormatException e) {
                System.err.println("Invalid port numbers provided.");
            }
        } else {
            scanner.scanCommonPorts(host);
        }

        long duration = System.currentTimeMillis() - startTime;
        System.out.println("Scan completed in " + duration + "ms.");
    }

    public void scanCommonPorts(String host) {
        int[] commonPorts = { 21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 3389, 5432, 6379, 8080,
                8443 };
        System.out.println("Scanning " + commonPorts.length + " common ports...");

        ExecutorService executor = Executors.newFixedThreadPool(THREAD_POOL_SIZE);
        List<Future<Void>> futures = new ArrayList<>();

        for (int port : commonPorts) {
            futures.add(executor.submit(() -> {
                if (isPortOpen(host, port)) {
                    System.out.println("✅ Port " + port + " is OPEN");
                }
                return null;
            }));
        }

        shutdownExecutor(executor, futures);
    }

    public void scanPorts(String host, int startPort, int endPort) {
        if (startPort > endPort) {
            System.err.println("Start port must be less than or equal to end port.");
            return;
        }

        int totalPorts = endPort - startPort + 1;
        System.out.println("Scanning " + totalPorts + " ports (" + startPort + "-" + endPort + ")...");

        ExecutorService executor = Executors.newFixedThreadPool(THREAD_POOL_SIZE);
        List<Future<Void>> futures = new ArrayList<>();

        for (int port = startPort; port <= endPort; port++) {
            int currentPort = port;
            futures.add(executor.submit(() -> {
                if (isPortOpen(host, currentPort)) {
                    System.out.println("✅ Port " + currentPort + " is OPEN");
                }
                return null;
            }));
        }

        shutdownExecutor(executor, futures);
    }

    private boolean isPortOpen(String host, int port) {
        try (Socket socket = new Socket()) {
            socket.connect(new InetSocketAddress(host, port), TIMEOUT_MS);
            return true;
        } catch (IOException e) {
            return false;
        }
    }

    private void shutdownExecutor(ExecutorService executor, List<Future<Void>> futures) {
        executor.shutdown();
        try {
            // Wait for all tasks to complete
            for (Future<Void> f : futures) {
                try {
                    f.get();
                } catch (ExecutionException e) {
                    // Ignore individual task errors
                }
            }
            executor.awaitTermination(1, TimeUnit.MINUTES);
        } catch (InterruptedException e) {
            System.err.println("Scan interrupted.");
        }
    }

    private static String extractHost(String input) {
        if (!input.contains("://")) {
            return input; // Assume it's already a hostname
        }
        try {
            URI uri = new URI(input);
            String host = uri.getHost();
            return (host != null) ? host : input;
        } catch (URISyntaxException e) {
            System.err.println("Invalid URL format: " + input + ". Using original input.");
            return input;
        }
    }
}
