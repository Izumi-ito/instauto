import os
from playwright.sync_api import sync_playwright

BINARY = os.path.expanduser("~/.cloakbrowser/chromium-146.0.7680.177.5/chrome.exe")
PROFILE_DIR = os.path.join(os.path.dirname(__file__), "profiles")

START_URL = "https://www.google.com"
WIDTH = 1280
HEIGHT = 800

def start_session(profile_name="account_1"):
    profile_dir = os.path.join(PROFILE_DIR, profile_name)
    state_file = os.path.join(profile_dir, "state.json")
    os.makedirs(profile_dir, exist_ok=True)

    print(f"[{profile_name}] Launching browser...")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            executable_path=BINARY,
            headless=False,
            args=[
                f"--window-size={WIDTH},{HEIGHT}",
                "--no-first-run",
                "--no-default-browser-check",
            ],
        )

        if os.path.exists(state_file):
            print(f"[{profile_name}] Restoring session")
            ctx = browser.new_context(
                storage_state=state_file,
                viewport={"width": WIDTH, "height": HEIGHT},
                device_scale_factor=1,
            )
        else:
            print(f"[{profile_name}] Starting fresh session")
            ctx = browser.new_context(
                viewport={"width": WIDTH, "height": HEIGHT},
                device_scale_factor=1,
            )

        page = ctx.new_page()
        print(f"[{profile_name}] Opening {START_URL}...")
        page.goto(START_URL, timeout=30000)

        # Accept cookies if dialog present
        try:
            accept_btn = page.locator("button:has-text('Принять все'), button:has-text('Accept all')")
            if accept_btn.count() > 0:
                accept_btn.first.click(timeout=3000)
                page.wait_for_timeout(1000)
        except Exception:
            pass

        print(f"[{profile_name}] Ready! Press Enter to save and close...")

        input()

        ctx.storage_state(path=state_file)
        print(f"[{profile_name}] Session saved")

        ctx.close()
        browser.close()
        print(f"[{profile_name}] Done.")

if __name__ == "__main__":
    start_session()
