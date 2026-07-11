#!/bin/bash

DNS="127.0.0.1"

echo "Setting DNS to $DNS..."

# Remove immutable flag if already set
sudo chattr -i /etc/resolv.conf 2>/dev/null

# Write new nameserver
echo "nameserver $DNS" | sudo tee /etc/resolv.conf > /dev/null

# Lock the file so nothing overwrites it
sudo chattr +i /etc/resolv.conf

echo "DNS updated and locked."
