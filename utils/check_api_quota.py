#!/usr/bin/env python3
"""
check_api_quota.py
Проверка статуса API квоты Gemini

Показывает:
- Текущий API ключ
- Модель
- Результат тестового запроса
- Рекомендации
"""

import sys
from pathlib import Path

# Добавляем корень проекта в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.api_config import api_config

def check_quota():
    """Проверяет квоту API"""
    print("="*80)
    print("🔍 ПРОВЕРКА GEMINI API КВОТЫ".center(80))
    print("="*80)
    print()
    
    # Показываем конфигурацию
    print("📊 Текущая конфигурация:")
    print(f"   API ключ: {api_config.gemini_key[:20]}..." if api_config.gemini_key else "   API ключ: ❌ Не установлен")
    print(f"   Модель: {api_config.gemini_model}")
    print()
    
    if not api_config.has_gemini():
        print("❌ GEMINI_API_KEY не установлен в .env")
        print("💡 Добавьте ключ в .env файл")
        return
    
    # Пробуем сделать минимальный запрос
    print("🧪 Тестовый запрос (минимальный)...")
    print()
    
    try:
        from google import genai
        
        client = genai.Client(api_key=api_config.gemini_key)
        
        # Минимальный промпт
        response = client.models.generate_content(
            model=api_config.gemini_model,
            contents="Hi"
        )
        
        print("✅ УСПЕШНО!")
        print(f"🤖 Ответ: {response.text[:100]}")
        print()
        print("="*80)
        print("✅ API работает! Квота в норме.".center(80))
        print("="*80)
        
    except Exception as e:
        error_str = str(e)
        print(f"❌ ОШИБКА: {error_str[:200]}")
        print()
        
        # Анализируем ошибку
        if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
            print("="*80)
            print("⚠️  КВОТА ИСЧЕРПАНА".center(80))
            print("="*80)
            print()
            print("📊 Лимиты Free Tier:")
            print("   • 15 запросов в минуту")
            print("   • 1,500 запросов в день")
            print("   • 1 миллион токенов в день")
            print()
            print("💡 Решения:")
            print()
            print("1. ⏰ Подожди:")
            print("   • Если превышен лимит в минуту → подожди 60 секунд")
            print("   • Если превышен дневной лимит → подожди до завтра")
            print()
            print("2. 🔑 Получи новый API ключ:")
            print("   • https://makersuite.google.com/app/apikey")
            print("   • Обнови в .env: GEMINI_API_KEY=new-key")
            print()
            print("3. 💰 Перейди на платный план:")
            print("   • https://ai.google.dev/pricing")
            print("   • Больше запросов и токенов")
            print()
            
        elif "503" in error_str or "UNAVAILABLE" in error_str:
            print("="*80)
            print("⚠️  МОДЕЛЬ ПЕРЕГРУЖЕНА".center(80))
            print("="*80)
            print()
            print("💡 Решения:")
            print()
            print("1. ⏰ Подожди 30-60 секунд и попробуй снова")
            print()
            print("2. 🔄 Смени модель в .env:")
            print("   GEMINI_MODEL=gemini-2.0-flash      # Стабильная")
            print("   # GEMINI_MODEL=gemini-2.5-flash    # Новая")
            print("   # GEMINI_MODEL=gemini-1.5-flash    # Старая")
            print()
            
        elif "404" in error_str or "NOT_FOUND" in error_str:
            print("="*80)
            print("⚠️  МОДЕЛЬ НЕ НАЙДЕНА".center(80))
            print("="*80)
            print()
            print("💡 Проверь имя модели в .env:")
            print(f"   Текущая: {api_config.gemini_model}")
            print()
            print("   Правильные имена:")
            print("   • gemini-2.5-flash")
            print("   • gemini-2.0-flash")
            print("   • gemini-1.5-flash")
            print()
            
        else:
            print("="*80)
            print("❌ НЕИЗВЕСТНАЯ ОШИБКА".center(80))
            print("="*80)
            print()
            print("💡 Проверь:")
            print("   1. API ключ корректный")
            print("   2. Есть интернет")
            print("   3. Модель существует")
            print()

if __name__ == "__main__":
    check_quota()
