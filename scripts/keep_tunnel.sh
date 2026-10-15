#!/usr/bin/env bash
while true; do
  echo "[$(date)] Starting SSH public tunnel to localhost.run with 127.0.0.1:8080..."
  ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ServerAliveInterval=10 -o ServerAliveCountMax=3 -R 80:127.0.0.1:8080 nokey@localhost.run
  echo "[$(date)] Tunnel disconnected. Reconnecting in 3 seconds..."
  sleep 3
done
