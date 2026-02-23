#!/usr/bin/env python3
"""Upload new Al Wadi POI media to Cloudinary and generate HTML entries."""
import os
import sys
import json
import cloudinary
import cloudinary.uploader

# Configure Cloudinary
cloudinary.config(
    cloud_name="dn3bxmi9r",
    api_key="145686874393476",
    api_secret="fAp16cHdFbFVIL35qwczP-3K92c"
)

BASE = "G:/My Drive/media/Fadhel"

# New POIs from Fadhel folder for Al Wadi district
NEW_POIS = [
    'جوس',
    'حلاق لمسات زين',
    'سمسم',
    'صيدلية ليمون',
    'درايف',
    'شاورمر',
    'نخلة ساسكو',
    'البطاريات',
    'عربة المجد للإطارات',
    'عربة المجد لغيار الزيت',
    'نظرة الجيدة لزينة السيارات',
    'Good Look',
    'توش توش',
    'ساسكو',
    'غرائب النظارات',
    'لومار',
    'فندق سفن جاردنز',
    'ستديو صقر الدوسري',
    'بقالة ميمونه الدوسري للمواد الغذائية',
    'مطعم بهارات هندي',
    'أكنان العربه',
    'فلافل القمة الشامية',
]

VIDEO_EXTS = {'.mp4', '.mov', '.avi', '.mkv'}
IMAGE_EXTS = {'.jpg', '.jpeg', '.heic', '.png', '.webp'}

file_counter = 625  # Continue after previous batch (Ahmad ended at 624)
all_poi_html = []
total_uploaded = 0
total_failed = 0

for poi_name in NEW_POIS:
    folder_path = os.path.join(BASE, poi_name)
    if not os.path.isdir(folder_path):
        print(f"SKIP (no folder): {poi_name}", flush=True)
        continue

    files = [f for f in os.listdir(folder_path)
             if f != 'desktop.ini' and not f.startswith('.')
             and os.path.splitext(f)[1].lower() in (VIDEO_EXTS | IMAGE_EXTS)]

    if not files:
        print(f"SKIP (no media): {poi_name}", flush=True)
        # Still create POI entry with no media
        poi_html = f'''<div class="poi" data-media="0" data-district="alwadi">
  <h3>{poi_name}</h3>
  <div class="meta">life_convenience | open | Media: 0</div>
  <div class="media-grid">
  </div>
</div>'''
        all_poi_html.append(poi_html)
        continue

    print(f"\nUploading {len(files)} files for: {poi_name}", flush=True)
    media_links = []
    photo_count = 0
    video_count = 0

    for filename in sorted(files):
        filepath = os.path.join(folder_path, filename)
        ext = os.path.splitext(filename)[1].lower()
        name_no_ext = os.path.splitext(filename)[0]
        is_video = ext in VIDEO_EXTS

        resource_type = "video" if is_video else "image"
        public_id = f"alwadi_media/{name_no_ext}_{file_counter}"

        try:
            result = cloudinary.uploader.upload(
                filepath,
                resource_type=resource_type,
                public_id=public_id,
                overwrite=False
            )
            url = result['secure_url']
            if is_video:
                video_count += 1
                media_links.append(f'    <a href="{url}" target="_blank" class="video">Video {video_count}</a>')
            else:
                photo_count += 1
                media_links.append(f'    <a href="{url}" target="_blank">Photo {photo_count}</a>')

            total_uploaded += 1
            print(f"  OK [{file_counter}]: {filename} -> {resource_type}", flush=True)
        except Exception as e:
            total_failed += 1
            print(f"  FAIL [{file_counter}]: {filename} -> {e}", flush=True)

        file_counter += 1

    total_media = photo_count + video_count
    media_grid = "\n".join(media_links)
    poi_html = f'''<div class="poi" data-media="1" data-district="alwadi">
  <h3>{poi_name}</h3>
  <div class="meta">life_convenience | open | Media: {total_media}</div>
  <div class="media-grid">
{media_grid}
  </div>
</div>'''
    all_poi_html.append(poi_html)

# Write the new POI HTML to a file
output_html = "\n".join(all_poi_html)
with open(r'c:\Users\abdul\media\_new_alwadi_pois.txt', 'a', encoding='utf-8') as f:
    f.write("\n" + output_html)

print(f"\n{'='*60}")
print(f"DONE: {total_uploaded} uploaded, {total_failed} failed")
print(f"Generated {len(all_poi_html)} POI entries")
print(f"Output: _new_alwadi_pois.txt")
