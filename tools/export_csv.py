import re
import csv

INPUT_FILE = "full_geolocations.html"
OUTPUT_FILE = "wigle_export.csv"

# Regex to match your combined markers
marker_regex = (r"L\.marker\(\[\s*([0-9\.\-]+)\s*,\s*([0-9\.\-]+)\s*\]\)"r".*?bindPopup\('SSID:\s*(.*?)<br>BSSID:\s*([0-9a-fA-F:]{17})<br>")

def main():
    with open(INPUT_FILE, "r") as f:
        html = f.read()

    matches = re.findall(marker_regex, html)

    seen = set()  # optional dedupe by BSSID

    with open(OUTPUT_FILE, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["SSID", "BSSID", "Latitude", "Longitude"])

        for lat, lon, ssid, bssid in matches:

            if bssid in seen:
                continue
            seen.add(bssid)

            writer.writerow([ssid, bssid, lat, lon])

    print(f"[+] Exported {len(seen)} entries to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

