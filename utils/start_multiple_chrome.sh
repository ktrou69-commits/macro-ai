#!/bin/bash
# start_multiple_chrome.sh
# Запуск нескольких Chrome с разными debug портами для параллельной работы

NUM_INSTANCES=${1:-3}  # По умолчанию 3 окна

echo "🚀 Запуск $NUM_INSTANCES экземпляров Chrome..."
echo ""

# Закрываем все экземпляры Chrome
echo "🧹 Закрытие существующих Chrome..."
killall "Google Chrome" 2>/dev/null
sleep 2

# Запускаем экземпляры
for i in $(seq 0 $((NUM_INSTANCES-1))); do
    PORT=$((9222 + i))
    PROFILE_DIR="/tmp/chrome-profile-$i"
    WINDOW_X=$((i * 50))
    WINDOW_Y=$((i * 50))
    
    echo "📍 Chrome #$i:"
    echo "   Порт: $PORT"
    echo "   Профиль: $PROFILE_DIR"
    echo "   Позиция: ($WINDOW_X, $WINDOW_Y)"
    
    /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
      --remote-debugging-port=$PORT \
      --user-data-dir="$PROFILE_DIR" \
      --window-position=$WINDOW_X,$WINDOW_Y \
      --window-size=800,900 \
      > /dev/null 2>&1 &
    
    sleep 1
done

echo ""
echo "✅ Запущено $NUM_INSTANCES экземпляров Chrome!"
echo ""
echo "📍 Debug порты:"
for i in $(seq 0 $((NUM_INSTANCES-1))); do
    PORT=$((9222 + i))
    echo "   Chrome #$i: http://localhost:$PORT"
done
echo ""
echo "💡 Теперь:"
echo "   1. Залогинься в каждом окне на разные аккаунты"
echo "   2. Открой TikTok в каждом окне"
echo "   3. Запусти: python3 parallel_runner.py --use-existing --instances $NUM_INSTANCES --macro <макрос>"
