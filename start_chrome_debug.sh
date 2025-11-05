#!/bin/bash
# Запуск Chrome с remote debugging для Selenium

# Закрыть все Chrome процессы
killall "Google Chrome" 2>/dev/null

# Найти Chrome (может быть "Google Chrome.app" или "Google Chrome 2.app")
CHROME_PATH=""
if [ -f "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" ]; then
    CHROME_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
elif [ -f "/Applications/Google Chrome 2.app/Contents/MacOS/Google Chrome" ]; then
    CHROME_PATH="/Applications/Google Chrome 2.app/Contents/MacOS/Google Chrome"
else
    echo "❌ Chrome не найден!"
    echo "💡 Установи Chrome: https://www.google.com/chrome/"
    exit 1
fi

echo "🔍 Найден Chrome: $CHROME_PATH"

# Запустить Chrome с debugging
"$CHROME_PATH" \
  --remote-debugging-port=9222 \
  --user-data-dir="/tmp/chrome-debug" \
  --no-first-run \
  --no-default-browser-check \
  "https://www.tiktok.com" &

echo "✅ Chrome запущен с debugging на порту 9222"
echo "🔗 Selenium может подключиться через debuggerAddress"
