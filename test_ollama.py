#!/usr/bin/env python3
"""
Быстрый тест Ollama + EasyOCR
"""
import requests
import time

def test_ollama():
    """Тест Ollama API"""
    print("\n🧠 Тест Ollama (Llama2)...")
    
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                'model': 'llama2',
                'prompt': 'Ответь коротко на комментарий: "Отличное видео!"',
                'stream': False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()['response'].strip()
            print(f"✅ Ollama работает!")
            print(f"💬 Ответ: {result}")
            return True
        else:
            print(f"❌ Ошибка: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"❌ Ошибка подключения к Ollama: {e}")
        print("⚠️  Убедись что Ollama сервер запущен: ollama serve")
        return False

def test_easyocr():
    """Тест EasyOCR"""
    print("\n📖 Тест EasyOCR...")
    
    try:
        import easyocr
        print("✅ EasyOCR импортирован")
        
        print("⏳ Инициализация EasyOCR (RU + EN)...")
        reader = easyocr.Reader(['ru', 'en'], gpu=False)
        print("✅ EasyOCR готов к работе!")
        return True
    
    except ImportError:
        print("❌ EasyOCR не установлен")
        print("Установи: pip install easyocr")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def main():
    print("="*60)
    print("🧪 Тест компонентов TikTok Comment Bot")
    print("="*60)
    
    # Тест Ollama
    ollama_ok = test_ollama()
    
    # Тест EasyOCR
    easyocr_ok = test_easyocr()
    
    # Итог
    print("\n" + "="*60)
    print("📊 Результаты:")
    print("="*60)
    print(f"  Ollama (LLM): {'✅ OK' if ollama_ok else '❌ FAIL'}")
    print(f"  EasyOCR (OCR): {'✅ OK' if easyocr_ok else '❌ FAIL'}")
    
    if ollama_ok and easyocr_ok:
        print("\n🎉 Все компоненты готовы к работе!")
        print("\n🚀 Запуск бота:")
        print("   python3 tiktok_comment_bot.py")
        print("   или")
        print("   ./run_comment_bot.sh")
    else:
        print("\n⚠️  Некоторые компоненты не работают")

if __name__ == '__main__':
    main()
