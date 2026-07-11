#!/bin/bash

echo "Select mode:"
echo "1) Auto Mode"
echo "2) Manual Mode"
read -p "Enter choice (1 or 2): " choice

case "$choice" in
    1)
        echo "Starting AUTO mode..."
        sudo touch /root/.pwnagotchi-auto
        sudo systemctl restart pwnagotchi
        ;;
    2)
        echo "Starting MANUAL mode..."
        sudo touch /root/.pwnagotchi-manu
        sudo systemctl restart pwnagotchi
        ;;
    *)
        echo "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

