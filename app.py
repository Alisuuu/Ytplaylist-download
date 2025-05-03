import os
import sys
import subprocess
from pathlib import Path
import yt_dlp
from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC
from mutagen.mp3 import MP3
from urllib.request import urlopen

def install_dependencies():
    """Instala todas as dependências automaticamente"""
    print("🔧 Instalando dependências...")
    commands = [
        'pkg update -y',
        'pkg upgrade -y',
        'pkg install -y python ffmpeg',
        'pip install --upgrade yt-dlp mutagen',
        'termux-setup-storage'
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Erro ao executar: {cmd}")
            print(f"Detalhes: {e}")
            return False
    return True

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    try:
        import yt_dlp
        from mutagen.id3 import ID3
        return True
    except ImportError:
        return install_dependencies()

def get_album_folder(music_path, album_name, artist_name):
    """Cria e retorna o caminho para a pasta do álbum"""
    # Remove caracteres inválidos
    valid_chars = "-_.() %s%s" % (os.sep, os.sep)
    album_name = ''.join(c for c in album_name if c.isalnum() or c in valid_chars).strip()
    artist_name = ''.join(c for c in artist_name if c.isalnum() or c in valid_chars).strip()
    
    # Pasta do artista -> álbum
    artist_path = os.path.join(music_path, artist_name)
    album_path = os.path.join(artist_path, album_name)
    
    os.makedirs(album_path, exist_ok=True)
    return album_path

def add_metadata(filepath, info):
    """Adiciona metadados e retorna informações do álbum"""
    try:
        audio = MP3(filepath, ID3=ID3)
        
        # Extrai metadados
        title = info.get('title', 'Desconhecido')
        uploader = info.get('uploader', 'Desconhecido')
        album = info.get('album', title)  # Usa o título como álbum se não tiver
        
        # Adiciona metadados
        audio.tags.add(TIT2(encoding=3, text=title))
        audio.tags.add(TPE1(encoding=3, text=uploader))
        audio.tags.add(TALB(encoding=3, text=album))
        
        # Capa do álbum
        thumbnail = info.get('thumbnail') or info.get('thumbnails', [{}])[-1].get('url', '')
        if thumbnail:
            try:
                with urlopen(thumbnail) as img:
                    audio.tags.add(
                        APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,
                            desc='Capa',
                            data=img.read()
                        )
                    )
            except Exception as e:
                print(f"⚠️ Não foi possível baixar a capa: {e}")
        
        audio.save()
        return {'artist': uploader, 'album': album}
    except Exception as e:
        print(f"⚠️ Erro nos metadados: {e}")
        return {'artist': 'Desconhecido', 'album': 'Desconhecido'}

def download_audio():
    """Função principal de download"""
    if not check_dependencies():
        print("❌ Falha ao instalar dependências")
        return

    FFMPEG_PATH = "/data/data/com.termux/files/usr/bin/ffmpeg"
    url = input("\n🎵 Cole a URL do YouTube/YouTube Music: ").strip()
    
    if not url.startswith(('http://', 'https://')):
        print("\n⚠️ URL inválida! Deve começar com http:// ou https://")
        return

    music_path = os.path.join("/storage/emulated/0", "Music")
    os.makedirs(music_path, exist_ok=True)
    print(f"\n📁 Pasta base: {music_path}")

    ydl_opts = {
        'ffmpeg_location': FFMPEG_PATH,
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(music_path, 'temp_%(title)s.%(ext)s'),
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
            }
        ],
        'writethumbnail': True,
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
    }

    try:
        print("\n⬇️ Baixando e organizando...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            if 'entries' in info:  # Playlist
                for entry in info['entries']:
                    if entry:
                        temp_path = os.path.join(music_path, f"temp_{entry['title']}.mp3")
                        metadata = add_metadata(temp_path, entry)
                        
                        # Move para pasta do álbum
                        album_path = get_album_folder(music_path, metadata['album'], metadata['artist'])
                        final_path = os.path.join(album_path, f"{entry['title']}.mp3")
                        os.rename(temp_path, final_path)
                        print(f"✓ {entry['title']} → {metadata['artist']}/{metadata['album']}")
            else:  # Vídeo único
                temp_path = os.path.join(music_path, f"temp_{info['title']}.mp3")
                metadata = add_metadata(temp_path, info)
                
                # Move para pasta do álbum
                album_path = get_album_folder(music_path, metadata['album'], metadata['artist'])
                final_path = os.path.join(album_path, f"{info['title']}.mp3")
                os.rename(temp_path, final_path)
                print(f"✓ {info['title']} → {metadata['artist']}/{metadata['album']}")

        print("\n✅ Download concluído e organizado!")
        print(f"🎧 Estrutura criada em: {music_path}")

    except Exception as e:
        print(f"\n❌ Erro durante o download: {str(e)}")
        # Limpa arquivos temporários
        for f in os.listdir(music_path):
            if f.startswith('temp_'):
                os.remove(os.path.join(music_path, f))

if __name__ == "__main__":
    print("\n=== Organizador de Músicas ===")
    print("📌 Este script:")
    print("- Baixa de YouTube/YT Music")
    print("- Organiza em pastas Artista/Álbum")
    print("- Mantém metadados e capas")
    print("="*50)
    
    download_audio()
    
    # Mantém o terminal aberto
    input("\nPressione Enter para sair...")
