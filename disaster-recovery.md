# Disaster Recovery — полное восстановление Hermes

## Источники для восстановления

| Источник | Что содержит | Где |
|----------|-------------|-----|
| **Google Drive** (rclone) | Полный архив: конфиг, skills, cron, wiki, проекты, БД | `gdrive:hermes-backup/daily/` |
| **GitHub** | Код, шаблоны, документация, AGENTS.md | `github.com/Udavka2020/lisnic-alarm-tenders` |
| **Твоя память** | Telegram Bot Token, API-ключи (`.env`) | Хранятся отдельно |

---

## 1. Подготовка нового сервера

```bash
# Установка Docker (если не установлен)
curl -fsSL https://get.docker.com | bash

# Установка Hermes
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash

# Установка rclone для доступа к Google Drive
curl https://rclone.org/install.sh | bash
```

---

## 2. Настройка доступа к Google Drive (rclone)

```bash
# Настроить rclone для Google Drive
rclone config
# Выбрать: n) New remote → имя: gdrive → Google Drive → OAuth
# Скопировать rclone.conf из бэкапа если есть:
#   ~/.config/rclone/rclone.conf

# Проверить доступ
rclone ls gdrive:hermes-backup/daily/
```

---

## 3. Восстановление из Google Drive бэкапа

```bash
# Найти последний бэкап
LATEST=$(rclone ls gdrive:hermes-backup/daily/ | grep 'hermes-full-' | sort -r | head -1 | awk '{print $2}')
echo "Последний бэкап: $LATEST"

# Скачать архив
rclone copy "gdrive:hermes-backup/daily/$LATEST" /tmp/

# Проверить контрольную сумму
cd /tmp
sha256sum -c "$LATEST.sha256"

# Распаковать в /root
tar xzf "$LATEST" -C /root

# Проверить, что восстановилось
ls -la /root/.hermes/config.yaml
ls -la /root/wiki/
ls -la /root/projects/
```

---

## 4. Восстановление секретов (`.env`)

**Без этого шага Hermes не запустится!**

```bash
# Создать .env с API-ключами
nano /root/.hermes/.env
```

Минимальное содержимое `.env`:

```env
# Основной провайдер
OPENROUTER_API_KEY=sk-or-v1-...

# Telegram бот (тот же, что и был)
TELEGRAM_BOT_TOKEN=8834252309:...

# GitHub токен (для доступа к репозиторию)
GITHUB_TOKEN=ghp_...

# GitHub Models (бесплатный доступ к LLM)
GITHUB_MODELS_TOKEN=github_pat_...

# Токен для Home Finance бота
# (если восстанавливается)
# TELEGRAM_HOME_FINANCE_TOKEN=...
```

---

## 5. Восстановление из GitHub

```bash
# Клонировать репозиторий
cd ~
git clone https://github.com/Udavka2020/lisnic-alarm-tenders.git

# Скопировать AGENTS.md в корень (для Copilot, Claude Code)
cp lisnic-alarm-tenders/AGENTS.md /root/AGENTS.md

# Шаблоны форм уже в репозитории:
#   tenders/21641864/forms/  — Anexa OMF 115
# Скопировать если нужны отдельно
cp -r lisnic-alarm-tenders/tenders/21641864/forms/* \
  ~/projects/tender-21641864/documents/forms/ 2>/dev/null || true
```

---

## 6. Восстановление cron задач

```bash
# Запустить Hermes
hermes

# Внутри Hermes восстановить cron задачи (все 12 — см. cron-jobs.md)
```

**Ключевые задачи (обязательные):**

```bash
# Мониторинг тендеров — Пн-Пт 8:05, 12:05, 16:05
cronjob create --schedule "5 8,12,16 * * 1-5" \
  --name "monitor-tenders-moldova" \
  --skill tenders-moldova \
  --prompt "Поиск тендеров по CPV + ключевым словам на achizitii.md..."
  --deliver origin

# Домашние финансы — ежедневно 21:00
cronjob create --schedule "0 21 * * *" \
  --name "home-finance-daily" \
  --skill home-finance \
  --prompt "Ежедневный отчёт по финансам..."
  --deliver telegram

# Полный бэкап — ежедневно 00:01
cronjob create --schedule "1 0 * * *" \
  --name "hermes-full-backup" \
  --script backup-full.sh \
  --deliver local

# Мониторинг топ-налогоплательщиков — Пн-Пт 8:30
cronjob create --schedule "30 8 * * 1-5" \
  --name "monitor-top-taxpayers" \
  --skill tenders-moldova \
  --prompt "Поиск тендеров топ-550 налогоплательщиков..."
  --deliver origin

# Конкуренты — Пн 9:00
cronjob create --schedule "0 9 * * 1" \
  --name "monitor-competitors" \
  --skill tenders-moldova \
  --prompt "Мониторинг конкурентов..."
  --deliver origin

# Товары/скидки — Пн-Пт 9:15
cronjob create --schedule "15 9 * * 1-5" \
  --name "monitor-products-ads" \
  --skill tenders-moldova \
  --prompt "Мониторинг товаров и скидок..."
  --deliver origin

# Парсинг конкурентов — ежедневно 20:21
cronjob create --schedule "21 20 * * *" \
  --name "parse-competitors-sites" \
  --skill parse-security-products \
  --prompt "Парсинг safe24.md, videosecurity.md, dahua.md..."
  --deliver origin

# Парсинг exterior.md — Ср 3:05
cronjob create --schedule "5 3 * * 3" \
  --name "parse-exterior-products" \
  --skill tenders-moldova \
  --prompt "Парсинг exterior.md..."
  --deliver origin

# Сохранение истории — ежедневно 23:00
cronjob create --schedule "0 23 * * *" \
  --name "save-conversation-history" \
  --prompt "Сохрани историю сегодняшних разговоров в Wiki..."
  --deliver origin

# Safe24 watchdog — Пн-Пт 8:55
cronjob create --schedule "55 8 * * 1-5" \
  --name "safe24-watchdog" \
  --script safe24-watchdog.sh \
  --no_agent true \
  --deliver origin
```

---

## 7. Настройка Telegram

```bash
# Gateway запустится автоматически при старте Hermes
# Проверить статус:
hermes gateway status

# Если gateway не видит бота — проверить токен в .env
# TELEGRAM_BOT_TOKEN=8834252309:...
```

---

## 8. Проверка восстановления

```bash
# Проверить конфиг
hermes doctor
hermes config check

# Проверить состояние
hermes status

# Проверить cron
cronjob list

# Проверить Telegram
# Отправить боту любое сообщение — должен ответить

# Проверить GitHub Actions (дублирующий мониторинг)
# Зайти: https://github.com/Udavka2020/lisnic-alarm-tenders/actions
# Нажать: Tender Monitor → Run workflow
# Через минуту — уведомление в Telegram
```

---

## 9. Что делать, если Google Drive недоступен

Если rclone не настроен или Google Drive недоступен:

1. **GitHub** — вся документация, шаблоны, AGENTS.md, скрипты
2. **Локальные бэкапы** — если сервер не упал полностью, архивы лежат в:
   ```
   ~/.hermes/backups/full/daily/
   ~/.hermes/backups/full/weekly/
   ~/.hermes/backups/full/monthly/
   ```
3. **Hermes устанавливается заново** — команды из раздела 1
4. **Cron задачи** — восстанавливаются вручную (раздел 6)
5. **GitHub Actions** — мониторинг тендеров работает независимо

---

## 10. Схема взаимодействия

```
                        ┌──────────────┐
                        │  Google Drive │  ← полный бэкап (tar.gz)
                        │  (rclone)     │
                        └──────┬───────┘
                               │ ежедневно 00:01
                               ▼
┌─────────────────────────────────────────────────────┐
│                     Сервер Hermes                    │
│                                                      │
│  ~/.hermes/         ← config, skills, cron, БД       │
│  ~/wiki/            ← тендеры, знания, концепции     │
│  ~/projects/        ← тендерные проекты, формы       │
│  ~/lisnic-alarm-tenders/ ← git clone                 │
│                                                      │
└─────────────────────────────────────────────────────┘
                               │
                    git push   │   git pull
                               ▼
┌─────────────────────────────────────────────────────┐
│                     GitHub                           │
│                                                      │
│  lisnic-alarm-tenders/    ← код, docs, шаблоны       │
│  .github/workflows/       ← Tender Monitor           │
│  AGENTS.md                ← контекст для AI-агентов  │
│  cron-jobs.md             ← инструкция для restore   │
│                                                      │
│  GitHub Actions работают ДАЖЕ если сервер упал       │
└─────────────────────────────────────────────────────┘
```

**Ключевой принцип:**  
- **Google Drive** = полная копия (конфиг, БД, сессии, wiki)  
- **GitHub** = рабочая база знаний (код, docs, шаблоны, Actions)  
- Восстанавливать нужно **оба источника**