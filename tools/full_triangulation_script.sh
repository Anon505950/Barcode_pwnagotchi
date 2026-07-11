#!/bin/bash
sudo python3 /home/pi/geowifi/pcap_tri.py
sudo python3 ./combine_maps.py
./host_map.sh
