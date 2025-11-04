#!/bin/bash

# setup.sh - Автоматическая установка окружения для Macro AI

echo "=================================="
echo "🚀 Macro AI - Установка окружения"
echo "=================================="

# Проверка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 не найден!"
    echo "   Установи Python 3.10+ с python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python $PYTHON_VERSION найден"

# Создание виртуального окружения
echo ""
echo "📦 Создаю виртуальное окружение..."
python3 -m venv venv

# Активация
echo "🔄 Активирую окружение..."
source venv/bin/activate

# Обновление pip
echo "⬆️  Обновляю pip..."
pip install --upgrade pip --quiet

# Установка зависимостей
echo "📥 Устанавливаю зависимости..."
pip install -r requirements.txt

# Создание структуры папок
echo ""
echo "📁 Создаю структуру папок..."
mkdir -p models
mkdir -p data/images/train
mkdir -p data/images/val
mkdir -p utils

# Проверка разрешений macOS
echo ""
echo "=================================="
echo "⚠️  ВАЖНО: Настрой разрешения macOS"
echo "=================================="
echo ""
echo "Открой System Settings и добавь Terminal в:"
echo "  1. Privacy & Security → Screen Recording"
echo "  2. Privacy & Security → Accessibility"
echo ""
echo "После добавления перезапусти Terminal!"
echo ""

# Проверка Apple Silicon
if [[ $(uname -m) == 'arm64' ]]; then
    echo "🍎 Обнаружен Apple Silicon (M1/M2/M3)"
    echo "   Рекомендуется установить PyTorch с MPS:"
    echo "   pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu"
    echo ""
fi

echo "=================================="
echo "✅ Установка завершена!"
echo "=================================="
echo ""
echo "Следующие шаги:"
echo "  1. Активируй окружение: source venv/bin/activate"
echo "  2. Захвати шаблон кнопки: python utils/capture_button.py"
echo "  3. Запусти макрос: python macro_ai.py --template"
echo ""
echo "Документация: cat README.md"
echo "=================================="
