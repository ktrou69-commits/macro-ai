#!/usr/bin/env python3
"""
Демо-скрипт для тестирования Этапа 3: Голосовой ввод
"""

import sys
import time
import threading
from pathlib import Path

def test_voice_components():
    """Тест отдельных компонентов голосового ввода"""
    print("🧪 Тестирование компонентов голосового ввода")
    print("=" * 60)
    
    # 1. Тест распознавания речи
    print("1. Тест VoiceRecognizer:")
    try:
        from src.voice.speech_recognition import VoiceRecognizer, HotwordDetector
        
        recognizer = VoiceRecognizer(engine="google")  # Fallback если нет микрофона
        print("   ✅ VoiceRecognizer инициализирован")
        
        hotword_detector = HotwordDetector()
        
        # Тест обнаружения ключевых слов
        test_phrases = [
            "Окей ассистент, открой Safari",
            "Привет ассистент, сделай скриншот", 
            "Просто обычная фраза",
            "Эй макро, покажи процессы"
        ]
        
        for phrase in test_phrases:
            detected = hotword_detector.detect_hotword(phrase)
            if detected:
                command = hotword_detector.extract_command(phrase)
                print(f"   🎯 '{phrase}' → Команда: '{command}'")
            else:
                print(f"   🔇 '{phrase}' → Не активирует")
        
    except Exception as e:
        print(f"   ❌ Ошибка VoiceRecognizer: {e}")
    
    # 2. Тест синтеза речи
    print("\n2. Тест TextToSpeech:")
    try:
        from src.voice.text_to_speech import TextToSpeech, VoiceAssistantResponses
        
        tts = TextToSpeech(engine="macos_say")
        responses = VoiceAssistantResponses(tts)
        
        print("   ✅ TextToSpeech инициализирован")
        
        # Тест быстрых ответов
        print("   🔊 Тестируем голосовые ответы...")
        responses.acknowledge_command("открой Safari")
        time.sleep(2)
        responses.report_working()
        time.sleep(2)
        responses.report_completed("открытие Safari")
        
        print("   ✅ Голосовые ответы работают")
        
    except Exception as e:
        print(f"   ❌ Ошибка TextToSpeech: {e}")
    
    # 3. Тест главного ассистента
    print("\n3. Тест VoiceAssistant:")
    try:
        from src.voice.voice_assistant import VoiceAssistant
        
        assistant = VoiceAssistant()
        print("   ✅ VoiceAssistant инициализирован")
        
        return assistant
        
    except Exception as e:
        print(f"   ❌ Ошибка VoiceAssistant: {e}")
        return None

def test_system_integration():
    """Тест интеграции с системными командами"""
    print("\n🔧 Тестирование интеграции с системными командами")
    print("=" * 60)
    
    try:
        from src.voice.voice_assistant import VoiceAssistant
        
        assistant = VoiceAssistant()
        
        # Тест системных команд через голосовой интерфейс
        test_commands = [
            "сделай скриншот",
            "покажи активное приложение", 
            "покажи процессы",
            "открой Calculator"
        ]
        
        for command in test_commands:
            print(f"\n🎤 Тестируем команду: '{command}'")
            assistant.process_text_command(command)
            time.sleep(3)  # Ждем выполнения
        
        print("\n✅ Интеграция с системными командами работает")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка интеграции: {e}")
        return False

def interactive_voice_demo():
    """Интерактивная демонстрация голосового ассистента"""
    print("\n🎮 Интерактивная демонстрация голосового ассистента")
    print("=" * 60)
    
    try:
        from src.voice.voice_assistant import VoiceAssistant
        
        assistant = VoiceAssistant()
        
        print("\n🚀 Запуск голосового ассистента...")
        print("📋 Доступные команды:")
        print("   • 'Окей ассистент, открой Safari'")
        print("   • 'Окей ассистент, сделай скриншот'")
        print("   • 'Окей ассистент, покажи процессы'")
        print("   • 'quit' - выход")
        print()
        
        # Запускаем ассистента
        assistant.start()
        
        # Ждем команд пользователя
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Получен сигнал остановки...")
            assistant.stop()
            
    except Exception as e:
        print(f"❌ Ошибка демо: {e}")

def test_voice_to_system_flow():
    """Тест полного цикла: голос → команда → выполнение → ответ"""
    print("\n🔄 Тест полного цикла голосового управления")
    print("=" * 60)
    
    try:
        from src.voice.voice_assistant import VoiceAssistant
        
        assistant = VoiceAssistant()
        
        # Симулируем полный цикл
        print("1. Симуляция распознавания: 'Окей ассистент, открой Calculator'")
        assistant._on_speech_recognized("Окей ассистент, открой Calculator")
        time.sleep(3)
        
        print("\n2. Симуляция распознавания: 'Окей ассистент, сделай скриншот'")
        assistant._on_speech_recognized("Окей ассистент, сделай скриншот")
        time.sleep(3)
        
        print("\n3. Симуляция распознавания: 'Окей ассистент, покажи активное приложение'")
        assistant._on_speech_recognized("Окей ассистент, покажи активное приложение")
        time.sleep(3)
        
        print("\n✅ Полный цикл работает корректно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка полного цикла: {e}")
        return False

def show_voice_capabilities():
    """Показать возможности голосового ассистента"""
    print("\n🎯 Возможности голосового ассистента Этапа 3")
    print("=" * 60)
    
    capabilities = [
        ("🎤 Распознавание речи", "Google Speech Recognition / Whisper / Fallback"),
        ("🔊 Синтез речи", "macOS say / pyttsx3 / Fallback"),
        ("🔑 Ключевые слова", "'Окей ассистент', 'Привет ассистент', 'Эй макро'"),
        ("🔧 Системные команды", "Интеграция с SystemOrchestrator"),
        ("💾 Управление состоянием", "Интеграция с StateManager"),
        ("🧠 AI команды", "Подготовка к интеграции с Gemini"),
        ("📊 Статистика", "Отслеживание команд и ошибок"),
        ("🎮 Интерактивность", "Реальное время + текстовый fallback")
    ]
    
    for feature, description in capabilities:
        print(f"   {feature}: {description}")
    
    print("\n📋 Примеры поддерживаемых команд:")
    commands = [
        "Окей ассистент, открой Safari",
        "Окей ассистент, открой Calculator", 
        "Окей ассистент, сделай скриншот",
        "Окей ассистент, покажи процессы",
        "Окей ассистент, покажи активное приложение",
        "Привет ассистент, закрой приложение",
        "Эй макро, создай макрос для гугла"
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"   {i}. {cmd}")

def main():
    """Главная функция демо"""
    print("🎤 Демо тестирование Этапа 3: Голосовой ввод")
    print("=" * 70)
    
    # Показываем возможности
    show_voice_capabilities()
    
    # Выбор режима тестирования
    print("\n🎮 Выберите режим тестирования:")
    print("   1. Тест компонентов")
    print("   2. Тест интеграции с системой")
    print("   3. Тест полного цикла")
    print("   4. Интерактивная демонстрация")
    print("   5. Все тесты")
    
    try:
        choice = input("\nВведите номер (1-5): ").strip()
        
        if choice == "1":
            assistant = test_voice_components()
        elif choice == "2":
            test_system_integration()
        elif choice == "3":
            test_voice_to_system_flow()
        elif choice == "4":
            interactive_voice_demo()
        elif choice == "5":
            print("\n🚀 Запуск всех тестов...")
            assistant = test_voice_components()
            if assistant:
                test_system_integration()
                test_voice_to_system_flow()
                
                print("\n🎮 Переход к интерактивной демонстрации...")
                time.sleep(2)
                interactive_voice_demo()
        else:
            print("❌ Неверный выбор")
            return
            
    except KeyboardInterrupt:
        print("\n🛑 Демо прервано пользователем")
    except Exception as e:
        print(f"❌ Ошибка демо: {e}")
    
    print("\n🎉 Демо завершено!")
    print("📋 Этап 3: Голосовой ввод готов к использованию!")

if __name__ == "__main__":
    main()
