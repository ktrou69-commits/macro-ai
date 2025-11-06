#!/usr/bin/env python3
"""
Тест Gemini API (новый SDK)
"""
import os

try:
    from google import genai
    
    print("🤖 Тест Gemini API (новый SDK)")
    print()
    
    # API ключ из переменной окружения
    # Клиент автоматически подхватит GEMINI_API_KEY
    client = genai.Client(api_key=os.getenv('GEMINI_API_KEY', 'AIzaSyBGlFjt6bKJLJqcsavArM6wb7voH111gc8'))
    
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
