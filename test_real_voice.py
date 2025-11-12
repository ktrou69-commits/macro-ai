#!/usr/bin/env python3
"""
Тест реального голосового ввода с микрофоном
"""

import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_microphone():
    """Тест микрофона"""
    print("🎤 Тестирование микрофона...")
    
    try:
        import speech_recognition as sr
        
        # Создаем распознаватель
        r = sr.Recognizer()
        
        # Получаем список микрофонов
        print("🎧 Доступные микрофоны:")
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print(f"   {index}: {name}")
        
        # Тестируем запись
        with sr.Microphone() as source:
            print("🔧 Настройка микрофона...")
            r.adjust_for_ambient_noise(source, duration=1)
            print("✅ Микрофон готов!")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка микрофона: {e}")
        return False

def test_tts():
    """Тест синтеза речи"""
    print("\n🔊 Тестирование синтеза речи...")
    
    try:
        import pyttsx3
        
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        
        print("🗣️ Доступные голоса:")
        for i, voice in enumerate(voices):
            print(f"   {i}: {voice.name} ({voice.languages})")
        
        # Тестируем произношение
        print("🔊 Произношу тестовую фразу...")
        engine.say("Привет! Голосовой ассистент работает!")
        engine.runAndWait()
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка TTS: {e}")
        return False

def test_voice_recognition():
    """Тест распознавания речи"""
    print("\n🎤 Тестирование распознавания речи...")
    
    try:
        import speech_recognition as sr
        
        r = sr.Recognizer()
        
        print("🎤 Говорите что-нибудь (5 секунд)...")
        
        with sr.Microphone() as source:
            # Настройка микрофона
            r.adjust_for_ambient_noise(source, duration=1)
            print("🔴 Запись...")
            
            # Записываем аудио
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            print("⏹️ Запись завершена")
        
        print("🧠 Распознавание...")
        
        # Пробуем Google Speech Recognition
        try:
            text = r.recognize_google(audio, language='ru-RU')
            print(f"✅ Google распознал: '{text}'")
            return True
        except sr.UnknownValueError:
            print("❌ Google не смог распознать речь")
        except sr.RequestError as e:
            print(f"❌ Ошибка Google API: {e}")
        
        return False
        
    except Exception as e:
        print(f"❌ Ошибка распознавания: {e}")
        return False

def test_full_voice_assistant():
    """Тест полного голосового ассистента"""
    print("\n🤖 Тестирование полного голосового ассистента...")
    
    try:
        from src.voice.voice_assistant import VoiceAssistant
        
        # Создаем ассистента с реальными движками
        assistant = VoiceAssistant(
            recognition_engine="google",  # Реальное распознавание
            tts_engine="pyttsx3"         # Реальный TTS
        )
        
        print("✅ Голосовой ассистент инициализирован")
        print("🎤 Скажите: 'Окей ассистент, привет!'")
        print("⏱️ Ожидание 10 секунд...")
        
        # Запускаем прослушивание
        assistant.start()
        
        # Ждем 10 секунд
        import time
        time.sleep(10)
        
        # Останавливаем
        assistant.stop()
        
        print("✅ Тест завершен")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка голосового ассистента: {e}")
        return False

def main():
    """Главная функция тестирования"""
    print("🎤 ТЕСТИРОВАНИЕ РЕАЛЬНОГО ГОЛОСОВОГО ВВОДА")
    print("=" * 60)
    
    print("⚠️ ВАЖНО: Убедитесь что:")
    print("   • Микрофон подключен и работает")
    print("   • Разрешения на микрофон даны приложению")
    print("   • Звук включен для тестирования TTS")
    print()
    
    tests = [
        ("Микрофон", test_microphone),
        ("Синтез речи", test_tts),
        ("Распознавание речи", test_voice_recognition),
        ("Полный голосовой ассистент", test_full_voice_assistant)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except KeyboardInterrupt:
            print(f"\n⏹️ Тест '{test_name}' прерван пользователем")
            results.append((test_name, False))
            break
        except Exception as e:
            print(f"❌ Неожиданная ошибка в '{test_name}': {e}")
            results.append((test_name, False))
    
    # Итоги
    print(f"\n{'='*60}")
    print("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🏆 Итого: {passed}/{len(results)} тестов пройдено")
    
    if passed == len(results):
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ! Голосовой ввод готов к использованию!")
    else:
        print("⚠️ Некоторые тесты провалены. Проверьте настройки системы.")

if __name__ == "__main__":
    main()
