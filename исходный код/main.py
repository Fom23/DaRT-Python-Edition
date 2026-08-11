import asyncio
import json
import os
import sys
from typing import List, Dict, Any, Optional

# noinspection PyUnresolvedReferences
from berconpy import ArmaClient
# noinspection PyUnresolvedReferences
from berconpy.errors import RCONCommandError


def load_settings() -> Dict[str, Any]:
    if not os.path.exists("settings.json"):
        default_settings = {
            "host": "127.0.0.1",
            "port": 2302,
            "password": "change_me",
            "admin_name": "Admin",
            "language": "en"
        }
        with open("settings.json", "w", encoding="utf-8") as f:
            json.dump(default_settings, f, indent=4)
        print("[INFO] Created settings.json. Fill it with your data!")
        return default_settings
    try:
        with open("settings.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        print("[ERROR] settings.json is corrupted!")
        return load_settings()


# ============================================================
# ЯЗЫКОВЫЕ ФАЙЛЫ
# ============================================================
LANG = {
    "en": {
        "title": "DaRT Python Edition v1.0",
        "status": "Status",
        "connected": "[OK] Connected",
        "not_connected": "[X] Not connected",
        "server": "Server",
        "menu": {
            "1": "1 - Connect to server",
            "2": "2 - Show players",
            "3": "3 - Send message",
            "4": "4 - Kick player (by ID)",
            "5": "5 - Ban player (ID/GUID)",
            "6": "6 - Show bans",
            "7": "7 - Remove ban",
            "8": "8 - Execute command",
            "9": "9 - Disconnect",
            "s": "  s - Settings",
            "0": "  0 - Exit"
        },
        "settings": {
            "title": "SETTINGS",
            "host": "1. Host",
            "port": "2. Port",
            "password": "3. Password",
            "admin_name": "4. Admin name",
            "language": "5. Language",
            "back": "0. Back"
        },
        "messages": {
            "connecting": "[INFO] Connecting to {host}:{port}...",
            "connected": "[OK] Connected to {host}:{port}",
            "not_connected": "[ERROR] Not connected to server",
            "disconnected": "[OK] Disconnected from server",
            "no_players": "[INFO] No players on server",
            "players_count": "[PLAYERS] {count} player(s) on server:",
            "kick_ban_info": "[INFO] For kick/ban:",
            "kick_ban_id": "   - By ID: enter number (e.g. 0)",
            "kick_ban_guid": "   - By GUID: enter 32 chars",
            "kick_warning": "[WARNING] Kick works only by numeric ID (e.g. 0, 1, 2...)",
            "ban_by_id": "[INFO] Ban by ID: {pid}",
            "ban_by_guid": "[INFO] Ban by GUID: {guid}",
            "player_not_found": "[WARNING] Player not online or not found",
            "invalid_format": "[WARNING] Invalid format!",
            "enter_message": "Enter message: ",
            "enter_player_id": "Enter player ID: ",
            "enter_reason": "Reason (Enter = default): ",
            "enter_id_guid": "Enter ID or GUID: ",
            "enter_duration": "Duration in minutes (0 = permanent): ",
            "enter_command": "Enter command: ",
            "select_action": "Select action: ",
            "press_enter": "Press Enter to continue...",
            "goodbye": "Goodbye!"
        }
    },
    "ru": {
        "title": "DaRT Python Edition v1.0",
        "status": "Status",
        "connected": "[OK] Подключено",
        "not_connected": "[X] Не подключено",
        "server": "Сервер",
        "menu": {
            "1": "1 - Подключиться к серверу",
            "2": "2 - Показать игроков",
            "3": "3 - Отправить сообщение",
            "4": "4 - Кикнуть игрока (по ID)",
            "5": "5 - Забанить игрока (ID/GUID)",
            "6": "6 - Показать баны",
            "7": "7 - Снять бан",
            "8": "8 - Выполнить команду",
            "9": "9 - Отключиться",
            "s": "  s - Настройки",
            "0": "  0 - Выход"
        },
        "settings": {
            "title": "НАСТРОЙКИ",
            "host": "1. Хост",
            "port": "2. Порт",
            "password": "3. Пароль",
            "admin_name": "4. Имя администратора",
            "language": "5. Язык",
            "back": "0. Назад"
        },
        "messages": {
            "connecting": "[INFO] Подключение к {host}:{port}...",
            "connected": "[OK] Подключено к {host}:{port}",
            "not_connected": "[ERROR] Не подключено к серверу",
            "disconnected": "[OK] Отключено от сервера",
            "no_players": "[INFO] Нет игроков на сервере",
            "players_count": "[ИГРОКИ] {count} игрок(ов) на сервере:",
            "kick_ban_info": "[INFO] Для кика/бана:",
            "kick_ban_id": "   - По ID: введите число (например, 0)",
            "kick_ban_guid": "   - По GUID: введите 32 символа",
            "kick_warning": "[WARNING] Кик работает только по числовому ID (например, 0, 1, 2...)",
            "ban_by_id": "[INFO] Бан по ID: {pid}",
            "ban_by_guid": "[INFO] Бан по GUID: {guid}",
            "player_not_found": "[WARNING] Игрок не в сети или не найден",
            "invalid_format": "[WARNING] Неверный формат!",
            "enter_message": "Введите сообщение: ",
            "enter_player_id": "Введите ID игрока: ",
            "enter_reason": "Причина (Enter = по умолчанию): ",
            "enter_id_guid": "Введите ID или GUID: ",
            "enter_duration": "Длительность в минутах (0 = навсегда): ",
            "enter_command": "Введите команду: ",
            "select_action": "Выберите действие: ",
            "press_enter": "Нажмите Enter для продолжения...",
            "goodbye": "До свидания!"
        }
    }
}


def get_text(key: str, lang: str = "en", **kwargs) -> str:
    keys = key.split('.')
    text = LANG.get(lang, LANG["en"])
    for k in keys:
        if isinstance(text, dict):
            text = text.get(k, key)
        else:
            return key
    if isinstance(text, str):
        return text.format(**kwargs) if kwargs else text
    return key


class SimpleRCon:
    def __init__(self, lang: str = "en"):
        self.client: Optional[ArmaClient] = None
        self.connected: bool = False
        self.host: str = ""
        self.port: int = 0
        self.password: str = ""
        self.admin_name: str = "Admin"
        self._context: Optional[Any] = None
        self.lang: str = lang

    def t(self, key: str, **kwargs) -> str:
        return get_text(key, self.lang, **kwargs)

    async def connect(self, host: str, port: int, password: str) -> bool:
        try:
            print(self.t("messages.connecting", host=host, port=port))
            self.host = host
            self.port = port
            self.password = password

            self.client = ArmaClient()
            if self.client is None:
                raise RuntimeError("Failed to create client")

            self._context = self.client.connect(host, port, password)
            if self._context is not None:
                if hasattr(self._context, '__aenter__'):
                    self.client = await self._context.__aenter__()
                else:
                    raise RuntimeError("Context does not support async with")
            else:
                raise RuntimeError("Failed to create connection context")

            await asyncio.sleep(0.5)
            self.connected = True
            print(self.t("messages.connected", host=host, port=port))
            return True
        except ConnectionRefusedError as conn_err:
            print(f"[ERROR] Connection refused. Server is not running or port {port} is closed. ({conn_err})")
            return False
        except OSError as os_err:
            print(f"[ERROR] Network error: {os_err}")
            return False
        except Exception as general_err:
            print(f"[ERROR] Connection error: {general_err}")
            return False

    async def _reconnect(self) -> bool:
        print("[INFO] Reconnecting...")
        if self.connected:
            await self.disconnect()
        await asyncio.sleep(1)
        return await self.connect(self.host, self.port, self.password)

    async def _send_command(self, command: str, silent: bool = False, retry: int = 2) -> Optional[str]:
        if not self.connected or self.client is None:
            if not silent:
                print(self.t("messages.not_connected"))
            return None

        try:
            if not silent:
                print(f"[SEND] {command}")
            response = await self.client.send_command(command)
            if response and not silent:
                print(f"[RESPONSE]\n{response}")
            elif not silent:
                print("[RESPONSE] (empty)")
            return response
        except asyncio.CancelledError:
            if retry > 0:
                if not silent:
                    print("[WARNING] Command cancelled, reconnecting...")
                if await self._reconnect():
                    return await self._send_command(command, silent, retry - 1)
            return None
        except RCONCommandError as rcon_err:
            if not silent:
                print(f"[ERROR] Send error: {rcon_err}")
                print("[INFO] Attempting to reconnect...")
            if await self._reconnect():
                if not silent:
                    print("[OK] Reconnected, retrying...")
                return await self._send_command(command, silent, retry - 1)
            return None
        except Exception as general_err:
            if not silent:
                print(f"[ERROR] {general_err}")
            return None

    async def get_players(self) -> List[Dict[str, Any]]:
        response = await self._send_command("players")
        if response is None:
            return []

        players = self._parse_players(response)
        if players:
            print(self.t("messages.players_count", count=len(players)))
            print("-" * 85)
            print(f"{'ID':<4} {'Name':<25} {'GUID':<36} {'Ping':<6} {'IP':<15}")
            print("-" * 85)
            for player in players:
                print(
                    f"{player['id']:<4} {player['name']:<25} {player['guid']:<36} {player['ping']:<6}ms {player['ip']:<15}")
            print("-" * 85)
            print(self.t("messages.kick_ban_info"))
            print(self.t("messages.kick_ban_id"))
            print(self.t("messages.kick_ban_guid"))
        else:
            print(self.t("messages.no_players"))
        return players

    @staticmethod
    def _parse_players(response: str) -> List[Dict[str, Any]]:
        lines = response.split('\n')
        players: List[Dict[str, Any]] = []

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if (line.startswith('Players on server:') or
                    line.startswith('[#]') or
                    line.startswith('---')):
                continue
            parts = line.split()
            if len(parts) >= 5:
                name = ' '.join(parts[4:])
                guid = parts[3].replace('(?)', '').replace('(OK)', '')
                ip = parts[1].split(':')[0] if ':' in parts[1] else parts[1]
                players.append({
                    'id': parts[0],
                    'ip': ip,
                    'port': parts[1].split(':')[1] if ':' in parts[1] else '',
                    'ping': parts[2],
                    'guid': guid,
                    'name': name
                })
        return players

    async def kick_player(self, player_id: str, reason: str = "Kicked by admin") -> None:
        if not player_id.isdigit():
            print(self.t("messages.kick_warning"))
            return
        await self._send_command(f"kick {player_id} {reason}")

    async def _find_player_by_guid(self, guid: str) -> Optional[Dict[str, Any]]:
        """Поиск игрока по GUID"""
        players = await self.get_players()
        for player in players:
            if player['guid'].lower() == guid.lower():
                return player
        return None

    async def ban_player(self, player_id: str, duration: str = "0", reason: str = "Banned by admin") -> None:
        try:
            duration_int = int(duration)
            if duration_int < 0:
                print("[WARNING] Duration cannot be negative")
                return
        except ValueError:
            print("[WARNING] Duration must be an integer (minutes)")
            return

        is_guid = len(player_id) == 32 and all(c in '0123456789abcdefABCDEF' for c in player_id)

        if is_guid:
            print(self.t("messages.ban_by_guid", guid=player_id[:8]))

            # Ищем игрока ДО бана
            target_player = await self._find_player_by_guid(player_id)

            if target_player:
                print(f"[INFO] Found player: {target_player['name']} (ID: {target_player['id']})")
                confirm = input(f"Ban and kick {target_player['name']}? (y/n): ").strip().lower()
                if confirm != 'y':
                    print("[INFO] Operation cancelled")
                    return

            # Баним по GUID
            await self._send_command(f"addBan {player_id} {duration_int} {reason}")

            # Если игрок найден - кикаем его
            if target_player:
                print(f"[INFO] Kicking player {target_player['name']}...")
                await self._send_command(f"kick {target_player['id']} {reason}")
            else:
                print("[INFO] Player with this GUID not found on server (already offline)")

        elif player_id.isdigit():
            print(self.t("messages.ban_by_id", pid=player_id))
            # При бане по ID - бан и кик одной командой
            await self._send_command(f"ban {player_id} {duration_int} {reason}")
        else:
            print(self.t("messages.invalid_format"))

    async def unban_player(self, ban_id: str) -> None:
        await self._send_command(f"removeBan {ban_id}")

    async def send_message(self, message: str) -> None:
        await self._send_command(f"say -1 {message}")

    async def execute_command(self, command: str) -> None:
        await self._send_command(command)

    async def get_bans(self) -> None:
        response = await self._send_command("bans")
        if response:
            print("\n[BANS] Ban list:")
            print("-" * 60)
            print(response)
            print("-" * 60)

    async def disconnect(self) -> None:
        if self._context is not None:
            try:
                await self._context.__aexit__(None, None, None)
            except (AttributeError, RuntimeError, asyncio.CancelledError):
                # Игнорируем ошибки при закрытии соединения
                pass
        self.connected = False
        print(self.t("messages.disconnected"))


def clear_screen() -> None:
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str) -> None:
    print("=" * 50)
    print(f"{title:^50}")
    print("=" * 50)


def print_menu(client: SimpleRCon) -> None:
    print("\n" + "=" * 50)
    print(f"  {client.t('title')}")
    print("=" * 50)
    print(client.t("menu.1"))
    print(client.t("menu.2"))
    print(client.t("menu.3"))
    print(client.t("menu.4"))
    print(client.t("menu.5"))
    print(client.t("menu.6"))
    print(client.t("menu.7"))
    print(client.t("menu.8"))
    print(client.t("menu.9"))
    print(client.t("menu.s"))
    print(client.t("menu.0"))
    print("=" * 50)


def settings_menu(settings: Dict[str, Any], client: SimpleRCon) -> Dict[str, Any]:
    clear_screen()
    print_header(client.t("settings.title"))
    print(client.t("settings.host") + f": {settings['host']}")
    print(client.t("settings.port") + f": {settings['port']}")
    print(client.t("settings.password") + f": {'*' * len(settings['password'])}")
    print(client.t("settings.admin_name") + f": {settings.get('admin_name', 'Admin')}")
    lang_display = "English" if settings.get('language', 'en') == 'en' else "Русский"
    print(client.t("settings.language") + f": {lang_display}")
    print(client.t("settings.back"))
    print("=" * 50)

    choice = input(client.t("messages.select_action")).strip()

    if choice == "1":
        new_host = input("Enter server IP: ").strip()
        if new_host:
            settings['host'] = new_host
    elif choice == "2":
        port_input = input("Enter port: ").strip()
        if port_input:
            try:
                settings['port'] = int(port_input)
            except ValueError:
                print("[ERROR] Invalid port!")
    elif choice == "3":
        new_password = input("Enter password: ").strip()
        if new_password:
            settings['password'] = new_password
    elif choice == "4":
        new_name = input("Enter admin name: ").strip()
        if new_name:
            settings['admin_name'] = new_name
    elif choice == "5":
        lang = input("Enter language (en/ru): ").strip().lower()
        if lang in ['en', 'ru']:
            settings['language'] = lang
            client.lang = lang
            print("[OK] Language changed. Restart to apply.")
        else:
            print("[WARNING] Invalid language. Use 'en' or 'ru'")

    with open("settings.json", "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

    return settings


async def main() -> None:
    settings = load_settings()
    lang = settings.get('language', 'en')
    client = SimpleRCon(lang)
    client.admin_name = str(settings.get("admin_name", "Admin"))

    while True:
        clear_screen()
        print_header(client.t("title"))

        status = client.t("connected") if client.connected else client.t("not_connected")
        print(f"{client.t('status')}: {status}")
        if client.connected:
            print(f"{client.t('server')}: {client.host}:{client.port}")
        print()

        print_menu(client)
        choice = input(client.t("messages.select_action")).strip().lower()

        if choice == "0":
            if client.connected:
                await client.disconnect()
            print(client.t("messages.goodbye"))
            break

        if choice == "1":
            if client.connected:
                print("[WARNING] Already connected!")
                input(client.t("messages.press_enter"))
                continue
            host = str(settings["host"])
            port = int(settings["port"])
            password = str(settings["password"])
            if await client.connect(host, port, password):
                input(client.t("messages.press_enter"))

        elif choice == "2":
            if not client.connected:
                print(client.t("messages.not_connected"))
                input(client.t("messages.press_enter"))
                continue
            await client.get_players()
            input("\n" + client.t("messages.press_enter"))

        elif choice == "3":
            if not client.connected:
                print(client.t("messages.not_connected"))
                input(client.t("messages.press_enter"))
                continue
            message = input(client.t("messages.enter_message")).strip()
            if message:
                await client.send_message(message)
            input(client.t("messages.press_enter"))

        elif choice == "4":
            if not client.connected:
                print(client.t("messages.not_connected"))
                input(client.t("messages.press_enter"))
                continue
            player_id = input(client.t("messages.enter_player_id")).strip()
            if player_id:
                reason = input(client.t("messages.enter_reason")).strip()
                await client.kick_player(player_id, reason or "Kicked by admin")
            input(client.t("messages.press_enter"))

        elif choice == "5":
            if not client.connected:
                print(client.t("messages.not_connected"))
                input(client.t("messages.press_enter"))
                continue
            player_id = input(client.t("messages.enter_id_guid")).strip()
            if player_id:
                duration = input(client.t("messages.enter_duration")).strip() or "0"
                reason = input(client.t("messages.enter_reason")).strip()
                await client.ban_player(player_id, duration, reason or "Banned by admin")
            input(client.t("messages.press_enter"))

        elif choice == "6":
            if not client.connected:
                print(client.t("messages.not_connected"))
                input(client.t("messages.press_enter"))
                continue
            await client.get_bans()
            input(client.t("messages.press_enter"))

        elif choice == "7":
            if not client.connected:
                print(client.t("messages.not_connected"))
                input(client.t("messages.press_enter"))
                continue
            ban_id = input("Enter ban ID from list: ").strip()
            if ban_id:
                await client.unban_player(ban_id)
            input(client.t("messages.press_enter"))

        elif choice == "8":
            if not client.connected:
                print(client.t("messages.not_connected"))
                input(client.t("messages.press_enter"))
                continue
            command = input(client.t("messages.enter_command")).strip()
            if command:
                await client.execute_command(command)
            input(client.t("messages.press_enter"))

        elif choice == "9":
            if client.connected:
                await client.disconnect()
            else:
                print(client.t("messages.not_connected"))
            input(client.t("messages.press_enter"))

        elif choice == "s":
            settings = settings_menu(settings, client)

        else:
            print("[ERROR] Invalid choice!")
            input(client.t("messages.press_enter"))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as main_err:
        print(f"\n[ERROR] {main_err}")
        import traceback

        traceback.print_exc()
    finally:
        if getattr(sys, 'frozen', False):
            input("\nPress Enter to exit...")
            sys.exit(0)