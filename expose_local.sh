#!/bin/bash
echo "🚀 Exposing Localhost:8000 to the Public Internet (HTTPS)..."
echo "-------------------------------------------------------------"
echo "NOTE: Copy the 'https://...' URL shown below and paste it into"
echo "the 'Custom Source' field on your Vercel Dashboard."
echo "-------------------------------------------------------------"

# Use localhost.run as it requires no installation, just SSH
# -R 80:localhost:8000 tells the remote server to forward traffic to our local port 8000
ssh -R 80:localhost:8000 nokey@localhost.run
