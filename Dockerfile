# Use a slim Python base image
FROM python:3.9-slim

# Install OpenJDK 17 (Required for Java Load Balancer)
# We also install 'procps' (for 'ps' command if needed) and 'curl'
RUN apt-get update && \
    apt-get install -y openjdk-17-jdk procps curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all project files
COPY . .

# Ensure scripts are executable
RUN chmod +x *.sh

# Compile the Java Load Balancer
RUN javac -d bin src/main/java/com/loadbalancer/*.java

# Run the web server (which manages the LB)
CMD ["python3", "web_server.py"]
