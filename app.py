import os
from pathlib import Path
import yt_dlp

FFMPEG_PATH = "/data/data/com.termux/files/usr/bin/ffmpeg"

def get_music_folder():
    """Garante a pasta Music existe e retorna o caminho"""
    music_path = os.path.join("/storage/emulated/0", "Music")
    os.makedirs(music_path, exist_ok=True)
    return music_path

def sanitize_filename(filename):
    """Remove caracteres inválidos para nomes de arquivo"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename[:240]  # Limita o tamanho do nome

def download_media():
    url = input("▶️ URL do vídeo/playlist: ").strip()
    
    if not url.startswith(('http://', 'https://')):
        print("❌ URL inválida! Deve começar com http:// ou https://")
        return

    music_path = get_music_folder()
    print(f"📁 Salvando em: {music_path}")

    ydl_opts = {
        'ffmpeg_location': FFMPEG_PATH,
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(music_path, '%(title)s.%(ext)s'),
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'FFmpegMetadata',
                'add_metadata': True,
            },
            {
                'key': 'EmbedThumbnail',
            }
        ],
        'writethumbnail': True,
        'restrictfilenames': True,
        'fixup': 'warn',
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
    }

    try:
        print("\n⏳ Processando...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Renomeia os arquivos para garantir compatibilidade
            if 'entries' in info:  # Playlist
                for entry in info['entries']:
                    if entry:
                        old_path = os.path.join(music_path, f"{entry['title']}.mp3")
                        new_name = sanitize_filename(entry['title']) + ".mp3"
                        new_path = os.path.join(music_path, new_name)
                        os.rename(old_path, new_path)
            else:  # Vídeo único
                old_path = os.path.join(music_path, f"{info['title']}.mp3")
                new_name = sanitize_filename(info['title']) + ".mp3"
                new_path = os.path.join(music_path, new_name)
                os.rename(old_path, new_path)

        print("\n✅ Download concluído com sucesso!")
        print(f"📌 Pasta de destino: {music_path}")
        print("🎧 Use um player como VLC ou MX Player para reproduzir")

    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        if "ffmpeg" in str(e).lower():
            print("🔧 Solução: Execute 'pkg install ffmpeg' no Termux")
        elif "No space left" in str(e):
            print("🔧 Solução: Libere espaço no dispositivo")
        elif "unavailable" in str(e).lower():
            print("🔧 O vídeo pode estar restrito ou privado")

if __name__ == "__main__":
    print("=== YouTube to MP3 Converter ===")
    print("Requisitos instalados? Execute:")
    print("1. termux-setup-storage")
    print("2. pkg install ffmpeg python")
    print("3. pip install yt-dlp")
    print("="*40)
    
    download_media()
