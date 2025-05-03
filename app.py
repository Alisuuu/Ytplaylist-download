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
    print("🔧 Instalando/Atualizando dependências...")
    commands = [
        'pkg update -y',
        'pkg upgrade -y',
        'pkg install -y python ffmpeg',
        'pip install --upgrade yt-dlp mutagen',
        'termux-setup-storage'
    ]
    
    for cmd in commands:
        try:
            subprocess.run(cmd.split(), check=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Erro ao executar: {cmd}")
            print(f"Detalhes: {e}")
            sys.exit(1)

def check_dependencies():
    """Verifica se todas as dependências estão instaladas"""
    try:
        import yt_dlp
        from mutagen.id3 import ID3
    except ImportError:
        print("📦 Dependências faltando, instalando...")
        install_dependencies()

def get_music_folder():
    """Cria e retorna o caminho para a pasta Music"""
    music_path = os.path.join("/storage/emulated/0", "Music")
    os.makedirs(music_path, exist_ok=True)
    return music_path

def add_metadata(filepath, info):
    """Adiciona metadados de forma compatível"""
    try:
        audio = MP3(filepath, ID3=ID3)
        
        # Adiciona metadados básicos
        audio.tags.add(TIT2(encoding=3, text=info.get('title', 'Desconhecido')))
        audio.tags.add(TPE1(encoding=3, text=info.get('uploader', 'Desconhecido')))
        audio.tags.add(TALB(encoding=3, text=info.get('title', 'Desconhecido')))
        
        # Adiciona capa do álbum
        if info.get('thumbnail'):
            try:
                with urlopen(info['thumbnail']) as img:
                    audio.tags.add(
                        APIC(
                            encoding=3,
                            mime='image/jpeg',
                            type=3,  # 3 = capa do álbum
                            desc='Capa',
                            data=img.read()
                        )
                    )
            except Exception as e:
                print(f"⚠️ Não foi possível baixar a capa: {e}")
        
        audio.save()
    except Exception as e:
        print(f"⚠️ Erro nos metadados: {e}")

def download_from_ytmusic():
    """Função principal de download"""
    check_dependencies()
    
    FFMPEG_PATH = "/data/data/com.termux/files/usr/bin/ffmpeg"
    url = input("\n🎵 Cole a URL do YouTube Music: ").strip()
    
    if "music.youtube.com" not in url.lower():
        print("\n⚠️ Use uma URL do YouTube Music (ex: music.youtube.com/watch?v=...)")
        return

    music_path = get_music_folder()
    print(f"\n📁 Pasta de destino: {music_path}")

    ydl_opts = {
        'ffmpeg_location': FFMPEG_PATH,
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(music_path, '%(title)s.%(ext)s'),
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
    }

    try:
        print("\n⬇️ Baixando música...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # Processa metadados
            if 'entries' in info:  # Playlist
                for entry in info['entries']:
                    if entry:
                        filepath = os.path.join(music_path, f"{entry['title']}.mp3")
                        add_metadata(filepath, entry)
            else:  # Vídeo único
                filepath = os.path.join(music_path, f"{info['title']}.mp3")
                add_metadata(filepath, info)

        print("\n✅ Download concluído com sucesso!")
        print(f"🎧 Arquivo salvo em: {music_path}")

    except Exception as e:
        print(f"\n❌ Erro durante o download: {str(e)}")

if __name__ == "__main__":
    print("\n=== YouTube Music Downloader ===")
    print("📌 Este script irá:")
    print("- Instalar automaticamente as dependências")
    print("- Baixar músicas do YouTube Music")
    print("- Adicionar metadados e capas automaticamente")
    print("="*50)
    
    # Verifica e instala dependências se necessário
    try:
        import yt_dlp
        from mutagen.id3 import ID3
    except ImportError:
        install_dependencies()
    
    download_from_ytmusic()
    
    # Mantém o terminal aberto para ver os resultados
    input("\nPressione Enter para sair...")
