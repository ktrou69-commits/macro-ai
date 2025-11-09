#!/bin/bash
# start_chrome_debug.sh
# Запуск Chrome с remote debugging портом для Selenium

echo "🚀 Запуск Chrome с debug портом..."
echo "📍 Порт: 9222"
echo ""

# Закрываем все экземпляры Chrome
killall "Google Chrome" 2>/dev/null

# Ждем закрытия
sleep 1

# Запускаем Chrome с debug портом
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=9222 \
  --user-data-dir="/tmp/chrome-debug-profile" \
  > /dev/null 2>&1 &

echo "✅ Chrome запущен!"
echo "📍 Debug port: http://localhost:9222"
echo ""
echo "Теперь:"
echo "1. Зайди на TikTok"
echo "2. Залогинься"
echo "3. Запусти макрос tiktok_dom_test"
