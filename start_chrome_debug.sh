#!/bin/bash
# Запуск Chrome с remote debugging для Selenium

# Закрыть все Chrome процессы
killall "Google Chrome" 2>/dev/null

# Запустить Chrome с debugging
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="/tmp/chrome-debug" \
  --no-first-run \
  --no-default-browser-check \
  "https://www.tiktok.com" &

echo "✅ Chrome запущен с debugging на порту 9222"
echo "🔗 Selenium может подключиться через debuggerAddress"
