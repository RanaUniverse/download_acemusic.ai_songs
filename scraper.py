"""
scraper.py

"""

from dataclasses import dataclass, field


from bs4 import BeautifulSoup
import requests

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0",
    "Referer": "https://acemusic.ai/",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


@dataclass
class LyricSection:
    """
    Represents a single secion of song lyrics
    intro verse chorus
    """

    heading: str
    content: str


@dataclass
class SongMetadata:
    """
    Holds artist and track metadata
    """

    author: str | None = None
    duration: str | None = None
    date: str | None = None


@dataclass
class SongDetails:
    title: str | None = None
    audio_url: str | None = None
    cover_url: str | None = None
    metadata: SongMetadata = field(default_factory=SongMetadata)
    lyrics: list[LyricSection] = field(default_factory=list)  # type: ignore


def fetch_song_details(song_url: str) -> SongDetails | None:
    """
    Scrapes song metadata, audio url, cover image and so on
    """
    try:
        response = requests.get(
            song_url,
            headers=headers,
            timeout=10,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Network or HTTP error occurred: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # later i will remove this print line
    # print(soup)
    # print(type(soup))

    title_tag = soup.select_one("main.song-page div.sp-title h1")

    if title_tag:
        title = title_tag.get_text(strip=True)
    else:
        # Fallback to Open Graph meta tag if the <h1> isn't found
        meta_title_tag = soup.find("meta", property="og:title")
        title_from_html = (
            meta_title_tag["content"] if meta_title_tag else "Unknown Title"
        )
        title = str(title_from_html)

    og_audio = soup.find("meta", property="og:audio")
    audio_url = (
        str(og_audio["content"]) if og_audio and og_audio.get("content") else None
    )

    og_image = soup.find("meta", property="og:image")
    cover_url = (
        str(og_image["content"]) if og_image and og_image.get("content") else None
    )

    meta_tag = soup.select_one("p.sp-meta")

    author = None
    duration = None
    release_date = None

    if meta_tag:
        # Extract the timestamp string (e.g. " · 3:05 · Nov 15, 2026")
        when_tag = meta_tag.select_one("span.sp-when")
        if when_tag:
            when_text = when_tag.get_text(strip=True)

            # Parse duration and date by splitting across separators
            # Splits string into parts like ['', '3:05', 'Nov 15, 2026']
            parts = [
                p.strip() for p in when_text.replace("·", "|").split("|") if p.strip()
            ]
            if len(parts) >= 1:
                duration = parts[0]  # "3:05"
            if len(parts) >= 2:
                release_date = parts[1]  # "Nov 15, 2026"

            # 3. Extract Author by taking full text and removing the when_text
            full_text = meta_tag.get_text(strip=True)
            author = full_text.replace(when_text, "").strip()

    # Example for parsing lyrics sections if you want to include them now:
    lyrics_list = []
    lyrics_section = soup.find("section", class_="sp-lyrics")
    if lyrics_section:
        for sec in lyrics_section.find_all("div", class_="sp-sec"):
            h3 = sec.find("h3")
            p = sec.find("p")

            heading = h3.get_text(strip=True) if h3 else "Section"
            if p:
                for br in p.find_all("br"):
                    br.replace_with("\n")
                content = p.get_text()
            else:
                content = ""
            lyrics_list.append(LyricSection(heading=heading, content=content)) # type: ignore

    return SongDetails(
        title=title,
        audio_url=audio_url,
        cover_url=cover_url,
        metadata=SongMetadata(
            author=author,
            duration=duration,
            date=release_date,
        ),
        # lyrics=lyrics_list,
    )


if __name__ == "__main__":
    url = "https://acemusic.ai/song/jpsefx7pcdd9?sh=nE0ZoCtIycD"
    data = fetch_song_details(song_url=url)
    print(data)
