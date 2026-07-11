# -*- coding: utf-8 -*-

import os
import glob
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

HASH_DIR = "./handshakes/"
GEOWIFI_PATH = "/home/pi/geowifi/geowifi.py"
RESULTS_DIR = "/home/pi/results/"

MAC_REGEX = re.compile(r'\b(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\b')

os.makedirs(RESULTS_DIR, exist_ok=True)

def ssid_from_pcap(filename):
    base = os.path.basename(filename)
    if "_" not in base:
        return base.replace(".pcap", "")
    return base.rsplit("_", 1)[0]

def safe_filename(name):
    return re.sub(r'[^A-Za-z0-9_\-\.]+', '_', name)

def run_geowifi_map(bssid, ssid):
    print("    [+] Running GeoWiFi for " + bssid + " (" + ssid + ")")

    cmd = [
        "sudo", "python3", GEOWIFI_PATH,
        "-s", "bssid",
        "-o", "map",
        bssid
    ]

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    match = re.search(r"(?:Map.*saved.*?:\s*)(.*\.html)", proc.stdout)

    if not match:
        print("    [!] GeoWiFi saved a map but message format did not match regex.")
        print("    [!] Falling back to newest HTML file in /home/pi/geowifi/results/")

        geowifi_results = "/home/pi/geowifi/results/"
        try:
            html_files = sorted(
                [os.path.join(geowifi_results, f) for f in os.listdir(geowifi_results) if f.endswith(".html")],
                key=os.path.getmtime
            )
        except FileNotFoundError:
            print("    [-] GeoWiFi results folder not found.")
            return None

        if not html_files:
            print("    [-] No HTML files found in GeoWiFi results folder.")
            return None

        real_path = html_files[-1]
    else:
        real_path = match.group(1).strip().replace("\\", "/")

    ssid_file = safe_filename(ssid) + ".html"
    output_file = os.path.join(RESULTS_DIR, ssid_file)

    subprocess.run(["sudo", "cp", real_path, output_file])

    print("    [+] Saved map -> " + output_file)
    return output_file


print("[*] Scanning PCAPs inside " + HASH_DIR)

pcap_files = glob.glob(os.path.join(HASH_DIR, "*.pcap"))
if not pcap_files:
    print("[!] No PCAP files found.")
    exit()

generated_maps = []

for pcap in pcap_files:
    filename = os.path.basename(pcap)
    ssid = ssid_from_pcap(filename)

    print("\n[+] Processing " + filename + " (SSID: " + ssid + ")")

    proc = subprocess.run(
        ["sudo", "tcpdump", "-nn", "-e", "-r", pcap],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    found_macs = MAC_REGEX.findall(proc.stdout)

    bssids = {
        mac.lower()
        for mac in found_macs
        if not mac.lower().startswith(("ff:", "33:", "da:"))
    }

    if not bssids:
        print("    [-] No valid BSSIDs found.")
        continue

    print("    [!] Found " + str(len(bssids)) + " BSSIDs: " + str(list(bssids)))

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(run_geowifi_map, bssid, ssid): bssid for bssid in bssids}

        for future in as_completed(futures):
            bssid = futures[future]
            html_file = future.result()
            if html_file:
                generated_maps.append(html_file)

print("\n[+] All maps saved:")
for m in generated_maps:
    print("    " + m)

print("\n[+] You can now combine these HTML files into one master map.")

