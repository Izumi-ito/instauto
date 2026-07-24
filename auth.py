"""
Модуль авторизации в Instagram.
Поддержка 2FA через 2fa.fb.tools, обработка диалогов.
"""
import re


def login_instagram(page, ig_config: dict) -> bool:
    """
    Логин в Instagram.

    Args:
        page: Playwright page
        ig_config: dict с ключами login, password, totp_secret (опционально)

    Returns:
        True если логин успешен, False если ошибка
    """
    context = page.context

    # Открываем страницу логина
    page.goto("https://www.instagram.com/accounts/login/", timeout=60000, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)

    # Принимаем cookie если появился диалог
    _accept_cookies(page)

    # Ждем загрузку формы
    username_input = page.locator('input[name="email"]')
    username_input.wait_for(state="visible", timeout=15000)

    # Вводим логин
    username_input.click()
    page.wait_for_timeout(300)
    username_input.fill(ig_config["login"])
    page.wait_for_timeout(500)

    # Вводим пароль
    pass_input = page.locator('input[name="pass"]')
    pass_input.click()
    page.wait_for_timeout(300)
    pass_input.fill(ig_config["password"])
    page.wait_for_timeout(1000)

    # Отправляем форму
    pass_input.press("Enter")

    # Ждем редирект
    if not _wait_for_redirect(page):
        return False

    # Обрабатываем 2FA если нужно
    if "two_step_verification" in page.url and ig_config.get("totp_secret"):
        if not _handle_2fa(page, context, ig_config["totp_secret"]):
            return False

    # Обрабатываем диалоги после логина
    _handle_post_login_dialogs(page)

    return True


def _accept_cookies(page):
    """Принимает cookie-диалог если появился."""
    try:
        cookie_btn = page.locator(
            'button:has-text("Allow"), button:has-text("Accept"), '
            'button:has-text("Allow All Cookies"), button:has-text("Принять")'
        )
        if cookie_btn.count() > 0:
            cookie_btn.first.click(timeout=3000)
            page.wait_for_timeout(1000)
    except Exception:
        pass


def _wait_for_redirect(page, timeout=15) -> bool:
    """Ждет смены URL после отправки формы."""
    for _ in range(timeout):
        page.wait_for_timeout(1000)
        url = page.url
        if "two_step_verification" in url:
            return True
        if "login" not in url:
            return True
    return False


def _handle_2fa(page, context, totp_secret: str) -> bool:
    """
    Обрабатывает 2FA через 2fa.fb.tools.

    Args:
        page: Playwright page (на странице 2FA)
        context: Browser context
        totp_secret: Секретный ключ TOTP

    Returns:
        True если 2FA пройдена, False если ошибка
    """
    # Ждем загрузку формы 2FA
    totp_input = page.locator('form input[type="text"]').first
    totp_input.wait_for(state="visible", timeout=10000)

    # Открываем 2fa.fb.tools во второй вкладке
    tab_2fa = context.new_page()
    tab_2fa.goto("https://2fa.fb.tools/", timeout=30000, wait_until="domcontentloaded")
    tab_2fa.wait_for_timeout(3000)

    # Вводим секрет
    secret_input = tab_2fa.locator('input[type="text"]').first
    secret_input.fill(totp_secret)
    tab_2fa.wait_for_timeout(1000)

    # Нажимаем кнопку генерации
    try:
        generate_btn = tab_2fa.locator(
            'button:has-text("Get Code"), button:has-text("Generate"), button[type="submit"]'
        )
        if generate_btn.count() > 0:
            generate_btn.first.click()
            tab_2fa.wait_for_timeout(3000)
    except Exception:
        pass

    # Извлекаем код
    code = _extract_2fa_code(tab_2fa)
    tab_2fa.close()

    if not code:
        code = input("  Enter 2FA code manually: ").strip()

    if not code:
        return False

    # Вводим код и отправляем
    totp_input.fill(code)
    page.wait_for_timeout(500)
    totp_input.press("Enter")
    page.wait_for_timeout(5000)

    return True


def _extract_2fa_code(tab_2fa) -> str:
    """Извлекает 6-значный код со страницы 2fa.fb.tools."""
    try:
        body_text = tab_2fa.locator('body').text_content()
        match = re.search(r'\b\d{6}\b', body_text)
        if match:
            return match.group(0)
    except Exception:
        pass
    return ""


def _handle_post_login_dialogs(page):
    """Обрабатывает диалоги после логина: сохранение данных, уведомления."""
    page.wait_for_timeout(2000)

    # "Сохранить данные для входа?"
    try:
        save_btn = page.locator('section button[type="button"]')
        if save_btn.count() > 0:
            save_btn.first.click(timeout=3000)
            page.wait_for_timeout(1000)
    except Exception:
        pass

    # "Включить уведомления?"
    try:
        notif_btn = page.locator('button._asz1')
        notif_btn.wait_for(state="visible", timeout=3000)
        notif_btn.click()
        page.wait_for_timeout(1000)
    except Exception:
        pass
