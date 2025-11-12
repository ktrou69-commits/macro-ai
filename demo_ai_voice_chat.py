#!/usr/bin/env python3
"""
Демо AI голосового чата с Gemini
"""

import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_ai_chat():
    """Тест AI чата"""
    print("🤖 Демо AI голосового чата с Gemini")
    print("=" * 50)
    
    try:
        from src.voice.ai_voice_integration import ai_assistant
        
        if not ai_assistant.is_available():
            print("❌ AI недоступен. Проверьте:")
            print("1. pip install google-generativeai python-dotenv")
            print("2. Добавьте GEMINI_API_KEY в .env файл")
            return
        
        print("✅ AI ассистент готов к общению!")
        print("💡 Примеры команд:")
        print("   • Привет! Как дела?")
        print("   • Открой Safari")
        print("   • Сделай скриншот")
        print("   • Создай макрос для открытия гугла")
        print("   • Покажи активное приложение")
        print()
        
        while True:
            try:
                user_input = input("👤 Вы: ").strip()
                
                if user_input.lower() in ['quit', 'выход', 'пока']:
                    print("👋 До свидания!")
                    break
                
                if not user_input:
                    continue
                
                # Обрабатываем через AI
                result = ai_assistant.process_voice_message(user_input)
                
                print(f"🤖 Ассистент: {result['response']}")
                
                # Показываем дополнительную информацию
                if result['action'] != 'chat':
                    print(f"🔧 Действие: {result['action']}")
                    if result.get('command'):
                        print(f"⚙️ Команда: {result['command']}")
                    if result.get('macro_request'):
                        print(f"📝 Макрос: {result['macro_request']}")
                
                print()
                
            except KeyboardInterrupt:
                print("\n👋 До свидания!")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        print("Установите зависимости: pip install google-generativeai python-dotenv")

def test_voice_assistant_with_ai():
    """Тест голосового ассистента с AI"""
    print("\n🎤 Тест голосового ассистента с AI интеграцией")
    print("=" * 50)
    
    try:
        from src.voice.voice_assistant import VoiceAssistant
        
        # Создаем ассистента в fallback режиме
        assistant = VoiceAssistant(
            recognition_engine="fallback",
            tts_engine="fallback"
        )
        
        print("✅ Голосовой ассистент с AI готов!")
        print("💡 Попробуйте команды с 'Окей ассистент':")
        print()
        
        test_commands = [
            "Окей ассистент, привет! Как дела?",
            "Окей ассистент, открой Safari", 
            "Окей ассистент, сделай скриншот",
            "Окей ассистент, что ты умеешь?",
            "Окей ассистент, создай макрос для открытия гугла"
        ]
        
        for command in test_commands:
            print(f"👤 Тест команды: {command}")
            assistant.process_text_command(command)
            print()
            
            # Небольшая пауза для чтения
            import time
            time.sleep(1)
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def main():
    """Главная функция"""
    print("🤖 AI Голосовой Ассистент - Демо")
    print("=" * 60)
    
    print("Выберите режим:")
    print("1. AI чат (текстовое общение)")
    print("2. Голосовой ассистент с AI (тест команд)")
    print("3. Оба режима")
    
    try:
        choice = input("\nВведите номер (1-3): ").strip()
        
        if choice == "1":
            test_ai_chat()
        elif choice == "2":
            test_voice_assistant_with_ai()
        elif choice == "3":
            test_ai_chat()
            test_voice_assistant_with_ai()
        else:
            print("❌ Неверный выбор")
            
    except KeyboardInterrupt:
        print("\n👋 До свидания!")

if __name__ == "__main__":
    main()
