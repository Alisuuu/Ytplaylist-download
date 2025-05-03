import os
import re
import subprocess
from pathlib import Path
from ytmusicapi import YTMusic
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
import yt_dlp

# Função para instalar dependências do sistema e pacotes Python
def install_dependencies():
    try:
        print("🔧 Instalando dependências...")
        subprocess.check_call(["pkg", "update", "-y"])
        subprocess.check_call(["pkg", "upgrade", "-y"])
        subprocess.check_call(["pkg", "install", "python", "ffmpeg", "git", "-y"])
        subprocess.check_call(["pip", "install", "yt-dlp", "ytmusicapi", "mutagen"])
        subprocess.check_call(["termux-setup-storage"])
        print("✅ Dependências instaladas com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        exit(1)

# Função para obter o caminho da pasta de músicas
def get_music_folder():
    base = "/storage/emulated/0/Music"
    os.makedirs(base, exist_ok=True)
    return base

# Função para sanitizar o nome da pasta ou arquivo (remover caracteres inválidos)
def sanitize(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

# Função para buscar os metadados da música no YouTube Music
def fetch_metadata(query):
    search = ytmusic.search(query, filter="songs")
    if not search:
        return None
    data = search[0]
    artist = data["artists"][0]["name"] if data.get("artists") else "Desconhecido"
    album = data["album"]["name"] if data.get("album") else None
    title = data["title"]
    return {
        "artist": sanitize(artist),
        "album": sanitize(album) if album else None,
        "title": sanitize(title)
    }

# Função para adicionar os metadados ID3 no arquivo MP3
def set_id3_tags(file_path, metadata):
    audio = MP3(file_path, ID3=EasyID3)
    audio["title"] = metadata["title"]
    audio["artist"] = metadata["artist"]
    if metadata["album"]:
        audio["album"] = metadata["album"]
    audio.save()

# Função para mostrar o progresso do download
def progress_hook(d):
    if not isinstance(d, dict) or d.get('status') != 'downloading':
        return
    print(f"\r⬇️ {d.get('_percent_str', '').strip()} {d.get('_speed_str', '').strip()} ETA: {d.get('_eta_str', '').strip()}", end='')

# Função principal para baixar a música
def download_music():
    url = input("🎵 Link do vídeo ou playlist: ").strip()
    metadata = fetch_metadata(url)
    if not metadata:
        print("⚠️ Não foi possível obter metadados. Usando título do vídeo.")
        metadata = {"artist": "Desconhecido", "album": None, "title": "%(title)s"}

    base = get_music_folder()
    target_dir = os.path.join(base, metadata["artist"])
    if metadata["album"]:
        target_dir = os.path.join(target_dir, metadata["album"])
    os.makedirs(target_dir, exist_ok=True)

    outtmpl = os.path.join(target_dir, f"{metadata['title']}.%(ext)s")

    opts = {
        'format': 'bestaudio/best',
        'ffmpeg_location': "/data/data/com.termux/files/usr/bin/ffmpeg",
        'outtmpl': outtmpl,
        'quiet': False,
        'no_warnings': True,
        'progress_hooks': [progress_hook],
        'postprocessors': [
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}
        ]
    }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            print("\n⏳ Baixando...")
            ydl.download([url])

        mp3_path = outtmpl.replace('%(ext)s', 'mp3')
        if os.path.exists(mp3_path):
            set_id3_tags(mp3_path, metadata)
        print(f"\n✅ Baixado com sucesso em: {mp3_path}")

    except Exception as e:
        print(f"\n❌ Erro: {e}")

# Função principal do script
def main():
    print("=== YouTube Music Downloader ===")
    install_dependencies()  # Instala as dependências
    download_music()

if __name__ == "__main__":
    main()
