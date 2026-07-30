#!/bin/bash

# Interrompe o script se algum comando der erro
set -e

echo "🚀 Iniciando compilação do Flatpak..."

# 1. Limpa e compila os arquivos
flatpak-builder --force-clean build-dir org.focodotrabalho.App.yaml

# 2. Exporta para o repositório local
flatpak-builder --repo=repo --force-clean build-dir org.focodotrabalho.App.yaml

# 3. Gera o arquivo final .flatpak pronto para instalar
flatpak build-bundle repo foco-no-trabalho.flatpak org.focodotrabalho.App

echo "✅ Compilação concluída! O arquivo foco-no-trabalho.flatpak está pronto."
