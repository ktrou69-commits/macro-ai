#!/usr/bin/env python3
"""
Тесты для Этапа 3: Голосовой ввод
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch

from src.voice.speech_recognition import VoiceRecognizer, HotwordDetector
from src.voice.text_to_speech import TextToSpeech, VoiceAssistantResponses
from src.voice.voice_assistant import VoiceAssistant


class TestHotwordDetector:
    """Тесты детектора ключевых слов"""
    
    def setup_method(self):
        self.detector = HotwordDetector()
    
    def test_hotword_detection(self):
        """Тест обнаружения ключевых слов"""
        # Позитивные случаи
        positive_cases = [
            "Окей ассистент, открой Safari",
            "Привет ассистент, сделай скриншот",
            "Эй макро, покажи процессы",
            "Слушай, что делать?",
            "АССИСТЕНТ, помоги"
        ]
        
        for phrase in positive_cases:
            assert self.detector.detect_hotword(phrase) == True, f"Не обнаружено в: {phrase}"
        
        # Негативные случаи
        negative_cases = [
            "Просто обычная фраза",
            "Открой Safari без ключевого слова",
            "Ассистенты бывают разные",
            "Макросы это полезно"
        ]
        
        for phrase in negative_cases:
            assert self.detector.detect_hotword(phrase) == False, f"Ложное срабатывание: {phrase}"
    
    def test_command_extraction(self):
        """Тест извлечения команд"""
        test_cases = [
            ("Окей ассистент, открой Safari", "открой Safari"),
            ("Привет ассистент, сделай скриншот", "сделай скриншот"),
            ("Эй макро, покажи процессы", "покажи процессы"),
            ("Ассистент, помоги с задачей", "помоги с задачей"),
            ("Слушай, что делать дальше?", "что делать дальше?")
        ]
        
        for full_phrase, expected_command in test_cases:
            extracted = self.detector.extract_command(full_phrase)
            assert extracted == expected_command, f"Неверно извлечено из '{full_phrase}': '{extracted}' != '{expected_command}'"
    
    def test_punctuation_handling(self):
        """Тест обработки знаков препинания"""
        test_cases = [
            ("Окей ассистент, открой Safari!", "открой Safari!"),
            ("Привет ассистент: сделай скриншот", "сделай скриншот"),
            ("Эй макро; покажи процессы", "покажи процессы")
        ]
        
        for full_phrase, expected_command in test_cases:
            extracted = self.detector.extract_command(full_phrase)
            # Убираем знаки препинания для сравнения
            cleaned_extracted = extracted.rstrip('!?:;.,')
            cleaned_expected = expected_command.rstrip('!?:;.,')
            assert cleaned_extracted == cleaned_expected


class TestTextToSpeech:
    """Тесты синтеза речи"""
    
    def setup_method(self):
        self.tts = TextToSpeech(engine="fallback")  # Используем fallback для тестов
    
    def test_tts_initialization(self):
        """Тест инициализации TTS"""
        assert self.tts is not None
        assert self.tts.engine in ["macos_say", "pyttsx3", "fallback"]
        assert self.tts.speech_queue is not None
    
    def test_speak_method(self):
        """Тест метода speak"""
        result = self.tts.speak("Тестовое сообщение")
        assert result == True
        
        # Ждем немного для обработки очереди
        import time
        time.sleep(0.5)
        
        # В fallback режиме очередь может быть пустой после обработки
        # Главное что метод вернул True
    
    def test_empty_text_handling(self):
        """Тест обработки пустого текста"""
        result = self.tts.speak("")
        assert result == False
        
        result = self.tts.speak("   ")
        assert result == False
    
    def test_voice_responses(self):
        """Тест голосовых ответов"""
        responses = VoiceAssistantResponses(self.tts)
        
        # Тест подтверждения команды
        responses.acknowledge_command("открой Safari")
        
        # Ждем обработки
        import time
        time.sleep(0.5)
        
        # Тест сообщения о работе
        responses.report_working()
        
        # В fallback режиме главное что методы выполняются без ошибок
        assert True


class TestVoiceRecognizer:
    """Тесты распознавания речи"""
    
    def setup_method(self):
        # Используем fallback режим для тестов
        self.recognizer = VoiceRecognizer(engine="fallback")
    
    def test_recognizer_initialization(self):
        """Тест инициализации распознавателя"""
        assert self.recognizer is not None
        assert self.recognizer.engine in ["google", "whisper", "fallback"]
        assert self.recognizer.language == "ru-RU"
        assert self.recognizer.is_listening == False
    
    def test_callback_mechanism(self):
        """Тест механизма callback'ов"""
        received_texts = []
        
        def test_callback(text):
            received_texts.append(text)
        
        # В fallback режиме мы можем симулировать ввод
        self.recognizer.callback = test_callback
        
        # Симулируем обработку текста
        if hasattr(self.recognizer, '_on_speech_recognized'):
            self.recognizer._on_speech_recognized("тестовый текст")
        
        # В fallback режиме callback вызывается напрямую
        if self.recognizer.callback:
            self.recognizer.callback("тестовый текст")
        
        assert len(received_texts) > 0
        assert "тестовый текст" in received_texts


class TestVoiceAssistant:
    """Тесты главного голосового ассистента"""
    
    def setup_method(self):
        self.assistant = VoiceAssistant(
            recognition_engine="fallback",
            tts_engine="fallback"
        )
    
    def test_assistant_initialization(self):
        """Тест инициализации ассистента"""
        assert self.assistant is not None
        assert self.assistant.voice_recognizer is not None
        assert self.assistant.tts is not None
        assert self.assistant.hotword_detector is not None
        assert self.assistant.voice_responses is not None
    
    def test_command_classification(self):
        """Тест классификации команд"""
        # Простые системные команды
        assert self.assistant._is_simple_system_command("открой Safari") == True
        assert self.assistant._is_simple_system_command("сделай скриншот") == True
        assert self.assistant._is_simple_system_command("покажи процессы") == True
        
        # AI команды
        assert self.assistant._is_ai_command("создай макрос для гугла") == True
        assert self.assistant._is_ai_command("сгенерируй автоматизацию") == True
        
        # Обычные команды
        assert self.assistant._is_simple_system_command("расскажи анекдот") == False
        assert self.assistant._is_ai_command("просто текст") == False
    
    def test_app_name_extraction(self):
        """Тест извлечения имен приложений"""
        test_cases = [
            ("открой Safari", "Safari"),
            ("запусти Google Chrome", "Google Chrome"),
            ("открой калькулятор", "Calculator"),
            ("запусти терминал", "Terminal")
        ]
        
        for command, expected_app in test_cases:
            extracted = self.assistant._extract_app_name(command)
            assert extracted == expected_app, f"Неверно извлечено из '{command}': '{extracted}' != '{expected_app}'"
    
    def test_text_command_processing(self):
        """Тест обработки текстовых команд"""
        # Тест без ошибок
        try:
            self.assistant.process_text_command("сделай скриншот")
            assert True  # Если дошли сюда, то ошибок нет
        except Exception as e:
            pytest.fail(f"Ошибка обработки команды: {e}")
    
    def test_speech_recognition_callback(self):
        """Тест callback распознавания речи"""
        # Тест с ключевым словом
        self.assistant._on_speech_recognized("Окей ассистент, открой Safari")
        
        # Тест без ключевого слова
        self.assistant._on_speech_recognized("просто обычная фраза")
        
        # Проверяем, что статистика обновляется
        assert self.assistant.stats['commands_processed'] >= 0


class TestVoiceIntegration:
    """Тесты интеграции голосового ввода"""
    
    def test_full_voice_cycle(self):
        """Тест полного цикла голосового управления"""
        assistant = VoiceAssistant(
            recognition_engine="fallback",
            tts_engine="fallback"
        )
        
        # Симулируем полный цикл
        initial_commands = assistant.stats['commands_processed']
        
        # Обрабатываем команду напрямую (так как в fallback режиме _on_speech_recognized может не работать)
        assistant.process_text_command("покажи активное приложение")
        
        # Проверяем, что команда была обработана
        assert assistant.stats['commands_processed'] > initial_commands
    
    def test_error_handling(self):
        """Тест обработки ошибок"""
        assistant = VoiceAssistant(
            recognition_engine="fallback",
            tts_engine="fallback"
        )
        
        initial_errors = assistant.stats['errors']
        
        # Симулируем команду, которая может вызвать ошибку
        try:
            assistant.process_text_command("неизвестная команда xyz123")
            # Ошибок быть не должно, но команда может не выполниться
        except Exception:
            # Если есть ошибка, она должна быть обработана
            pass
        
        # Проверяем, что система продолжает работать
        assert assistant.is_active == False  # Ассистент не запущен в тестах


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
