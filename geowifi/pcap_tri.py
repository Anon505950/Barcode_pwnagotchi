# -*- coding: utf-8 -*-

import os
import glob
import subprocess
import re
import time

HASH_DIR = "/root/handshakes/"
GEOWIFI_PATH = "/home/pi/geowifi/geowifi.py"
RESULTS_DIR = "/home/pi/geowifi/results/"
MAX_TRIES = 5
MAC_REGEX = re.compile(r'\b(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\b')

os.makedirs(RESULTS_DIR, exist_ok=True)


def replace_popup_with_ssid(path, ssid):
    """Rewrite popup text inside GeoWiFi HTML file."""
    try:
        with open(path, "r") as f:
            html = f.read()

        html = html.replace("Network Information", ssid)
        html = re.sub(r"Module:.*?<br>", "", html)
        html = re.sub(r"Vendor:.*?<br>", "", html)

        with open(path, "w") as f:
            f.write(html)

        print(" [+] Rewrote popup to SSID:", ssid)
    except Exception as e:
        print(" [-] Failed to rewrite popup:", e)


def html_has_marker(path):
    """Check if GeoWiFi map contains at least one marker."""
    try:
        with open(path, "r") as f:
            return "L.marker" in f.read()
    except:
        return False


def ssidmac_from_pcap(filename):
    return os.path.basename(filename).replace(".pcap", "")


def newest_geowifi_file():
    """Return newest HTML file in results directory."""
    html_files = [
        os.path.join(RESULTS_DIR, f)
        for f in os.listdir(RESULTS_DIR)
        if f.endswith(".html")
    ]
    if not html_files:
        return None
    return max(html_files, key=os.path.getmtime)


def run_geowifi_map(bssid):
    """Run GeoWiFi and return the newest file."""
    print("    [+] Running GeoWiFi for " + bssid)

    cmd = [
        "sudo", "python3", GEOWIFI_PATH,
        "-s", "bssid",
        "-o", "map",
        bssid
    ]

    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    time.sleep(0.5)  # allow GeoWiFi time to finish writing
    return newest_geowifi_file()


print("[*] Scanning PCAPs inside " + HASH_DIR)

pcap_files = glob.glob(os.path.join(HASH_DIR, "*.pcap"))
if not pcap_files:
    print("[!] No PCAP files found.")
    exit()

generated_maps = []

for pcap in pcap_files:
    filename = os.path.basename(pcap)
    ssidmac = ssidmac_from_pcap(filename)
    print("\n[+] Processing " + filename + " (SSID_MAC: " + ssidmac + ")")

    # Extract BSSIDs first (needed for skip logic)
    proc = subprocess.run(
        ["sudo", "tcpdump", "-nn", "-e", "-r", pcap],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    found_macs = MAC_REGEX.findall(proc.stdout)

    bssids = [
        mac.lower()
        for mac in found_macs
        if not mac.lower().startswith(("ff:", "33:", "da:", "00:"))
    ]

    unique_ouis = {}
    for mac in bssids:
        oui = mac[:8]
        if oui not in unique_ouis:
            unique_ouis[oui] = mac

    bssids = list(unique_ouis.values())[:MAX_TRIES]

    print(" [!] BSSIDs to try:", bssids)

    if not bssids:
        print("    [-] No valid BSSIDs found.")
        continue

    # Skip entire PCAP if ANY BSSID already has a map
    existing_maps = [
        f for f in os.listdir(RESULTS_DIR)
        if any(bssid.replace(":", "_") in f for bssid in bssids)
    ]

    if existing_maps:
        print(f"    [!] A map already exists for SSID_MAC {ssidmac}, skipping entire PCAP.")
        continue

    map_saved = False

    for bssid in bssids:
        geowifi_filename = bssid.replace(":", "_") + ".html"
        geowifi_path = os.path.join(RESULTS_DIR, geowifi_filename)

        # If GeoWiFi already made this file, treat it as valid
        if os.path.exists(geowifi_path):
            print("    [!] Map already exists for " + geowifi_filename + ", using existing file.")

            if html_has_marker(geowifi_path):
                print(" [+] Existing map has valid markers!")
                replace_popup_with_ssid(geowifi_path, ssidmac)
                generated_maps.append(geowifi_path)
                map_saved = True
                break
            else:
                print(" [-] Existing map has no markers, continuing.")
            continue

        # Run GeoWiFi
        html_file = run_geowifi_map(bssid)

        if not html_file:
            print(" [-] GeoWiFi produced no file.")
            continue

        print("    [+] GeoWiFi saved:", html_file)

        if html_has_marker(html_file):
            print(" [+] Valid map found with markers!")
            replace_popup_with_ssid(html_file, ssidmac)
            generated_maps.append(html_file)
            map_saved = True
            break
        else:
            print(" [-] No markers found, deleting:", html_file)
            try:
                os.remove(html_file)
            except:
                print(" [-] Failed to delete", html_file)

    if not map_saved:
        print("    [-] No valid map produced for SSID_MAC:", ssidmac)

print("\n[+] All maps saved:")
for m in generated_maps:
    print("    " + m)

print("\n[+] You can now combine these HTML files into one master map.")

if generated_maps:
    subprocess.run(["sudo", "python3", "/home/pi/tools/combine_maps.py"])


