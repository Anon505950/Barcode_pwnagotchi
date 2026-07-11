# -*- coding: utf-8 -*-

import os
import glob
import subprocess
import re

HASH_DIR = "/root/handshakes/"
GEOWIFI_PATH = "/home/pi/geowifi/geowifi.py"
RESULTS_DIR = "./results/"
MAX_TRIES = 5
MAC_REGEX = re.compile(r'\b(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}\b')

os.makedirs(RESULTS_DIR, exist_ok=True)

def replace_popup_with_ssid(path, ssid):
    try:
        with open(path, "r") as f:
            html = f.read()

        # Replace the popup title
        html = html.replace("Network Information", ssid)

        # Optional: remove module/vendor lines entirely
        html = re.sub(r"Module:.*?<br>", "", html)
        html = re.sub(r"Vendor:.*?<br>", "", html)

        with open(path, "w") as f:
            f.write(html)

        print(" [+] Rewrote popup to SSID:", ssid)
    except Exception as e:
        print(" [-] Failed to rewrite popup:", e)



def html_has_marker(path):
    try:
        with open(path, "r") as f:
            return "L.marker" in f.read()
    except:
        return False



# Extract full SSID_MAC from filename
def ssidmac_from_pcap(filename):
    base = os.path.basename(filename)
    return base.replace(".pcap", "")

# Make filename safe
def safe_filename(name):
    return re.sub(r'[^A-Za-z0-9_\-\.]+', '_', name)

def run_geowifi_map(bssid, ssidmac):
    print("    [+] Running GeoWiFi for " + bssid + " (" + ssidmac + ")")

    cmd = [
        "sudo", "python3", GEOWIFI_PATH,
        "-s", "bssid",
        "-o", "map",
        bssid
    ]

    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    
    # Universal regex for all GeoWiFi versions
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

    # Output filename: SSID_MAC.html
    ssidmac_file = safe_filename(ssidmac) + ".html"
    #output_file = os.path.join(RESULTS_DIR, ssidmac_file)

    #subprocess.run(["sudo", "cp", real_path, output_file])

    print("    [+] Saved map -> " + ssidmac_file)
    return ssidmac_file

    replace_popup_with_ssid(real_path, ssidmac)


print("[*] Scanning PCAPs inside " + HASH_DIR)

pcap_files = glob.glob(os.path.join(HASH_DIR, "*.pcap"))
if not pcap_files:
    print("[!] No PCAP files found.")
    exit()

generated_maps = []

for pcap in pcap_files:
    filename = os.path.basename(pcap)
    ssidmac = ssidmac_from_pcap(filename)
    ssidmac_file = os.path.join(RESULTS_DIR, safe_filename(ssidmac) + ".html")

    print("\n[+] Processing " + filename + " (SSID_MAC: " + ssidmac + ")")

    # SMART CHECK: skip if SSID_MAC already has a map
    if os.path.exists(ssidmac_file):
        print("    [!] Map already exists for " + ssidmac + ", skipping.")
        continue

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
        if not mac.lower().startswith(("ff:", "33:", "da:"))
    ]

    # Reduce BSSIDs to unique OUIs
    unique_ouis = {}
    for mac in bssids:
        oui = mac[:8]
        if oui not in unique_ouis:
            unique_ouis[oui] = mac

    bssids = list(unique_ouis.values())
    print(" [!] Reduced to unique OUIs:", bssids)

    # Universal stopping point
    bssids = bssids[:MAX_TRIES]
    print(" [!] Limiting to first", MAX_TRIES, "BSSIDs:", bssids)

    if not bssids:
        print("    [-] No valid BSSIDs found.")
        continue

    print("    [!] Found " + str(len(bssids)) + " BSSIDs")

    # SMART SCAN: stop after first valid map
    map_saved = False

    for bssid in bssids:
        html_file = run_geowifi_map(bssid, ssidmac)

        if html_file and html_has_marker(html_file):
            print(" [+] Valid map found with markers, stopping further scans.")
            generated_maps.append(ssidmac_file)
            map_saved = True
            break
        else:
            print(" [-] No markers found for " + bssid + ", trying next BSSID...")
            try:
                os.remove(ssidmac_file)
            except:
                print(" [-] Failed to delete", ssidmac_file)

        if not map_saved:
            print("    [-] No valid map produced for SSID_MAC: " + ssidmac)

print("\n[+] All maps saved:")
for m in generated_maps:
    print("    " + m)

print("\n[+] You can now combine these HTML files into one master map.")


if generated_maps:
    subprocess.run(["sudo", "python3", "combine_maps.py"])

