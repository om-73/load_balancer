# Use a stable Debian 12 (Bookworm) base with Python 3.11
# This ensures standard package repos are available for OpenJDK
FROM python:3.11-slim-bookworm

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

# Run the startup script
CMD ["./start_render.sh"]
