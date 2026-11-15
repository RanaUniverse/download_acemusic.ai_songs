from bs4 import BeautifulSoup
import requests

# Target song page URL
url = "https://acemusic.ai/song/ca77nehisvv2"

# Headers mimicking a real browser request
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Referer": "https://acemusic.ai/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

print("🔍 Fetching page content...")
response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")

    # 1. Extract Song Audio URL (from Open Graph meta tag or audio tag)
    og_audio = soup.find("meta", property="og:audio")
    audio_url = og_audio["content"] if og_audio else None

    if not audio_url:
        audio_tag = soup.find("audio")
        if audio_tag and audio_tag.get("src"):
            audio_url = audio_tag["src"]

    # 2. Extract Cover Image URL (from Open Graph meta tag)
    og_image = soup.find("meta", property="og:image")
    image_url = og_image["content"] if og_image else None

    print("\n--- Extracted Links ---")
    print(f"🎵 Song MP3 URL: {audio_url}")
    print(f"🖼️ Cover Image URL: {image_url}")

else:
    print(f"❌ Failed to fetch page. Status code: {response.status_code}")
