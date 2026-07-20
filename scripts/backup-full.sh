#!/bin/bash
# Полный бэкап Hermes + Home Finance + Wiki — расширенная версия
set -euo pipefail

DATE_DIR=$(date +%Y-%m-%d)
DAY_OF_WEEK=$(date +%u)
ARCHIVE_NAME="hermes-full-$DATE_DIR.tar.gz"
CHECKSUM_NAME="$ARCHIVE_NAME.sha256"
ARCHIVE_PATH="/tmp/$ARCHIVE_NAME"
CHECKSUM_PATH="/tmp/$CHECKSUM_NAME"
LOCAL_DAILY_DIR="/root/.hermes/backups/full/daily"
LOCAL_WEEKLY_DIR="/root/.hermes/backups/full/weekly"
LOCAL_MONTHLY_DIR="/root/.hermes/backups/full/monthly"
KEEP_LOCAL_DAILY=7
KEEP_LOCAL_WEEKLY=8
KEEP_LOCAL_MONTHLY=6

echo "🔹 Создание расширенного полного бэкапа..."
rm -f "$ARCHIVE_PATH" "$CHECKSUM_PATH"
mkdir -p "$LOCAL_DAILY_DIR" "$LOCAL_WEEKLY_DIR" "$LOCAL_MONTHLY_DIR"

# Инвентарь бэкапа (сохраняется в сам архив)
cat > /tmp/backup-inventory.txt << 'INVENTORY'
=== РАСШИРЕННЫЙ ПОЛНЫЙ БЭКАП HERMES ===
Дата: DATE_PLACEHOLDER

--- КОНФИГУРАЦИЯ HERMES (.hermes/) ---
1. config.yaml                 — Конфигурация Hermes
2. SOUL.md                     — Описание агента
3. skills/                     — Все скилы
4. plugins/                    — Плагины
5. cron/                       — Кроны и их состояние
6. memories/                   — Persistent memory (факты о пользователе/среде)
7. state/                      — Служебное состояние
8. state.db                    — БД сессий (история разговоров)
9. sessions/                   — Дампы сессий (JSON)
10. scripts/                   — Скрипты (backup-full.sh, gateway-watchdog и др.)
11. home_finance.db            — База данных финансов
12. kanban.db + kanban/        — Kanban-доски
13. auth.json                  — Auth-токены
14. channel_directory.json     — Каналы
15. gateway_state.json         — Состояние gateway
16. platforms/                 — Платформы
17. pairing/                   — Pairing-информация
18. hooks/                     — Хуки
19. bin/                       — Утилиты
20. backups/                   — Предыдущие бэкапы и локальные копии

--- ДОПОЛНИТЕЛЬНЫЕ ДАННЫЕ ---
21. backup-tools/              — Вспомогательные скрипты бэкапов
22. home-finance/              — Код и документация бота финансов
23. wiki/                      — Wiki, включая tender PDF/DOC/DOCX, сертификаты, формы
24. projects/                  — Проекты по тендерам (документы, спецификации, формы)
25. .config/rclone/rclone.conf — Конфиг rclone
26. lisnic-alarm-tenders/     — Репозиторий GitHub (docs, шаблоны, disaster-recovery.md)

--- ЧТО СОЗДАЁТСЯ ДОПОЛНИТЕЛЬНО ---
26. ARCHIVE_NAME_PLACEHOLDER         — Основной архив
27. CHECKSUM_NAME_PLACEHOLDER        — SHA256 checksum архива
28. Локальные копии в ~/.hermes/backups/full/ (daily/weekly/monthly)

НЕ ВКЛЮЧЕНО (безопасность / кэш / восстанавливаемо):
- .hermes/.env                 — API-ключи (секреты копировать отдельно в шифрованный архив)
- .hermes/home_finance.env     — Токен Telegram-бота (секреты копировать отдельно в шифрованный архив)
- .hermes/audio_cache/         — Кэш аудио
- .hermes/image_cache/         — Кэш изображений
- .hermes/cache/               — Кэш моделей/данных
- .hermes/logs/                — Логи (не нужны для restore)
- .hermes/sandboxes/           — Песочницы
- .hermes/models_dev_cache.json — Кэш моделей (перестроится)
- wiki/raw/conversations/      — Сырые разговоры
- .venv, __pycache__, *.pyc    — Виртуальные окружения и кэш Python

Восстановление: смотри wiki/guides/disaster-recovery.md
INVENTORY
sed -i "s/DATE_PLACEHOLDER/$DATE_DIR/" /tmp/backup-inventory.txt
sed -i "s/ARCHIVE_NAME_PLACEHOLDER/$ARCHIVE_NAME/" /tmp/backup-inventory.txt
sed -i "s/CHECKSUM_NAME_PLACEHOLDER/$CHECKSUM_NAME/" /tmp/backup-inventory.txt

# Создаём архив — все значимые данные Hermes
tar czf "$ARCHIVE_PATH" \
  --exclude='.venv' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.hermes/.env' \
  --exclude='.hermes/home_finance.env' \
  --exclude='.hermes/audio_cache' \
  --exclude='.hermes/image_cache' \
  --exclude='.hermes/cache' \
  --exclude='.hermes/logs' \
  --exclude='.hermes/sandboxes' \
  --exclude='.hermes/models_dev_cache.json' \
  --exclude='.hermes/.skills_prompt_snapshot.json' \
  --exclude='.hermes/.update_check' \
  --exclude='.hermes/gateway.lock' \
  --exclude='.hermes/gateway.pid' \
  --exclude='.hermes/processes.json' \
  --exclude='.hermes/backups/*/.env' \
  --exclude='.hermes/backups/full' \
  --exclude='wiki/raw/conversations' \
  --exclude='.hermes/*.db-shm' \
  --exclude='.hermes/*.db-wal' \
  -C /root \
  .hermes/config.yaml \
  .hermes/SOUL.md \
  .hermes/skills \
  .hermes/plugins \
  .hermes/cron \
  .hermes/memories \
  .hermes/state \
  .hermes/state.db \
  .hermes/sessions \
  .hermes/scripts \
  .hermes/home_finance.db \
  .hermes/kanban.db \
  .hermes/kanban \
  .hermes/auth.json \
  .hermes/channel_directory.json \
  .hermes/gateway_state.json \
  .hermes/platforms \
  .hermes/pairing \
  .hermes/hooks \
  .hermes/bin \
  .hermes/backups \
  backup-tools \
  home-finance \
  wiki \
  projects \
  lisnic-alarm-tenders \
  .config/rclone/rclone.conf \
  -C /tmp backup-inventory.txt \
  2>/tmp/hermes-tar-error.log

# Базовая проверка архива
tar tzf "$ARCHIVE_PATH" >/dev/null
tar tzf "$ARCHIVE_PATH" > /tmp/hermes-archive-filelist.txt
for required_path in \
  ".hermes/config.yaml" \
  ".hermes/state.db" \
  ".hermes/scripts/backup-full.sh" \
  "wiki/tenders/index.md" \
  "projects" \
  ".config/rclone/rclone.conf"
do
  if ! grep -q "^${required_path}" /tmp/hermes-archive-filelist.txt; then
    echo "❌ В архиве отсутствует обязательный путь: $required_path"
    exit 1
  fi
done

sha256sum "$ARCHIVE_PATH" | sed "s|  $ARCHIVE_PATH|  $ARCHIVE_NAME|" > "$CHECKSUM_PATH"
ARCHIVE_SIZE=$(du -h "$ARCHIVE_PATH" | cut -f1)
echo "  ✅ Архив: $ARCHIVE_PATH ($ARCHIVE_SIZE)"
echo "  ✅ SHA256: $(cut -d' ' -f1 "$CHECKSUM_PATH")"

# Локальные копии
cp -f "$ARCHIVE_PATH" "$LOCAL_DAILY_DIR/$ARCHIVE_NAME"
cp -f "$CHECKSUM_PATH" "$LOCAL_DAILY_DIR/$CHECKSUM_NAME"
echo "  ✅ Локальная daily-копия: $LOCAL_DAILY_DIR/$ARCHIVE_NAME"

if [ "$DAY_OF_WEEK" = "7" ]; then
  cp -f "$ARCHIVE_PATH" "$LOCAL_WEEKLY_DIR/$ARCHIVE_NAME"
  cp -f "$CHECKSUM_PATH" "$LOCAL_WEEKLY_DIR/$CHECKSUM_NAME"
  echo "  ✅ Локальная weekly-копия: $LOCAL_WEEKLY_DIR/$ARCHIVE_NAME"
fi

if [ "$(date +%d)" = "01" ]; then
  cp -f "$ARCHIVE_PATH" "$LOCAL_MONTHLY_DIR/$ARCHIVE_NAME"
  cp -f "$CHECKSUM_PATH" "$LOCAL_MONTHLY_DIR/$CHECKSUM_NAME"
  echo "  ✅ Локальная monthly-копия: $LOCAL_MONTHLY_DIR/$ARCHIVE_NAME"
fi

# Ротация локальных копий
(ls -1t "$LOCAL_DAILY_DIR"/hermes-full-*.tar.gz 2>/dev/null || true) | tail -n +$((KEEP_LOCAL_DAILY + 1)) | xargs -r rm -f
(ls -1t "$LOCAL_DAILY_DIR"/hermes-full-*.tar.gz.sha256 2>/dev/null || true) | tail -n +$((KEEP_LOCAL_DAILY + 1)) | xargs -r rm -f
(ls -1t "$LOCAL_WEEKLY_DIR"/hermes-full-*.tar.gz 2>/dev/null || true) | tail -n +$((KEEP_LOCAL_WEEKLY + 1)) | xargs -r rm -f
(ls -1t "$LOCAL_WEEKLY_DIR"/hermes-full-*.tar.gz.sha256 2>/dev/null || true) | tail -n +$((KEEP_LOCAL_WEEKLY + 1)) | xargs -r rm -f
(ls -1t "$LOCAL_MONTHLY_DIR"/hermes-full-*.tar.gz 2>/dev/null || true) | tail -n +$((KEEP_LOCAL_MONTHLY + 1)) | xargs -r rm -f
(ls -1t "$LOCAL_MONTHLY_DIR"/hermes-full-*.tar.gz.sha256 2>/dev/null || true) | tail -n +$((KEEP_LOCAL_MONTHLY + 1)) | xargs -r rm -f

# Инвентарь архива
echo ""
echo "=== Содержимое архива ==="
tar tzf "$ARCHIVE_PATH" 2>/dev/null | grep -v '/$' | sort
echo "---"
echo "Всего файлов: $(tar tzf "$ARCHIVE_PATH" 2>/dev/null | grep -v '/$' | wc -l)"
echo ""

# Копируем на Google Диск
if command -v rclone &>/dev/null && rclone listremotes 2>/dev/null | grep -q "gdrive:"; then
    DEST="gdrive:hermes-backup/daily/$DATE_DIR/"
    rclone delete "$DEST$ARCHIVE_NAME" 2>/dev/null || true
    rclone delete "$DEST$CHECKSUM_NAME" 2>/dev/null || true
    rclone copy "$ARCHIVE_PATH" "$DEST" 2>/dev/null
    rclone copy "$CHECKSUM_PATH" "$DEST" 2>/dev/null
    echo "  ✅ На Google Диск: $(rclone size "$DEST$ARCHIVE_NAME" 2>/dev/null | grep "Total size")"
    echo "  ✅ Checksum на Google Диск: $DEST$CHECKSUM_NAME"

    if [ "$DAY_OF_WEEK" = "7" ]; then
        WEEKLY_DEST="gdrive:hermes-backup/weekly/week-$(date +%V)/"
        rclone copy "$ARCHIVE_PATH" "$WEEKLY_DEST" 2>/dev/null
        rclone copy "$CHECKSUM_PATH" "$WEEKLY_DEST" 2>/dev/null
        echo "  ✅ Недельный архив"
    fi
    if [ "$(date +%d)" = "01" ]; then
        MONTHLY_DEST="gdrive:hermes-backup/monthly/$(date +%Y-%m)/"
        rclone copy "$ARCHIVE_PATH" "$MONTHLY_DEST" 2>/dev/null
        rclone copy "$CHECKSUM_PATH" "$MONTHLY_DEST" 2>/dev/null
        echo "  ✅ Месячный архив"
    fi
    rclone delete --min-age 7d "gdrive:hermes-backup/daily/" 2>/dev/null || true
    echo "  ✅ Ротация daily на Google Drive: удалено старше 7 дней"

    # Отдельный бекап тендерных файлов (быстрый доступ как вторичная копия)
    if [ -d "/root/wiki/tenders" ] && [ "$(find /root/wiki/tenders -type f | wc -l)" -gt 0 ]; then
        TENDERS_DEST="gdrive:hermes-backup/tenders/$DATE_DIR/"
        echo ""
        echo "📄 Отдельный бекап тендерных файлов..."
        rclone delete "$TENDERS_DEST" 2>/dev/null || true
        rclone copy /root/wiki/tenders "$TENDERS_DEST" \
            --include '*.pdf' --include '*.docx' --include '*.doc' 2>/dev/null
        TENDERS_COUNT=$(rclone size "$TENDERS_DEST" 2>/dev/null | grep "Total size" || echo "0")
        TENDERS_FILES=$(rclone ls "$TENDERS_DEST" 2>/dev/null | wc -l)
        echo "  ✅ Тендерные файлы на Google Диск: $TENDERS_FILES файлов ($TENDERS_COUNT)"

        rclone delete "gdrive:hermes-backup/tenders/latest" 2>/dev/null || true
        rclone copy /root/wiki/tenders "gdrive:hermes-backup/tenders/latest/" \
            --include '*.pdf' --include '*.docx' --include '*.doc' 2>/dev/null
        echo "  ✅ Обновлена ссылка 'latest'"
    fi
else
    echo "  ⚠️ rclone не настроен"
fi

rm -f /tmp/backup-inventory.txt /tmp/hermes-tar-error.log /tmp/hermes-archive-filelist.txt "$ARCHIVE_PATH" "$CHECKSUM_PATH"
echo "✅ Бэкап завершён: $(date)"
