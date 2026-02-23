#!/usr/bin/env python3
"""Download Al Nafl attachments from ArcGIS Form 1 and upload to Cloudinary."""
import os
import requests
import cloudinary
import cloudinary.uploader

AGOL_USER = "nagadco0000"
AGOL_PASS = "Nagad$1390"

cloudinary.config(
    cloud_name="dn3bxmi9r",
    api_key="145686874393476",
    api_secret="fAp16cHdFbFVIL35qwczP-3K92c"
)

DOWNLOAD_DIR = r"c:\Users\abdul\media\_arcgis_downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Get token
print("Getting token...", flush=True)
token_resp = requests.post("https://www.arcgis.com/sharing/rest/generateToken", data={
    "username": AGOL_USER, "password": AGOL_PASS,
    "referer": "https://www.arcgis.com", "f": "json"
})
TOKEN = token_resp.json()["token"]

LAYER_URL = "https://services5.arcgis.com/pYlVm2T6SvR7ytZv/arcgis/rest/services/service_36f94509389d4a85a311cc6aa9c7398e/FeatureServer/0"

# Get all Al Nafl OIDs
print("Getting Al Nafl OIDs...", flush=True)
resp = requests.get(f"{LAYER_URL}/query", params={
    "where": "district_en = 'Al Nafl'",
    "returnIdsOnly": "true",
    "f": "json", "token": TOKEN
})
oids = resp.json().get("objectIds", [])
print(f"Total Al Nafl features: {len(oids)}", flush=True)

# Find features with attachments
print("Finding features with attachments...", flush=True)
features_with_atts = []
for i in range(0, len(oids), 100):
    batch = oids[i:i+100]
    att_resp = requests.post(f"{LAYER_URL}/queryAttachments", data={
        "objectIds": ",".join(str(x) for x in batch),
        "f": "json", "token": TOKEN
    })
    for group in att_resp.json().get("attachmentGroups", []):
        infos = group.get("attachmentInfos", [])
        if infos:
            features_with_atts.append((group["parentObjectId"], infos))

print(f"Features with attachments: {len(features_with_atts)}", flush=True)

# Get feature details
all_oids_with_atts = [x[0] for x in features_with_atts]
feat_map = {}
for i in range(0, len(all_oids_with_atts), 50):
    batch = all_oids_with_atts[i:i+50]
    resp2 = requests.get(f"{LAYER_URL}/query", params={
        "objectIds": ",".join(str(x) for x in batch),
        "outFields": "objectid,name_ar,name_en,district_en",
        "f": "json", "token": TOKEN
    })
    for f in resp2.json().get("features", []):
        feat_map[f["attributes"]["objectid"]] = f["attributes"]

# Read counter
counter_file = r'c:\Users\abdul\media\_last_counter.txt'
if os.path.exists(counter_file):
    with open(counter_file) as f:
        file_counter = int(f.read().strip())
else:
    file_counter = 5000
print(f"Starting counter at: {file_counter}", flush=True)

# Download attachments, upload to Cloudinary, generate HTML
all_poi_html = []
total_uploaded = 0
total_failed = 0

for oid, att_infos in features_with_atts:
    attrs = feat_map.get(oid, {})
    poi_name = attrs.get("name_ar", f"POI_{oid}")
    poi_name_en = attrs.get("name_en", "")

    print(f"\n{poi_name} / {poi_name_en} ({len(att_infos)} attachments)", flush=True)

    media_links = []
    photo_count = 0
    video_count = 0

    for att in att_infos:
        att_id = att["id"]
        att_name = att["name"]
        content_type = att.get("contentType", "")

        # Download
        dl_url = f"{LAYER_URL}/{oid}/attachments/{att_id}"
        dl_resp = requests.get(dl_url, params={"token": TOKEN})

        if dl_resp.status_code != 200:
            print(f"  FAIL download: {att_name}", flush=True)
            total_failed += 1
            file_counter += 1
            continue

        # Save locally
        local_path = os.path.join(DOWNLOAD_DIR, f"{oid}_{att_name}")
        with open(local_path, "wb") as f:
            f.write(dl_resp.content)

        # Determine type
        is_video = content_type.startswith("video/")
        resource_type = "video" if is_video else "image"
        name_no_ext = os.path.splitext(att_name)[0]
        public_id = f"alnafl_media/{name_no_ext}_{file_counter}"

        # Upload to Cloudinary
        try:
            result = cloudinary.uploader.upload(
                local_path,
                resource_type=resource_type,
                public_id=public_id,
                overwrite=False
            )
            url = result["secure_url"]
            if is_video:
                video_count += 1
                media_links.append(f'    <a href="{url}" target="_blank" class="video">Video {video_count}</a>')
            else:
                photo_count += 1
                media_links.append(f'    <a href="{url}" target="_blank">Photo {photo_count}</a>')
            total_uploaded += 1
            print(f"  OK [{file_counter}]: {att_name}", flush=True)
        except Exception as e:
            total_failed += 1
            print(f"  FAIL [{file_counter}]: {att_name} -> {e}", flush=True)

        file_counter += 1

        # Clean up local file
        try:
            os.remove(local_path)
        except:
            pass

    total_media = photo_count + video_count
    if total_media > 0:
        media_grid = "\n".join(media_links)
        poi_html = f'''<div class="poi" data-media="1" data-district="alnafl">
  <h3>{poi_name}</h3>
  <div class="meta">life_convenience | open | Media: {total_media}</div>
  <div class="media-grid">
{media_grid}
  </div>
</div>'''
        all_poi_html.append(poi_html)

# Write output
output_html = "\n".join(all_poi_html)
with open(r'c:\Users\abdul\media\_new_alnafl_arcgis_pois.txt', 'w', encoding='utf-8') as f:
    f.write(output_html)

with open(counter_file, 'w') as f:
    f.write(str(file_counter))

print(f"\n{'='*60}")
print(f"DONE: {total_uploaded} uploaded, {total_failed} failed")
print(f"Generated {len(all_poi_html)} POI entries")
print(f"Last counter: {file_counter}")
print(f"Output: _new_alnafl_arcgis_pois.txt")
