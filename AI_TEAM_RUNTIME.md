# AI Team Runtime — автономный бесплатный режим

## Требования
- Python 3.10+ (только стандартная библиотека).
- Репозиторий GitHub.
- Опционально: уже существующие TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID для доставки отчёта.
- AI-provider keys, Cloudflare, API-кредиты и платёжные данные не нужны.

## Локальный запуск
```bash
python scripts/site_audit.py
python -m unittest discover -s tests -v
python scripts/ai_team.py
```
Отчёты в reports/:
- daily-ai-report-YYYY-MM-DD.md
- daily-ai-report-YYYY-MM-DD.json

## GitHub Actions
Daily AI team report запускается вручную через Actions → Daily AI team report → Run workflow и ежедневно в 09:15 Asia/Barnaul (02:15 UTC). Расписание доступно после merge workflow в default branch.

Если Telegram secrets не заданы, отправка пропускается; отчёт остаётся в Actions artifact. Для анализа секреты не нужны.

## Данные и ограничения
- Исходники не отправляются наружу, веб-запросы не выполняются.
- Конкуренты автоматически не исследуются.
- Поисковые позиции, трафик, конверсии и продажи не измеряются без источников.
- Визуальный рендер и мобильные скриншоты не проверяются.
- Отчёт — технический анализ и гипотезы, не медицинское или юридическое заключение.
- Запуск не изменяет сайт, не создаёт PR, не делает merge и не публикует изменения.

## Безопасность
- Не добавлять OPENAI_API_KEY, OPEN_AI_KEY, Cloudflare или другие AI-provider secrets.
- Workflow имеет contents: read.
- Изменения сайта — отдельная ветка и PR, с ручным решением владельца.
