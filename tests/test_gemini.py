#!/usr/bin/env python3
"""
Тест Gemini API (новый SDK)
"""
import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from google import genai
    from src.utils.api_config import APIConfig
    
    print("🤖 Тест Gemini API (новый SDK)")
    print()
    
    # API ключ из .env через централизованную конфигурацию
    config = APIConfig()
    
    if not config.has_gemini():
        print("❌ GEMINI_API_KEY не найден в .env")
        print("💡 Добавьте ключ в .env файл:")
        print("   GEMINI_API_KEY=your-key-here")
        sys.exit(1)
    
    client = genai.Client(api_key=config.get_gemini_key())
    
    print("✅ Gemini API инициализирован")
    print()
    
    # Тестовый запрос
    test_comment = "Отличное видео! Очень понравилось 👍"
    print(f"💬 Тестовый комментарий: {test_comment}")
    print()
    
    prompt = f"Напиши короткий дружелюбный ответ (до 50 символов) на комментарий TikTok: {test_comment}"
    
    print("🔄 Генерация ответа...")
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    reply = response.text.strip()
    
    print()
    print("✅ Успешно!")
    print(f"🤖 AI ответ: {reply}")
    print()
    print("🎉 Gemini API работает корректно!")
    
except ImportError:
    print("❌ google-genai не установлен")
    print("Установи: pip install google-genai")
except Exception as e:
    print(f"❌ Ошибка: {e}")
    print()
    print("Проверь:")
    print("1. API ключ корректный")
    print("2. Есть интернет")
    print("3. Квота API не исчерпана")
