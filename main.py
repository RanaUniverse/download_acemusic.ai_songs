from scraper import fetch_song_details

url = "https://acemusic.ai/song/jpsefx7pcdd9?sh=nE0ZoCtIycD"

if __name__ == "__main__":
    data = fetch_song_details(song_url=url)
    print(data)
