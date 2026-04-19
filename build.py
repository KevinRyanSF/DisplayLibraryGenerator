import os
import subprocess
import sys


def build_project():
    print("Iniciando o processo de build do Display Library Generator...")

    # Check if PyInstaller is installed; if not, install it
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller não encontrado. Instalando...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Build command configuration
    # --noconsole: Hides the black terminal window
    # --onefile: Generates a single .exe file
    # --name: Name of the final executable file
    # --windowed: Ensures correct GUI behavior on Windows
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