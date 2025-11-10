#!/bin/bash
#
# run_tests.sh
# 🧪 Быстрый запуск всех тестов
#
# Использование:
#   ./run_tests.sh           # Все тесты
#   ./run_tests.sh smoke     # Только smoke тесты
#   ./run_tests.sh quick     # Быстрые тесты
#

set -e  # Остановиться при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "======================================================================"
echo "🧪 ЗАПУСК ТЕСТОВ"
echo "======================================================================"
echo ""

# Определяем какие тесты запускать
TEST_TYPE=${1:-all}

case $TEST_TYPE in
  smoke)
    echo "🔥 Запуск SMOKE тестов (проверка всей системы)..."
    echo ""
    python3 tests/test_smoke.py
    ;;
    
  quick)
    echo "⚡ Запуск БЫСТРЫХ тестов..."
    echo ""
    python3 tests/test_api_config.py
    python3 tests/test_config.py
    python3 tests/test_imports.py
    ;;
    
  all)
    echo "📦 Запуск ВСЕХ тестов..."
    echo ""
    
    # Smoke тесты (самые важные)
    echo "${BLUE}🔥 1. Smoke тесты${NC}"
    python3 tests/test_smoke.py
    echo ""
    
    # Критичные тесты
    echo "${BLUE}🔥 2. Критичные тесты${NC}"
    python3 tests/test_dsl_full.py
    python3 tests/test_macro_loading.py
    echo ""
    
    # Важные тесты
    echo "${BLUE}⭐ 3. Важные тесты${NC}"
    python3 tests/test_vision_basic.py
    python3 tests/test_ai_basic.py
    python3 tests/test_utils_full.py
    echo ""
    
    # Конфигурация
    echo "${BLUE}⚙️  4. Тесты конфигурации${NC}"
    python3 tests/test_api_config.py
    python3 tests/test_config.py
    echo ""
    
    # Импорты
    echo "${BLUE}📦 5. Тесты импортов${NC}"
    python3 tests/test_imports.py
    echo ""
    
    # DSL
    echo "${BLUE}📝 6. Тесты DSL${NC}"
    python3 tests/test_dsl.py
    echo ""
    
    # Gemini API
    echo "${BLUE}🤖 7. Тесты Gemini API${NC}"
    python3 tests/test_gemini.py
    echo ""
    ;;
    
  *)
    echo "${RED}❌ Неизвестный тип тестов: $TEST_TYPE${NC}"
    echo ""
    echo "Использование:"
    echo "  ./run_tests.sh           # Все тесты"
    echo "  ./run_tests.sh smoke     # Только smoke тесты"
    echo "  ./run_tests.sh quick     # Быстрые тесты"
    echo ""
    exit 1
    ;;
esac

echo ""
echo "======================================================================"
echo "${GREEN}✅ ВСЕ ТЕСТЫ ЗАВЕРШЕНЫ!${NC}"
echo "======================================================================"
echo ""
echo "💡 Система работоспособна!"
echo ""
