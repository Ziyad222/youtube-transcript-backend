#!/usr/bin/env bash

# Télécharger la dernière version statique de ffmpeg (compatible x86_64 Linux)
curl -L https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz -o ffmpeg.tar.xz

# Extraire l'archive
mkdir -p ffmpeg
tar -xJf ffmpeg.tar.xz -C ffmpeg --strip-components=1

# Donner les droits d'exécution à ffmpeg
chmod +x ffmpeg/ffmpeg

# Installer les dépendances Python
pip install -r requirements.txt
