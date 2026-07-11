import re
import json

INPUT_FILE = "full_geolocations.html"
OUTPUT_FILE = "wigle_export.json"

# Regex to match your combined markers
marker_regex = (r"L\.marker\(\[\s*([0-9\.\-]+)\s*,\s*([0-9\.\-]+)\s*\]\)"r".*?bindPopup\('SSID:\s*(.*?)<br>BSSID:\s*([0-9a-fA-F:]{17})<br>")

def main():
    with open(INPUT_FILE, "r") as f:
        html = f.read()

    matches = re.findall(marker_regex, html)

    results = []

    for lat, lon, ssid, bssid in matches:
        results.append({
            "ssid": ssid,
            "bssid": bssid,
            "lat": float(lat),
            "lon": float(lon)
        })

    with open(OUTPUT_FILE, "w") as f:
        json.dump({"results": results}, f, indent=4)

    print(f"[+] Exported {len(results)} entries to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

