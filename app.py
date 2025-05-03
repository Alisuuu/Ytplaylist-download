#!/data/data/com.termux/files/usr/bin/python3

import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Instala todas as dependências automaticamente"""
    print("🔧 Instalando dependências necessárias...")
    commands = [
        'pkg update -y',
        'pkg upgrade -y',
        'pkg install -y python ffmpeg',
        'pip install --upgrade pip',
        'pip install yt-dlp mutagen',
        'termux-setup-storage'
    ]
    
    for cmd in commands:
        try:
            print(f"Executando: {cmd}")
            subprocess.run(cmd, shell=True, check=True)
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Erro ao executar: {cmd}")
            print(f"Detalhes: {e}")
            return False
    return True

def check_and_install():
    """Verifica e instala dependências se necessário"""
    try:
        import yt_dlp
        from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC
        return True
    except ImportError:
        print("📦 Dependências não encontradas, iniciando instalação...")
        return install_dependencies()

def main():
    if not check_and_install():
        print("❌ Falha na instalação das dependências")
        sys.exit(1)

    # Agora importa os módulos principais
    import yt_dlp
    from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC
    from mutagen.mp3 import MP3
    from urllib.request import urlopen

    # Restante do seu código aqui...
    def get_music_folder():
        music_path = os.path.join("/storage/emulated/0", "Music")
        os.makedirs(music_path, exist_ok=True)
        return music_path

    def download_media():
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
        }

        try:
            print("\n⬇️ Baixando...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("\n✅ Download concluído!")
        except Exception as e:
            print(f"\n❌ Erro: {str(e)}")

    print("\n=== YouTube Music Downloader ===")
    download_media()

if __name__ == "__main__":
    main()
    input("\nPressione Enter para sair...")
