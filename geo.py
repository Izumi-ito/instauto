"""
Утилита для определения геолокации по IP прокси.
Использует бесплатные GeoIP API.
"""
import json
import httpx

# Маппинг стран на локали
COUNTRY_LOCALE = {
    "RU": "ru-RU",
    "US": "en-US",
    "GB": "en-GB",
    "DE": "de-DE",
    "FR": "fr-FR",
    "ES": "es-ES",
    "IT": "it-IT",
    "PT": "pt-PT",
    "BR": "pt-BR",
    "JP": "ja-JP",
    "KR": "ko-KR",
    "CN": "zh-CN",
    "TR": "tr-TR",
    "UA": "uk-UA",
    "PL": "pl-PL",
    "NL": "nl-NL",
    "SE": "sv-SE",
    "NO": "nb-NO",
    "FI": "fi-FI",
    "DK": "da-DK",
    "CZ": "cs-CZ",
    "RO": "ro-RO",
    "HU": "hu-HU",
    "GR": "el-GR",
    "IL": "he-IL",
    "SA": "ar-SA",
    "AE": "ar-AE",
    "EG": "ar-EG",
    "TH": "th-TH",
    "VN": "vi-VN",
    "ID": "id-ID",
    "MY": "ms-MY",
    "PH": "en-PH",
    "IN": "en-IN",
    "AU": "en-AU",
    "NZ": "en-NZ",
    "CA": "en-CA",
    "MX": "es-MX",
    "AR": "es-AR",
    "CL": "es-CL",
    "CO": "es-CO",
    "PE": "es-PE",
}


def detect_geo(proxy_server: str, proxy_user: str = None, proxy_pass: str = None) -> dict:
    """
    Определяет геолокацию по IP прокси.

    Args:
        proxy_server: Адрес прокси (http://host:port или socks5://host:port)
        proxy_user: Логин прокси (опционально)
        proxy_pass: Пароль прокси (опционально)

    Returns:
        dict с полями: timezone, locale, country, city, ip
    """
    # Формируем URL прокси для httpx
    proxy_url = proxy_server
    if proxy_user and proxy_pass:
        # Вставляем авторизацию в URL
        proto, rest = proxy_server.split("://", 1)
        proxy_url = f"{proto}://{proxy_user}:{proxy_pass}@{rest}"

    try:
        # Используем ip-api.com (бесплатно, 45 запросов/мин)
        with httpx.Client(proxy=proxy_url, timeout=10) as client:
            resp = client.get("http://ip-api.com/json/?fields=status,country,countryCode,regionName,city,timezone,isp,query")
            data = resp.json()

            if data.get("status") != "success":
                return _default_geo()

            country_code = data.get("countryCode", "")
            timezone = data.get("timezone", "UTC")
            locale = COUNTRY_LOCALE.get(country_code, "en-US")

            return {
                "timezone": timezone,
                "locale": locale,
                "country": data.get("country", ""),
                "country_code": country_code,
                "city": data.get("city", ""),
                "isp": data.get("isp", ""),
                "ip": data.get("query", ""),
            }

    except Exception as e:
        print(f"  GeoIP detection failed: {e}")
        return _default_geo()


def _default_geo() -> dict:
    """Значения по умолчанию при ошибке."""
    return {
        "timezone": "UTC",
        "locale": "en-US",
        "country": "",
        "country_code": "",
        "city": "",
        "isp": "",
        "ip": "",
    }


def auto_fill_account(account: dict) -> dict:
    """
    Автоматически заполняет timezone и locale на основе прокси.

    Если прокси указан — определяет геолокацию.
    Если прокси нет — оставляет как есть.

    Args:
        account: Словарь с данными аккаунта

    Returns:
        Обновленный словарь аккаунта
    """
    proxy = account.get("proxy")
    if not proxy or not proxy.get("server"):
        print(f"  [{account['name']}] No proxy, skipping geo detection")
        return account

    print(f"  [{account['name']}] Detecting geo for {proxy['server']}...")
    geo = detect_geo(
        proxy["server"],
        proxy.get("username"),
        proxy.get("password"),
    )

    # Обновляем только если не задано вручную
    if not account.get("timezone") or account["timezone"] == "UTC":
        account["timezone"] = geo["timezone"]
    if not account.get("locale") or account["locale"] == "en-US":
        account["locale"] = geo["locale"]

    print(f"  [{account['name']}] Detected: {geo['country']}, {geo['city']}, {geo['timezone']}, {geo['locale']}")
    print(f"  [{account['name']}] IP: {geo['ip']}, ISP: {geo['isp']}")

    return account


def detect_all_accounts(accounts: list) -> list:
    """Определяет геолокацию для всех аккаунтов с прокси."""
    print("\n=== GeoIP Detection ===\n")
    for account in accounts:
        auto_fill_account(account)
    print()
    return accounts


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # Тест: python geo.py http://user:pass@proxy:8080
        proxy = sys.argv[1]
        result = detect_geo(proxy)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Usage: python geo.py <proxy_url>")
        print("Example: python geo.py http://user:pass@proxy:8080")
