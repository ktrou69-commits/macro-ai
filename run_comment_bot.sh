#!/bin/bash
# Автоматический запуск TikTok Comment Bot
# OCR: EasyOCR, LLM: Ollama (локальная), Стиль: Дружелюбный

echo "🚀 Запуск TikTok Comment Bot..."
echo ""
echo "Параметры:"
echo "  📖 OCR: EasyOCR (RU + EN)"
echo "  🧠 LLM: Ollama (Llama2)"
echo "  🎨 Стиль: Дружелюбный"
echo ""

# Автоматический ввод параметров
python3 tiktok_comment_bot.py << EOF
1
3
1
1
EOF
