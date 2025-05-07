import os
import re
import requests
from pathlib import Path
import yt_dlp

FFMPEG_PATH = "/data/data/com.termux/files/usr/bin/ffmpeg"

def get_music_folder():
    possible_paths = [
        "/storage/emulated/0/Music",
        "/sdcard/Music",
        os.path.join(str(Path.home()), "Music"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    fallback = "/storage/emulated/0/Music"
    os.makedirs(fallback, exist_ok=True)
    return fallback

def sanitize(text):
    return ''.join(c for c in text if c.isalnum() or c in " _-").strip() or "Desconhecido"

def buscar_metadados_deezer(titulo):
    try:
        query = re.sub(r"\([^)]*\)|\[.*?\]", "", titulo).strip()  # remove "(Official Video)", etc
        res = requests.get(f"https://api.deezer.com/search?q={query}")
        data = res.json()
        if data["data"]:
            faixa = data["data"][0]
            artista = faixa["artist"]["name"]
            album = faixa["album"]["title"]
            return sanitize(artista), sanitize(album)
    except Exception:
        pass
    return "Desconhecido", "Desconhecido"

def download_playlist():
    while True:
        url = input("\n▶️ URL da playlist/vídeo (ou 'sair' para encerrar): ").strip()
        if url.lower() == 'sair':
            break
        if not url.startswith(('http://', 'https://')):
            print("❌ URL inválida! Use http:// ou https://")
            continue

        formato = input("🎵 Formato (mp3/mp4): ").lower().strip()
        while formato not in ["mp3", "mp4"]:
            formato = input("⚠️ Digite mp3 ou mp4: ").lower().strip()

        music_path = get_music_folder()
        print(f"📁 Os arquivos serão salvos em: {music_path}")

        def progress_hook(d):
            if d['status'] == 'downloading':
                print(f"\r⬇️ {d.get('_percent_str', '')} {d.get('_speed_str', '')} {d.get('_eta_str', '')}", end='')
            elif d['status'] == 'finished':
                print("\n✅ Download finalizado. Convertendo...")

        class DeezerMetadataProcessor:
            def __call__(self, info_dict):
                titulo = info_dict.get("title", "")
                artista, album = buscar_metadados_deezer(titulo)
                info_dict["artist"] = artista
                info_dict["album"] = album
                return info_dict

        ydl_opts = {
            'ffmpeg_location': FFMPEG_PATH,
            'format': 'bestaudio/best' if formato == 'mp3' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(music_path, '%(artist)s/%(album)s/%(title)s.%(ext)s') if formato == 'mp3'
                       else os.path.join(music_path, '%(title)s.%(ext)s'),
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                } if formato == 'mp3' else {},
                {'key': 'EmbedThumbnail'},
                {'key': 'FFmpegMetadata'},
            ],
            'writethumbnail': True,
            'embedthumbnail': True,
            'progress_hooks': [progress_hook],
            'prefer_ffmpeg': True,
            'keepvideo': False,
            'postprocessor_hooks': [DeezerMetadataProcessor()],
        }

        try:
            print("\n⏳ Iniciando download...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"\n✅ Tudo pronto! Arquivos salvos em: {music_path}")
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            if "ffmpeg" in str(e).lower():
                print("ℹ️ Solução: Execute no Termux: 'pkg install ffmpeg'")
            elif "No such file" in str(e):
                print("ℹ️ Execute: 'termux-setup-storage'")

if __name__ == "__main__":
    print("=== YouTube Downloader para Termux ===")
    print("Requisitos: termux-setup-storage | ffmpeg | python | pip install yt-dlp")
    print("="*40)
    download_playlist()
    input("\nPressione Enter para sair...")
