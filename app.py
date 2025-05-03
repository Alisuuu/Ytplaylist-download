import os
import yt_dlp
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TPE2, TCON, TDRC, TRCK, APIC
from mutagen.easyid3 import EasyID3
from urllib.request import urlopen

FFMPEG_PATH = "/data/data/com.termux/files/usr/bin/ffmpeg"

def get_music_folder():
    """Garante a pasta Music existe e retorna o caminho"""
    music_path = os.path.join("/storage/emulated/0", "Music")
    os.makedirs(music_path, exist_ok=True)
    return music_path

def add_proper_metadata(filepath, info):
    """Adiciona metadados de forma compatível com a maioria dos players"""
    try:
        # Primeiro limpa quaisquer metadados existentes
        try:
            audio = MP3(filepath, ID3=ID3)
            audio.delete()
            audio.save()
        except:
            pass

        # Adiciona metadados básicos usando EasyID3 (mais compatível)
        audio = EasyID3(filepath)
        
        # Metadados essenciais
        audio['title'] = info.get('title', 'Desconhecido')
        audio['artist'] = info.get('uploader', 'Desconhecido')
        audio['album'] = info.get('title', 'Desconhecido')
        
        # Metadados opcionais
        if 'track' in info:
            audio['tracknumber'] = str(info['track'])
        if 'release_year' in info:
            audio['date'] = str(info['release_year'])
        
        audio.save()

        # Adiciona a capa do álbum (usando ID3 normal)
        audio = MP3(filepath, ID3=ID3)
        if info.get('thumbnail'):
            try:
                with urlopen(info['thumbnail']) as img:
                    audio.tags.add(
                        APIC(
                            encoding=3,  # UTF-8
                            mime='image/jpeg',
                            type=3,  # 3 é para capa do álbum
                            desc='Capa',
                            data=img.read()
                        )
                    )
            except Exception as e:
                print(f"⚠️ Não foi possível adicionar capa: {e}")

        audio.save()
        
    except Exception as e:
        print(f"⚠️ Erro ao adicionar metadados: {e}")

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
            }
        ],
        'writethumbnail': True,
        'restrictfilenames': True,
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
    }

    try:
        print("\n⏳ Processando...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Processa metadados para cada arquivo
            if 'entries' in info:  # Playlist
                for entry in info['entries']:
                    if entry:
                        filepath = os.path.join(music_path, f"{entry['title']}.mp3")
                        add_proper_metadata(filepath, entry)
            else:  # Vídeo único
                filepath = os.path.join(music_path, f"{info['title']}.mp3")
                add_proper_metadata(filepath, info)

        print("\n✅ Download concluído com sucesso!")
        print("🎧 Os arquivos agora devem ser reconhecidos por todos os players populares")

    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")

if __name__ == "__main__":
    print("=== Conversor YouTube para MP3 (Metadados Corrigidos) ===")
    print("Certifique-se de ter instalado:")
    print("1. termux-setup-storage")
    print("2. pkg install ffmpeg python")
    print("3. pip install yt-dlp mutagen")
    print("="*40)
    
    download_media()
