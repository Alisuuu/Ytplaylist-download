# 📥 YouTube Playlist Downloader for Termux

**Baixe playlists do YouTube/YT Music diretamente no seu Android**

## 🚀 Instalação Rápida
```
pkg update -y && pkg upgrade -y && pkg install python ffmpeg git -y && pip install yt-dlp --upgrade && termux-setup-storage && if [ ! -f yt_playlist_downloader.py ]; then curl -O https://raw.githubusercontent.com/Alisuuu/Ytplaylist-download/refs/heads/main/app.py && mv app.py yt_playlist_downloader.py; fi && python yt_playlist_downloader.py
```
2. Cole a URL da playlist
3. Escolha formato (mp3/mp4)
4. Os arquivos serão salvos em `/storage/emulated/0/Download/`

## ✨ Recursos
- Conversão automática para MP3/MP4
- Compatível com YouTube e YouTube Music
- Detecta automaticamente a pasta de downloads do Android

## ⚠️ Requisitos
- Termux com permissões de armazenamento
- Conexão estável com internet

> Dica: Para playlists privadas, execute `termux-login` primeiro
