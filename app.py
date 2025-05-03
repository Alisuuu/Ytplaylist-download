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

def get_music_folder():
    """Cria e retorna o caminho para a pasta Music"""
    music_path = os.path.join("/storage/emulated/0", "Music")
    os.makedirs(music_path, exist_ok=True)
    return music_path

def add_metadata(filepath, info):
    """Adiciona metadados de forma compatível"""
    try:
        audio = MP3(filepath, ID3=ID3)
        
        # Metadados básicos
        title = info.get('title', 'Desconhecido')
        uploader = info.get('uploader', 'Desconhecido')
        
        audio.tags.add(TIT2(encoding=3, text=title))
        audio.tags.add(TPE1(encoding=3, text=uploader))
        audio.tags.add(TALB(encoding=3, text=title))
        
        # Capa do álbum (se disponível)
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
    except Exception as e:
        print(f"⚠️ Erro nos metadados: {e}")

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
        'extract_flat': False,
    }

    try:
        print("\n⬇️ Baixando áudio...")
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

        print("\n✅ Download concluído!")
        print(f"🎧 Arquivo(s) salvo(s) em: {music_path}")

    except Exception as e:
        print(f"\n❌ Erro durante o download: {str(e)}")

if __name__ == "__main__":
    print("\n=== YouTube/YT Music Downloader ===")
    print("📌 Este script:")
    print("- Baixa de YouTube e YouTube Music")
    print("- Mantém metadados e capas")
    print("- Qualidade 320kbps")
    print("="*50)
    
    download_audio()
    
    # Mantém o terminal aberto
    input("\nPressione Enter para sair...")
