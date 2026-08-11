#!/usr/bin/env python3
"""
Сборка DaRT для текущей платформы
Запустите: python build.py

На Windows: соберет DaRT.exe
На Linux:   соберет DaRT
"""

import os
import sys
import shutil
import platform
import subprocess
import json
from datetime import datetime


def clean_build():
    """Очистка старых сборок"""
    folders = ['build', '__pycache__', 'dist']
    for folder in folders:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            print(f"[OK] Removed: {folder}")

    for file in ['DaRT.spec']:
        if os.path.exists(file):
            os.remove(file)
            print(f"[OK] Removed: {file}")


def check_pyinstaller():
    """Проверка установки PyInstaller"""
    try:
        import PyInstaller
        return True
    except ImportError:
        print("[ERROR] PyInstaller not installed!")
        print("Install it with: pip install pyinstaller")
        return False


def build_current_platform():
    """Сборка для текущей платформы"""
    current_os = platform.system()

    print("\n" + "=" * 50)
    print(f"  Building for {current_os}")
    print("=" * 50)

    if not check_pyinstaller():
        return False

    # Формируем команду в зависимости от ОС
    if current_os == "Windows":
        cmd = [
            "pyinstaller",
            "--onefile",
            "--name", "DaRT",
            "--console",
            "--add-data", "settings.json;.",
            "--hidden-import", "berconpy",
            "--hidden-import", "berconpy.ext.arma",
            "--hidden-import", "berconpy.io",
            "--hidden-import", "berconpy.errors",
            "--hidden-import", "asyncio",
            "--collect-all", "berconpy",
            "main.py"
        ]
        output_file = "dist/DaRT.exe"
    else:  # Linux и другие Unix-подобные
        cmd = [
            "pyinstaller",
            "--onefile",
            "--name", "DaRT",
            "--console",
            "--add-data", "settings.json:.",
            "--hidden-import", "berconpy",
            "--hidden-import", "berconpy.ext.arma",
            "--hidden-import", "berconpy.io",
            "--hidden-import", "berconpy.errors",
            "--hidden-import", "asyncio",
            "--collect-all", "berconpy",
            "main.py"
        ]
        output_file = "dist/DaRT"

    try:
        print(f"[INFO] Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)

        if os.path.exists(output_file):
            print(f"[OK] Build complete: {output_file}")
            return True
        else:
            print(f"[ERROR] Build failed - {output_file} not found")
            return False
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Build failed: {e}")
        return False


def create_release_package():
    """Создание пакета для распространения"""
    current_os = platform.system()

    print("\n" + "=" * 50)
    print("  Creating release package")
    print("=" * 50)

    # Определяем имя папки для платформы
    platform_folder = "Windows" if current_os == "Windows" else "Linux"
    binary_name = "DaRT.exe" if current_os == "Windows" else "DaRT"

    # Создаем папку релиза
    release_dir = "release"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)

    os.makedirs(release_dir)
    os.makedirs(os.path.join(release_dir, platform_folder))

    # Копируем исполняемый файл
    source = f"dist/{binary_name}"
    dest = os.path.join(release_dir, platform_folder, binary_name)

    if os.path.exists(source):
        shutil.copy(source, dest)
        if current_os != "Windows":
            os.chmod(dest, 0o755)
        print(f"[OK] Copied {binary_name}")
    else:
        print(f"[ERROR] Binary not found: {source}")
        return False

    # Копируем файл настроек
    if os.path.exists("settings.json"):
        shutil.copy("settings.json", os.path.join(release_dir, "settings.json"))
        print("[OK] Copied settings.json")
    else:
        # Создаем settings.json по умолчанию
        default_settings = {
            "host": "127.0.0.1",
            "port": 2322,
            "password": "your_rcon_password_here",
            "admin_name": "Admin",
            "language": "ru"
        }
        with open(os.path.join(release_dir, "settings.json"), "w", encoding="utf-8") as f:
            json.dump(default_settings, f, indent=4)
        print("[OK] Created default settings.json")

    # Создаем README
    create_readme(release_dir, platform_folder)

    # Создаем скрипты запуска
    create_launcher_scripts(release_dir, platform_folder, binary_name)

    # Создаем архив с указанием платформы
    archive_name = f"DaRT_{current_os}_{datetime.now().strftime('%Y%m%d')}"
    shutil.make_archive(archive_name, "zip", release_dir)
    print(f"[OK] Created archive: {archive_name}.zip")

    print("\n" + "=" * 50)
    print(f"  Release package for {current_os} created successfully!")
    print(f"  File: {archive_name}.zip")
    print("=" * 50)
    return True


def create_readme(release_dir: str, platform_folder: str):
    """Создание README файла"""
    binary_name = "DaRT.exe" if platform_folder == "Windows" else "DaRT"
    run_script = "run.bat" if platform_folder == "Windows" else "run.sh"

    readme_content = f"""================================================================================
DaRT - DayZ Remote Tool v1.0 ({platform_folder})
================================================================================

ОПИСАНИЕ:
---------
DaRT - это инструмент для удаленного управления сервером DayZ через RCon.

УСТАНОВКА:
----------
1. Распакуйте архив в любую папку
2. Отредактируйте файл settings.json (укажите данные вашего сервера)
3. Запустите программу:
   - {platform_folder}: Запустите {run_script} или {platform_folder}/{binary_name}

НАСТРОЙКА:
----------
Откройте файл settings.json в текстовом редакторе и укажите:

{{
    "host": "IP_АДРЕС_СЕРВЕРА",        // IP вашего сервера
    "port": 2322,                       // Порт RCon (обычно 2322)
    "password": "ВАШ_ПАРОЛЬ_RCON",     // Пароль RCon из server.cfg
    "admin_name": "Admin",              // Имя администратора
    "language": "ru"                    // Язык: en - английский, ru - русский
}}

ЗАПУСК:
-------
После настройки запустите программу и введите:
  1 - Подключиться к серверу
  2 - Показать игроков
  3 - Отправить сообщение
  4 - Кикнуть игрока (по ID)
  5 - Забанить игрока (ID/GUID)
  6 - Показать баны
  7 - Снять бан
  8 - Выполнить команду
  9 - Отключиться
  s - Настройки
  0 - Выход

ПРИМЕЧАНИЯ:
-----------
- При бане по GUID игрок автоматически кикается с сервера
- Для кика/бана используйте ID из списка игроков
- GUID можно скопировать из списка игроков (32 символа)

СИСТЕМНЫЕ ТРЕБОВАНИЯ:
-------------------
- {platform_folder}: {platform_folder} 7 и выше

================================================================================
"""

    with open(os.path.join(release_dir, "README.txt"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    print("[OK] Created README.txt")


def create_launcher_scripts(release_dir: str, platform_folder: str, binary_name: str):
    """Создание скриптов запуска"""

    if platform_folder == "Windows":
        # Windows .bat
        bat_content = f"""@echo off
chcp 65001 > nul
title DaRT - DayZ Remote Tool
echo ============================================================
echo   DaRT - DayZ Remote Tool v1.0
echo   Windows Launcher
echo ============================================================
echo.
echo Press any key to start DaRT...
pause > nul
echo.

{binary_name}

pause
"""
        with open(os.path.join(release_dir, "run.bat"), "w", encoding="utf-8") as f:
            f.write(bat_content)
        print("[OK] Created run.bat")
    else:
        # Linux .sh
        sh_content = f"""#!/bin/bash
# DaRT - DayZ Remote Tool v1.0
# Linux Launcher

echo "============================================================"
echo "  DaRT - DayZ Remote Tool v1.0"
echo "  Linux Launcher"
echo "============================================================"
echo ""

if [ ! -f "{binary_name}" ]; then
    echo "[ERROR] DaRT binary not found!"
    echo "Make sure {binary_name} is in the same folder"
    echo ""
    echo "Press Enter to exit..."
    read
    exit 1
fi

# Проверяем права на выполнение
if [ ! -x "{binary_name}" ]; then
    echo "[INFO] Making DaRT executable..."
    chmod +x {binary_name}
fi

echo "Starting DaRT..."
echo ""
./{binary_name}

echo ""
echo "Press Enter to exit..."
read
"""
        with open(os.path.join(release_dir, "run.sh"), "w", encoding="utf-8") as f:
            f.write(sh_content)
        os.chmod(os.path.join(release_dir, "run.sh"), 0o755)
        print("[OK] Created run.sh")


def main():
    """Главная функция сборки"""
    print("=" * 60)
    print("  DaRT - Build Tool v1.0")
    print("=" * 60)

    current_os = platform.system()
    print(f"[INFO] Current OS: {current_os}")
    print(f"[INFO] Python: {sys.version}")
    print(f"[INFO] Platform: {platform.platform()}")

    # Очищаем старые сборки
    clean_build()

    # Собираем для текущей платформы
    if not build_current_platform():
        print("\n[ERROR] Build failed!")
        sys.exit(1)

    # Создаем пакет для распространения
    if not create_release_package():
        print("\n[ERROR] Failed to create release package!")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("  Build complete!")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[INFO] Build cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Build failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)