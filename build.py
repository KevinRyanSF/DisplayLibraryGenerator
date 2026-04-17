import os
import subprocess
import sys


def build_project():
    print("Iniciando o processo de build do Display Library Generator...")

    # Verifica se o PyInstaller está instalado, se não, instala
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller não encontrado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Comando de build
    # --noconsole: Oculta a janela preta do terminal
    # --onefile: Gera um único arquivo .exe
    # --name: Nome do arquivo final
    # --windowed: Garante o comportamento correto da GUI no Windows
    command = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        "--windowed",
        "--name=Display_Library_Generator",
        "main.py"
    ]

    print("Executando PyInstaller...")
    subprocess.run(command, check=True)

    print("\n--- BUILD CONCLUÍDO COM SUCESSO ---")
    print("O seu executável está dentro da pasta 'dist/'.")


if __name__ == "__main__":
    build_project()