import os
from pathlib import Path
import yt_dlp

FFMPEG_PATH = "/data/data/com.termux/files/usr/bin/ffmpeg"

def get_music_folder():
    paths = [
        "/storage/emulated/0/Music",
        "/sdcard/Music",
        os.path.join(str(Path.home()), "Music")
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    fallback = "/storage/emulated/0/Music"
    os.makedirs(fallback, exist_ok=True)
    return fallback

def sanitize(text):
    return ''.join(c for c in text if c.isalnum() or c in " -_").strip()

def download_playlist():
    url = input("▶️ URL da playlist/vídeo: ").strip()
    if not url.startswith(('http://', 'https://')):
        print("❌ URL inválida!")
        return

    formato = input("🎵 Formato (mp3/mp4): ").lower().strip()
    while formato not in ["mp3", "mp4"]:
        formato = input("⚠️ Digite mp3 ou mp4: ").lower().strip()

    base_path = get_music_folder()
    print(f"📁 Salvando em: {base_path}")

    def generate_outtmpl(info_dict):
        artist = info_dict.get('artist') or info_dict.get('uploader') or "Desconhecido"
        album = info_dict.get('album')
        title = info_dict.get('title') or "Sem título"

        artist = sanitize(artist)
        title = sanitize(title)
        if album:
            album = sanitize(album)
            return os.path.join(base_path, artist, album, f"{title}.%(ext)s")
        else:
            return os.path.join(base_path, artist, f"{title}.%(ext)s")

    class AlbumPathPP(yt_dlp.postprocessor.PostProcessor):
        def run(self, info_dict):
            self._downloader.params['outtmpl'] = generate_outtmpl(info_dict)
            return [], info_dict

    def progress_hook(d):
        if isinstance(d, dict) and d.get('status') == 'downloading':
            percent = d.get('_percent_str', '').strip()
            speed = d.get('_speed_str', '').strip()
            eta = d.get('_eta_str', '').strip()
            print(f"\r⬇️ {percent} {speed} ETA: {eta}", end='')

    ydl_opts = {
        'ffmpeg_location': FFMPEG_PATH,
        'format': 'bestaudio/best' if formato == 'mp3' else 'bestvideo+bestaudio/best',
        'quiet': False,
        'no_warnings': False,
        'progress_hooks': [progress_hook],
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
            {'key': 'EmbedThumbnail'},
            {'key': 'FFmpegMetadata'},
        ] if formato == 'mp3' else [],
        'outtmpl': '%(title)s.%(ext)s',  # temporário
    }

    try:
        print("\n⏳ Baixando...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.add_post_processor(AlbumPathPP())
            ydl.download([url])
        print("\n✅ Finalizado!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        if "ffmpeg" in str(e).lower():
            print("ℹ️ Solução: pkg install ffmpeg")
        elif "No such file or directory" in str(e):
            print("ℹ️ Solução: termux-setup-storage")

if __name__ == "__main__":
    print("=== YouTube Music Downloader (Termux) ===")
    print("1. termux-setup-storage")
    print("2. pkg install ffmpeg python")
    print("3. pip install yt-dlp")
    print("="*40)
    download_playlist()
    
