"""
© 2025 Matheus Marcelino Lopes
Todos os direitos reservados.

Projeto: Sistema Militar Gerador de Cartões de Veículos
GitHub: https://github.com/Matheus-Marcelino/Cadastro-de-Veiculos.git

Este software é protegido pela Lei de Software Brasileira (Lei nº 9.609/1998).
É proibida a cópia, redistribuição ou uso comercial sem autorização expressa do autor.
O uso não autorizado para fins comerciais constitui violação de direitos autorais e está sujeito a penalidades legais.
"""
from cx_Freeze import setup, Executable
import sys
import os
import kivy

# --- Função para pegar todas as DLLs de uma pasta ---
def add_dlls_from_folder(src_folder, dest_folder=""):
    files = []
    if os.path.exists(src_folder):
        for f in os.listdir(src_folder):
            if f.endswith(".dll"):
                files.append((os.path.join(src_folder, f), os.path.join(dest_folder, f)))
    return files

# --- Configurações dos arquivos incluídos ---
include_files = [
    # copia as imagens para o exe
    #("15rcmecicon.png", "15rcmecicon.png"),
    #("15rcmec.png", "15rcmec.png"),
    #("camuflado.jpg", "camuflado.jpg"),

    # copia a pasta imagens para o exe
    ("images", "images"),
    ("properties.kv", "properties.kv")                                  
]

# --- Adiciona as DLLs do Kivy ---
kivy_dir = os.path.dirname(kivy.__file__)

# SDL2 DLLs
sdl2_dir = os.path.join(kivy_dir, "deps", "sdl2")
include_files += add_dlls_from_folder(sdl2_dir)

# GLEW DLL
glew_dir = os.path.join(kivy_dir, "deps", "glew")
include_files += add_dlls_from_folder(glew_dir)

# GStreamer DLLs
gstreamer_dir = os.path.join(kivy_dir, "deps", "gstreamer", "bin")
include_files += add_dlls_from_folder(gstreamer_dir)

# --- Adiciona a pasta com suas DLLs (api_dlls) ---
api_dlls_dir = os.path.join(os.getcwd(), "api_dlls")
include_files += add_dlls_from_folder(api_dlls_dir, dest_folder="api_dlls")

# --- Pacotes usados pelo app ---
packages = [
    "kivy",
    "kivymd",
    "reportlab",
    "qrcode",
    "os",
    "pathlib",
    "shutil",
    "json",
    "sys",
    "getpass",
    "webbrowser",
]

# --- Opções do build ---
build_exe_options = {
    "build_exe": "SMGCV",
    "packages": packages,
    "include_files": include_files,
    "include_msvcr": True,  # inclui as DLLs do Visual C++
}

# --- Tipo de executável (sem console no Windows) ---
base = "Win32GUI" if sys.platform == "win32" else None

# --- Configuração final ---
setup(
    name="Sistema Militar Gerador de Cartões de Veículos",
    version="1.0",
    description="Aplicativo Gerador de Cartões para Veículos Militares",
    author="Matheus Marcelino Lopes",
    author_email="matheussmarcelinolopes@gmail.com",
    options={"build_exe": build_exe_options},
    executables=[Executable(
        script="main.py",
        base=base,
        icon="F:\BackUp\codigos\Cadastro de veiculos\cad.ico",  # ícone do executável (opcional)
        target_name="SMGCV.exe"
    )]
)
