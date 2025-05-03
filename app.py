import os
import yt_dlp
from pathlib import Path

# Configurações para Termux
FFMPEG_PATH = "/data/data/com.termux/files/usr/bin/ffmpeg"
MUSIC_FOLDER = "/storage/emulated/0/Music"

def setup_folders():
    """Garante que a pasta de música existe"""
    os.makedirs(MUSIC_FOLDER, exist_ok=True)
    return MUSIC_FOLDER

def download_from_ytmusic():
    url = input("🎵 Cole a URL do YouTube Music: ").strip()
    
    if "music.youtube.com" not in url:
        print("⚠️ Por favor, use uma URL do YouTube Music (music.youtube.com)")
        return

    output_folder = setup_folders()
    print(f"📁 Pasta de destino: {output_folder}")

    ydl_opts = {
        'ffmpeg_location': FFMPEG_PATH,
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            },
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            },
            {
                'key': 'EmbedThumbnail',
                'already_have_thumbnail': False,
            }
        ],
        'writethumbnail': True,
        'extract_flat': False,
        'quiet': False,
        'no_warnings': False,
    }

    try:
        print("\n⬇️ Baixando música...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        print("\n✅ Download completo!")
        print(f"🎧 Arquivo salvo em: {output_folder}")
        print("👉 Use players como: VLC, Poweramp ou MX Player")

    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        if "Private video" in str(e):
            print("🔒 Vídeo privado - não é possível baixar")
        elif "ffmpeg" in str(e):
            print("🔧 Execute: pkg install ffmpeg")

if __name__ == "__main__":
    print("=== YouTube Music Downloader ===")
    print("Requisitos:")
    print("1. termux-setup-storage")
    print("2. pkg install ffmpeg python")
    print("3. pip install yt-dlp")
    print("="*40)
    
    download_from_ytmusic()
