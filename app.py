import yt_dlp
import os
from pathlib import Path

# Configuração especial para Termux
FFMPEG_PATH = "/data/data/com.termux/files/usr/bin/ffmpeg"

def get_download_folder():
    """Obtém o caminho de downloads do Android"""
    android_paths = [
        "/storage/emulated/0/Download",
        "/sdcard/Download",
        os.path.join(str(Path.home()), "storage", "shared", "Download")  # Corrigido: parêntese fechado
    ]
    
    for path in android_paths:
        if os.path.exists(path):
            return path
    return os.getcwd()  # Fallback para pasta atual

def download_playlist():
    url = input("▶️ URL da playlist: ").strip()
    
    if not url.startswith(('http://', 'https://')):
        print("❌ URL inválida! Use http:// ou https://")
        return

    formato = input("🎵 Formato (mp3/mp4): ").lower()
    while formato not in ["mp3", "mp4"]:
        formato = input("⚠️ Digite mp3 ou mp4: ").lower()

    download_path = get_download_folder()
    os.makedirs(download_path, exist_ok=True)
    
    # Configuração robusta para Termux
    ydl_opts = {
        'ffmpeg_location': FFMPEG_PATH,
        'format': 'bestaudio/best' if formato == 'mp3' else 'best[ext=mp4]',
        'outtmpl': f'{download_path}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }] if formato == 'mp3' else [],
        'quiet': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print("\n⬇️ Baixando...")
            ydl.download([url])
        print(f"\n✅ Concluído! Arquivos em: {download_path}")
    except Exception as e:
        print(f"\n❌ Falha crítica: {str(e)}")
        if "ffmpeg" in str(e).lower():
            print("Dica: Execute 'pkg install ffmpeg' no Termux")

if __name__ == "__main__":
    print("=== Downloader para Termux ===")
    print("Certifique-se de ter executado:")
    print("termux-setup-storage")
    print("pkg install ffmpeg")
    download_playlist()