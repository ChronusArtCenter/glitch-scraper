import os
import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, unquote

# --- Step 1: Handle command-line argument ---
if len(sys.argv) != 2:
    print("Usage: python main.py <glitch_live_url>")
    print("Example: python main.py https://resonance-concise-centipedes.glitch.me")
    sys.exit(1)

project_url = sys.argv[1]

# --- Step 2: Setup directories ---
output_dir = "glitch_download"
assets_dir = os.path.join(output_dir, "assets")
os.makedirs(assets_dir, exist_ok=True)

# --- Step 3: Download index.html ---
print(f"📥 Fetching {project_url}...")
try:
    response = requests.get(project_url)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"❌ Error fetching {project_url}:\n{e}")
    sys.exit(1)

html_content = response.text
soup = BeautifulSoup(html_content, "html.parser")

# --- Step 4: Find and download assets ---
asset_tags = soup.find_all(["a-asset-item", "audio", "img"])

def download_and_replace(tag):
    src = tag.get("src")
    if not src or src.startswith("data:"):
        return
    parsed_url = urlparse(src)
    filename = os.path.basename(unquote(parsed_url.path))
    local_path = os.path.join(assets_dir, filename)
    print(f"⬇️  Downloading: {filename}")

    try:
        r = requests.get(src)
        r.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(r.content)
        # Rewrite the src in the tag
        tag['src'] = f"assets/{filename}"
    except Exception as e:
        print(f"⚠️  Failed to download {src}: {e}")

for tag in asset_tags:
    download_and_replace(tag)

# --- Step 5: Save rewritten HTML ---
output_html_path = os.path.join(output_dir, "index.html")
with open(output_html_path, "w", encoding="utf-8") as f:
    f.write(str(soup.prettify()))

print(f"\n✅ Finished. Local HTML: {output_html_path}")
print(f"📁 Assets saved to: {assets_dir}")

