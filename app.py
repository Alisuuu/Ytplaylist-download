import os
from pathlib import Path
import yt_dlp

# Caminho para o ffmpeg no Termux
FFMPEG_PATH = "/data/data/com.termux/files/usr/bin/ffmpeg"

def get_music_folder():
    """Cria e retorna o caminho para a pasta Music"""
    possible_paths = [
        "/storage/emulated/0/Music",
        "/storage/emulated/0/music",
        "/sdcard/Music",
        "/sdcard/music",
        os.path.join(str(Path.home()), "Music"),
        os.path.join(str(Path.home()), "music"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    music_path = os.path.join("/storage/emulated/0", "Music")
    os.makedirs(music_path, exist_ok=True)
    return music_path

def sanitize_path_component(text):
    """Remove caracteres inválidos para nomes de pastas"""
    return ''.join(c for c in text if c.isalnum() or c in " _-").strip() or "Desconhecido"

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

        ydl_opts = {
            'ffmpeg_location': FFMPEG_PATH,
            'format': 'bestaudio/best' if formato == 'mp3' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(music_path, '%(album|Desconhecido)s/%(title)s.%(ext)s') if formato == 'mp3'
                       else os.path.join(music_path, '%(title)s.%(ext)s'),
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                },
                {
                    'key': 'EmbedThumbnail',
                    'already_have_thumbnail': False,
                },
                {
                    'key': 'FFmpegMetadata',
                },
            ] if formato == 'mp3' else [],
            'writethumbnail': True if formato == 'mp3' else False,
            'embed-metadata': True if formato == 'mp3' else False,
            'embed-thumbnail': True if formato == 'mp3' else False,
            'progress_hooks': [progress_hook],
            'quiet': False,
            'no_warnings': False,
            'extract_flat': False,
            'postprocessor_args': [
                '-metadata', 'album_artist=%(album_artist)s',
                '-metadata', 'album=%(album)s',
            ] if formato == 'mp3' else [],
            'prefer_ffmpeg': True,
        }

        try:
            print("\n⏳ Iniciando download...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                if formato == 'mp3' and 'entries' in info_dict:  # É uma playlist
                    album = info_dict.get('title', 'Desconhecido')
                    # Tenta baixar a thumbnail do álbum
                    try:
                        thumbnail_url = info_dict.get('thumbnail')
                        if thumbnail_url:
                            thumb_opts = {
                                'format': 'bestaudio/best',
                                'outtmpl': os.path.join(music_path, f'{album}/cover.%(ext)s'),
                                'writethumbnail': True,
                                'skip_download': True,
                                'quiet': True,
                            }
                            with yt_dlp.YoutubeDL(thumb_opts) as thumb_dl:
                                thumb_dl.download([url])
                    except Exception as e:
                        print(f"⚠️ Não foi possível baixar a capa do álbum: {str(e)}")
            
            print(f"\n✅ Tudo pronto! Arquivos salvos em: {music_path}")
        except Exception as e:
            print(f"\n❌ Erro durante o download: {str(e)}")
            if "ffmpeg" in str(e).lower():
                print("ℹ️ Solução: Execute no Termux: 'pkg install ffmpeg'")
            elif "No such file or directory" in str(e):
                print("ℹ️ Solução: Execute no Termux: 'termux-setup-storage'")

if __name__ == "__main__":
    print("=== YouTube Downloader para Termux ===")
    print("Requisitos:")
    print("1. termux-setup-storage")
    print("2. pkg install ffmpeg python")
    print("3. pip install yt-dlp")
    print("="*40)
    download_playlist()
    input("\nPressione Enter para sair...")
