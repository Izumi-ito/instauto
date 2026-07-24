# InstAuto — Автоматизация мультиаккаунта Instagram

Управление несколькими аккаунтами Instagram с уникальными отпечатками браузера, прокси, таймзонами и 2FA.

## Возможности

| Функция | Бесплатно | Pro |
|---|---|---|
| Уникальные отпечатки (C++ патчи) | ✅ Chromium 146 | ✅ Chromium 150 |
| Persistent profiles (куки, localStorage) | ✅ | ✅ |
| Прокси на профиль (HTTP/SOCKS5) | ✅ | ✅ |
| Таймзона и язык на профиль | ✅ | ✅ |
| Автоматический логин с 2FA | ✅ | ✅ |
| `humanize=True` (имитация человека) | ❌ | ✅ |
| `geoip=True` (таймзона по IP) | ❌ | ✅ |

## Установка

### 1. Установите uv

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Установите зависимости

```bash
cd C:\Users\Izumi\Desktop\instauto
uv sync
```

### 3. Скачайте CloakBrowser

```bash
uv run python -m cloakbrowser install
```

## Конфигурация аккаунтов

Откройте файл `accounts.json` и заполните данные:

```json
{
    "accounts": [
        {
            "name": "account_1",
            "proxy": {
                "server": "http://proxy1.example.com:8080",
                "username": "user1",
                "password": "pass1"
            },
            "instagram": {
                "login": "my_login_1",
                "password": "my_password_1",
                "totp_secret": ""
            }
        }
    ]
}
```

**Таймзона и язык определяются автоматически** по IP прокси. Если нужно задать вручную:

```json
{
    "timezone": "Europe/Moscow",
    "locale": "ru-RU"
}
```

### Параметры

| Параметр | Обязательно | Описание |
|---|---|---|
| `name` | ✅ | Уникальное имя профиля |
| `proxy.server` | ❌ | Адрес прокси (`http://` или `socks5://`) |
| `proxy.username` | ❌ | Логин прокси |
| `proxy.password` | ❌ | Пароль прокси |
| `timezone` | ❌ | Часовой пояс (авто, если не задан) |
| `locale` | ❌ | Язык (авто, если не задан) |
| `instagram.login` | ✅ | Логин от Instagram |
| `instagram.password` | ✅ | Пароль от Instagram |
| `instagram.totp_secret` | ❌ | Секрет для 2FA |

### Как добавить новый аккаунт

1. Откройте `accounts.json`
2. Скопируйте блок аккаунта
3. Измените `name`, прокси, логин, пароль
4. Сохраните файл

## Запуск

### Один аккаунт

```bash
uv run python run.py
```

### Мультиаккаунт

```bash
uv run python run_multi.py
```

Программа покажет список профилей и предложит выбрать:
- Введите имя профиля (например `account_1`) для запуска одного
- Введите `all` для запуска всех

## Структура проекта

```
instauto/
├── accounts.json               # Конфигурация аккаунтов (РЕДАКТИРУЙТЕ ЭТОТ ФАЙЛ)
├── run.py                      # Запуск одного профиля (базовый)
├── run_multi.py                # Мультиаккаунт-ланчер
├── profiles/                   # Данные сессий (автоматически)
│   ├── account_1/
│   │   └── state.json
│   └── account_2/
│       └── state.json
├── pyproject.toml
└── README.md
```

## Работа с 2FA

1. Включите двухфакторную аутентификацию в Instagram
2. При настройке выберите "Authentication App"
3. Скопируйте секретный ключ (строка `JBSWY3DPEHPK3PXP` и т.д.)
4. Вставьте его в `profiles_config_example.py` в поле `totp_secret`

При логине скрипт автоматически сгенерирует код и введет его.

## Управление сессиями

- **Сессии сохраняются** в `profiles/<name>/state.json`
- **Повторный запуск** восстанавливает куки и localStorage
- **Новый профиль** = новый браузер с чистой историей
- **Удаление профиля** = удаление папки в `profiles/`

## Советы

1. **Разные прокси** — каждый аккаунт должен использовать свой прокси
2. **Совпадение таймзоны** — таймзона должна совпадать с IP прокси
3. **Не спешите** — добавляйте задержки между действиями
4. **Используйте Pro** для `humanize=True` — имитация поведения человека

## Обновление CloakBrowser

```bash
uv run python -m cloakbrowser update
```

## Решение проблем

1. **Браузер не запускается** — проверьте `uv run python -m cloakbrowser info`
2. **Прокси не работает** — убедитесь, что прокси доступен
3. **Instagram блокирует** — смените прокси, добавьте задержки
4. **2FA не работает** — проверьте секретный ключ
