import os
from pathlib import Path
import yt_dlp

# Caminho para o ffmpeg no Termux
FFMPEG_PATH = "/data/data/com.termux/files/usr/bin/ffmpeg"

def get_music_folder():
    """Cria e retorna o caminho para a pasta Music"""
    possible_paths = [
        "/storage/emulated/0/Music",
        "/storage/emulated/0/music",
        "/sdcard/Music",
        "/sdcard/music",
        os.path.join(str(Path.home()), "Music"),
        os.path.join(str(Path.home()), "music"),
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    music_path = os.path.join("/storage/emulated/0", "Music")
    os.makedirs(music_path, exist_ok=True)
    return music_path

def sanitize_path_component(text):
    """Remove caracteres inválidos para nomes de pastas"""
    return ''.join(c for c in text if c.isalnum() or c in " _-").strip() or "Desconhecido"

def create_directory_structure(base_path, artist, album):
    """Cria a estrutura de pastas Artista/Álbum"""
    # Sanitiza os nomes
    artist = sanitize_path_component(artist)
    album = sanitize_path_component(album)
    
    # Se não tiver álbum, usa "Desconhecido"
    if not album or album.lower() == "none":
        album = "Desconhecido"
    
    # Cria o caminho completo
    full_path = os.path.join(base_path, artist, album)
    
    # Cria as pastas se não existirem
    os.makedirs(full_path, exist_ok=True)
    
    return full_path

def download_playlist():
    url = input("▶️ URL da playlist/vídeo: ").strip()
    if not url.startswith(('http://', 'https://')):
        print("❌ URL inválida! Use http:// ou https://")
        return

    formato = input("🎵 Formato (mp3/mp4): ").lower().strip()
    while formato not in ["mp3", "mp4"]:
        formato = input("⚠️ Digite mp3 ou mp4: ").lower().strip()

    music_path = get_music_folder()
    print(f"📁 Os arquivos serão salvos em: {music_path}")

    def progress_hook(d):
        if d['status'] == 'downloading':
            print(f"\r⬇️ {d.get('_percent_str', '')} {d.get('_speed_str', '')} {d.get('_eta_str', '')}", end='')
        elif d['status'] == 'finished':
            print("\n✅ Download finalizado. Convertendo...")

    def get_outtmpl(info):
        """Gera o caminho de saída baseado nos metadados"""
        artist = info.get('artist') or info.get('uploader') or "Desconhecido"
        album = info.get('album') or "Desconhecido"
        title = info.get('title') or "Sem título"
        
        # Cria a estrutura de pastas
        base_dir = create_directory_structure(music_path, artist, album)
        
        # Retorna o caminho completo do arquivo
        ext = info.get('ext', 'mp3' if formato == 'mp3' else 'mp4')
        return os.path.join(base_dir, f"{sanitize_path_component(title)}.{ext}")

    ydl_opts = {
        'ffmpeg_location': FFMPEG_PATH,
        'format': 'bestaudio/best' if formato == 'mp3' else 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': get_outtmpl,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            },
            {
                'key': 'EmbedThumbnail'
            },
            {
                'key': 'FFmpegMetadata',
            },
        ] if formato == 'mp3' else [],
        'writethumbnail': True if formato == 'mp3' else False,
        'embed-metadata': True if formato == 'mp3' else False,
        'embed-thumbnail': True if formato == 'mp3' else False,
        'progress_hooks': [progress_hook],
        'quiet': False,
        'no_warnings': False,
        'extract_flat': False,
    }

    try:
        print("\n⏳ Iniciando download...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"\n✅ Tudo pronto! Arquivos organizados em: {music_path}")
    except Exception as e:
        print(f"\n❌ Erro durante o download: {str(e)}")
        if "ffmpeg" in str(e).lower():
            print("ℹ️ Solução: Execute no Termux: 'pkg install ffmpeg'")
        elif "No such file or directory" in str(e):
            print("ℹ️ Solução: Execute no Termux: 'termux-setup-storage'")

def main():
    print("=== YouTube Downloader para Termux ===")
    print("Requisitos:")
    print("1. termux-setup-storage")
    print("2. pkg install ffmpeg python")
    print("3. pip install yt-dlp")
    print("="*40)
    
    while True:
        print("\nOpções:")
        print("1. Baixar música/playlist")
        print("2. Sair")
        
        escolha = input("Escolha uma opção (1/2): ").strip()
        
        if escolha == "1":
            download_playlist()
        elif escolha == "2":
            print("Saindo...")
            break
        else:
            print("Opção inválida! Digite 1 ou 2.")

if __name__ == "__main__":
    main()
