"""
Мультиаккаунт-ланчер.
Читает конфигурацию из accounts.json.
"""
import os
import json
from playwright.sync_api import sync_playwright
from geo import detect_all_accounts
from auth import login_instagram

BINARY = os.path.expanduser("~/.cloakbrowser/chromium-146.0.7680.177.5/chrome.exe")
PROFILE_DIR = os.path.join(os.path.dirname(__file__), "profiles")
CONFIG_FILE = os.path.join(os.path.dirname(__file__), "accounts.json")


def load_accounts():
    """Загрузка аккаунтов из JSON."""
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)["accounts"]


def start_session(account: dict, skip_login: bool = False, test_url: str = None):
    """Запуск сессии для одного аккаунта."""
    name = account["name"]
    profile_dir = os.path.join(PROFILE_DIR, name)
    state_file = os.path.join(profile_dir, "state.json")
    os.makedirs(profile_dir, exist_ok=True)

    proxy = account.get("proxy")
    timezone = account.get("timezone", "UTC")
    locale = account.get("locale", "en-US")
    viewport = account.get("viewport", {"width": 1280, "height": 800})
    ig = account.get("instagram", {})

    print(f"\n[{name}] Запуск...")
    print(f"  Proxy: {proxy['server'] if proxy else 'Нет'}")
    print(f"  Timezone: {timezone}")

    with sync_playwright() as p:
        args = [
            f"--window-size={viewport['width']},{viewport['height']}",
            f"--window-position=100,50",
            "--no-first-run",
            "--no-default-browser-check",
            f"--fingerprint-timezone={timezone}",
            f"--fingerprint-locale={locale}",
        ]

        pw_proxy = None
        if proxy and proxy.get("server"):
            pw_proxy = {"server": proxy["server"]}
            if proxy.get("username"):
                pw_proxy["username"] = proxy["username"]
                pw_proxy["password"] = proxy["password"]

        launch_kwargs = {
            "executable_path": BINARY,
            "headless": False,
            "args": args,
        }
        if pw_proxy:
            launch_kwargs["proxy"] = pw_proxy

        browser = p.chromium.launch(**launch_kwargs)

        if os.path.exists(state_file):
            print(f"  Восстановление сессии...")
            ctx = browser.new_context(
                storage_state=state_file,
                viewport=viewport,
                device_scale_factor=1,
                timezone_id=timezone,
                locale=locale,
            )
        else:
            print(f"  Новая сессия")
            ctx = browser.new_context(
                viewport=viewport,
                device_scale_factor=1,
                timezone_id=timezone,
                locale=locale,
            )

        page = ctx.new_page()

        if test_url:
            print(f"  Opening {test_url}...")
            page.goto(test_url, timeout=60000, wait_until="domcontentloaded")
            print(f"  Page loaded: {page.title()}")
        elif not skip_login and ig.get("login") and ig.get("password"):
            print(f"  Логин в Instagram как {ig['login']}...")
            success = login_instagram(page, ig)
            if success:
                print(f"  Login successful!")
            else:
                print(f"  Login failed")
        else:
            print(f"  Opening Instagram...")
            page.goto("https://www.instagram.com/", timeout=60000, wait_until="domcontentloaded")
            print(f"  Page loaded: {page.title()}")

        print(f"\n  Готово! Нажмите Enter чтобы сохранить и закрыть...")
        input()

        ctx.storage_state(path=state_file)
        print(f"  Сессия сохранена")
        ctx.close()
        browser.close()
        print(f"  Завершено.")


if __name__ == "__main__":
    import sys

    test_mode = "--test" in sys.argv

    accounts = load_accounts()

    # Автоопределение геолокации по прокси
    if not test_mode:
        accounts = detect_all_accounts(accounts)

    print("=== InstAuto ===\n")
    if test_mode:
        print("  [TEST MODE - no login]\n")

    print("Доступные аккаунты:")
    for i, acc in enumerate(accounts, 1):
        proxy = acc.get("proxy")
        tz = acc.get("timezone", "?")
        print(f"  {i}. {acc['name']} | {tz} | {proxy['server'] if proxy else 'без прокси'}")

    print(f"\n  all - все аккаунты")
    if test_mode:
        print(f"  test - открыть Instagram без логина")
    choice = input("\nВыберите номер или имя: ").strip()

    if choice == "all":
        for acc in accounts:
            start_session(acc, skip_login=test_mode)
    elif choice == "test":
        start_session(accounts[0], skip_login=True, test_url="https://www.instagram.com/")
    elif choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(accounts):
            start_session(accounts[idx], skip_login=test_mode)
        else:
            print("Неверный номер")
    else:
        found = [a for a in accounts if a["name"] == choice]
        if found:
            start_session(found[0], skip_login=test_mode)
        else:
            print(f"Аккаунт '{choice}' не найден")
