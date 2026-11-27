# AI Runtime: бесплатный запуск и интеграции

## Архитектура текущего этапа
1. GitHub Actions запускает статический аудит.
2. scripts/ai_team.py собирает JSON-аудит и инвентаризацию контента.
3. Один вызов Cloudflare Workers AI выполняет многофункциональный командный разбор.
4. Markdown-отчёт сохраняется как GitHub Actions artifact на 30 дней.
5. Telegram получает отчёт даже если AI недоступен, при наличии Telegram secrets.

## Бесплатный режим — строго
- Используется только Cloudflare Workers AI на тарифе Workers Free.
- На дату подготовки официальная бесплатная квота Workers AI — 10 000 Neurons в сутки; лимит сбрасывается ежедневно. Лимиты и доступность моделей могут меняться.
- На Workers Free после исчерпания квоты запросы должны завершаться ошибкой; runtime не повторяет запросы и не переключается на платный API.
- Не подключать Workers Paid, Unified Billing, prepaid credits или платные модели.
- Не хранить и не использовать OPENAI_API_KEY. Старый OpenAI API backend удалён из workflow.
- При ошибке AI создаётся fallback-отчёт, статический аудит и Telegram продолжают работать.

Официальная информация: https://developers.cloudflare.com/workers-ai/platform/pricing/
Модель по умолчанию: @cf/zai-org/glm-4.7-flash. Проверить доступность в Workers Free перед запуском. Если модель перестанет быть бесплатной — не переходить на платный план.

## GitHub Actions Secrets
Добавить в Settings → Secrets and variables → Actions → Repository secrets:
- CLOUDFLARE_API_TOKEN — Cloudflare Workers AI API token с минимально необходимым Workers AI permission.
- CLOUDFLARE_ACCOUNT_ID — Cloudflare Account ID.
- TELEGRAM_BOT_TOKEN — существующий Telegram bot token.
- TELEGRAM_CHAT_ID — существующий Telegram chat ID.

Не отправлять токены в чат, issue, PR или код. Не выводить их в логи.
Опциональная Actions variable:
- CLOUDFLARE_AI_MODEL — ID модели; по умолчанию @cf/zai-org/glm-4.7-flash.

Создавать Cloudflare token через Workers AI → Use REST API. Не включать платный план и не добавлять платёжный метод ради проекта. Если Cloudflare предлагает перейти на Workers Paid или добавить оплату — остановиться.

## Запуск
- Ежедневно: 09:15 Asia/Barnaul.
- Ручной запуск: GitHub → Actions → Daily AI team report → Run workflow.

## Текущие ограничения
- AI runtime пока read-only: не меняет файлы сайта и не создаёт PR.
- Не подключены Search Console, веб-аналитика, Ozon Seller и Wildberries Seller.
- Конкурентное исследование не выполняется без проверенных веб-источников.
- Один AI-запрос на запуск для экономии квоты; независимые роли — разделы одного командного анализа.

## Следующий этап
После проверки Workers AI и Telegram:
1. Включить разработчика, который готовит изменения в отдельной ветке.
2. Подключить ограниченные GitHub permissions для создания ветки и PR.
3. Добавить CI/QA gate.
4. Запретить автоматический merge и деплой без решения владельца.
