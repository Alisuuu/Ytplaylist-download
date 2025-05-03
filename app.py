#!/data/data/com.termux/files/usr/bin/python3

import os
import sys
import subprocess

def install_dependencies():
    """Instala todas as dependências automaticamente"""
    print("🔧 Instalando dependências necessárias...")
    commands = [
        'pkg update -y',
        'pkg upgrade -y',
        'pkg install -y python ffmpeg git',
        'pip install --upgrade pip',
        'pip install yt-dlp mutagen',
        'termux-setup-storage'
    ]
    
    for cmd in commands:
        try:
            print(f"Executando: {cmd}")
            subprocess.run(cmd, shell=True, check=True)
        except Exception as e:
            print(f"⚠️ Erro ao executar {cmd}: {str(e)}")
            return False
    return True

def main():
    # Verifica e instala dependências
    if not install_dependencies():
        print("❌ Falha na instalação das dependências")
        sys.exit(1)

    # Agora importa os módulos após instalação
    try:
        import yt_dlp
        from mutagen.id3 import ID3, TIT2, TPE1, TALB, APIC
        from mutagen.mp3 import MP3
        from urllib.request import urlopen
    except ImportError as e:
        print(f"❌ Erro crítico: {str(e)}")
        sys.exit(1)

    # Configurações principais
    FFMPEG_PATH = "/data/data/com.termux/files/usr/bin/ffmpeg"
    MUSIC_FOLDER = "/storage/emulated/0/Music"

    def create_music_folder():
        """Cria a pasta de música se não existir"""
        os.makedirs(MUSIC_FOLDER, exist_ok=True)
        return MUSIC_FOLDER

    def download_and_organize():
        """Função principal de download"""
        url = input("\n🎵 Cole a URL do YouTube/YouTube Music: ").strip()
        
        if not url.startswith(('http://', 'https://')):
            print("\n⚠️ URL inválida! Deve começar com http:// ou https://")
            return

        music_path = create_music_folder()
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
            print("\n⬇️ Baixando... (Isso pode levar alguns minutos)")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print("\n✅ Download concluído com sucesso!")
            print(f"🎧 Música salva em: {music_path}")
        except Exception as e:
            print(f"\n❌ Erro durante o download: {str(e)}")

    # Interface do usuário
    print("\n=== YouTube Music Downloader ===")
    print("📌 Funcionalidades:")
    print("- Baixa músicas do YouTube e YouTube Music")
    print("- Converte para MP3 320kbps")
    print("- Adiciona metadados e capa automaticamente")
    print("="*50)
    
    download_and_organize()
    input("\nPressione Enter para sair...")

if __name__ == "__main__":
    main()
