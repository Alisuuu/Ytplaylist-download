import os
from pathlib import Path
import yt_dlp

FFMPEG_PATH = "/data/data/com.termux/files/usr/bin/ffmpeg"

def get_music_folder():
    """Cria e retorna o caminho para a pasta music"""
    music_path = os.path.join("/storage/emulated/0", "Music")
    os.makedirs(music_path, exist_ok=True)
    return music_path

def set_metadata(info, filepath):
    """Adiciona metadados ao arquivo MP3"""
    from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB
    from mutagen.mp3 import MP3
    
    try:
        audio = MP3(filepath, ID3=ID3)
        
        # Adiciona capa do álbum
        if info.get('thumbnail'):
            with yt_dlp.YoutubeDL().urlopen(info['thumbnail']) as img:
                audio.tags.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,  # 3 é para capa do álbum
                    data=img.read()
                ))
        
        # Adiciona metadados básicos
        audio.tags.add(TIT2(encoding=3, text=info.get('title', '')))
        audio.tags.add(TPE1(encoding=3, text=info.get('uploader', '')))
        audio.tags.add(TALB(encoding=3, text=info.get('title', '')))
        
        audio.save()
    except Exception as e:
        print(f"⚠️ Não foi possível adicionar metadados: {e}")

def download_playlist():
    url = input("▶️ URL da playlist/vídeo: ").strip()
    
    if not url.startswith(('http://', 'https://')):
        print("❌ URL inválida! Use http:// ou https://")
        return

    music_path = get_music_folder()
    print(f"📁 Os arquivos serão salvos em: {music_path}")
    
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
                'already_have_thumbnail': False,
            }
        ],
        'writethumbnail': True,
        'quiet': False,
        'no_warnings': False,
        'progress_hooks': [lambda d: print(f"\r⬇️ Progresso: {d.get('_percent_str', '?')}", end='')],
        'extract_flat': False,
    }

    try:
        print("\n⏳ Iniciando download...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            
            # Processa metadados adicionais para cada entrada
            if 'entries' in info_dict:  # É uma playlist
                for entry in info_dict['entries']:
                    if entry:
                        filepath = os.path.join(music_path, f"{entry['title']}.mp3")
                        set_metadata(entry, filepath)
            else:  # É um único vídeo
                filepath = os.path.join(music_path, f"{info_dict['title']}.mp3")
                set_metadata(info_dict, filepath)
                
        print(f"\n✅ Download concluído! Arquivos com metadados em: {music_path}")
    except Exception as e:
        print(f"\n❌ Erro durante o download: {str(e)}")

if __name__ == "__main__":
    print("=== YouTube Downloader com Metadados ===")
    print("Requisitos:")
    print("1. termux-setup-storage")
    print("2. pkg install ffmpeg python")
    print("3. pip install yt-dlp mutagen")
    print("="*40)
    
    download_playlist()
