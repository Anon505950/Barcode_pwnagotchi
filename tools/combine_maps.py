import os
import re

MAP_DIR = "../geowifi/results"
OUTPUT_FILE = "full_geolocations.html"

HTML_HEADER = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8" />
<title>Combined WiFi Map</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

<style>
  body { margin: 0; padding: 0; font-family: Arial, sans-serif; }
  #header {
      background: #222;
      color: #fff;
      padding: 10px;
      display: flex;
      align-items: center;
      gap: 20px;
  }
  #searchBox {
      padding: 6px 10px;
      font-size: 16px;
      width: 300px;
  }
  #map { height: calc(100vh - 50px); width: 100%; }
</style>
</head>

<body>
<div id="header">
    <span style="font-size:18px; font-weight:bold;">Combined WiFi Map</span>
    <input id="searchBox" type="text" placeholder="Search SSID or BSSID...">
    <span id="markerCount">Total markers: 0</span>
</div>

<div id="map"></div>

<script>
var map = L.map('map').setView([40.44, -79.99], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19
}).addTo(map);

var allMarkers = [];
"""

HTML_FOOTER = """
// Update marker count
document.getElementById("markerCount").innerText = "Total markers: " + allMarkers.length;

// Search filtering
document.getElementById("searchBox").addEventListener("input", function() {
    var q = this.value.toLowerCase();

    allMarkers.forEach(function(m) {
        var match = m.ssid.toLowerCase().includes(q) ||
                    m.bssid.toLowerCase().includes(q);

        if (match || q === "") {
            if (!map.hasLayer(m)) map.addLayer(m);
        } else {
            if (map.hasLayer(m)) map.removeLayer(m);
        }
    });
});
</script>
</body>
</html>
"""



def sanitize_ssid(ssid):
    if "_" in ssid:
        return ssid.rsplit("_", 1)[0]
    return ssid


def extract_ssid(html_text):
    match = re.search(r"<h3>(.*?)</h1>", html_text)
    if match:
        return match.group(1)
    return "Unknown"

def extract_bssid(html_text):
    match = re.search(r"<b>BSSID</b>:\s*([0-9a-fA-F:]{17})", html_text)
    if match:
        return match.group(1)
    return "00:00:00:00:00:00"

def extract_markers(html_text):
    # Matches: L.marker( [lat, lon], {} )
    marker_regex = r"L\.marker\(\s*\[\s*([0-9\.\-]+)\s*,\s*([0-9\.\-]+)\s*\]"
    return re.findall(marker_regex, html_text)

def ssid_from_filename(filename):
    # If your PCAPs are named like SSID_bssid.pcap and you mirror that,
    # you can adapt this. For now, just use the BSSID-ish part.
    base = filename.replace(".html", "")
    return base

def main():
    markers = []

    print(f"[*] Reading maps from {MAP_DIR}")

    for filename in os.listdir(MAP_DIR):
        if not filename.endswith(".html"):
            continue

        path = os.path.join(MAP_DIR, filename)
        #ssid = ssid_from_filename(filename)

        print(f"[+] Processing {filename}")

        with open(path, "r") as f:
            html = f.read()
        ssid_raw = extract_ssid(html)
        ssid = sanitize_ssid(ssid_raw)
        bssid = extract_bssid(html)
        coords = extract_markers(html)

        for lat, lon in coords:
            markers.append((lat, lon, ssid, bssid))

    print(f"[+] Found {len(markers)} total markers")

    combined = HTML_HEADER

    for lat, lon, ssid, bssid in markers:
        popup = f"SSID: {ssid}<br>BSSID: {bssid}<br>{lat}, {lon}"
        combined += f"""
        var m = L.marker([{lat}, {lon}]).addTo(map).bindPopup("SSID: {ssid}<br>BSSID: {bssid}<br>{lat}, {lon}");
        m.ssid = "{ssid}";
        m.bssid = "{bssid}";
        allMarkers.push(m);
        """


    combined += HTML_FOOTER

    with open(OUTPUT_FILE, "w") as f:
        f.write(combined)

    print(f"\n[+] Combined map saved as {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

