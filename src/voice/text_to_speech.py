#!/usr/bin/env python3
"""
text_to_speech.py
Система синтеза речи для ответов ИИ
"""

import subprocess
import threading
import queue
import time
from typing import Optional, Dict, Any
from pathlib import Path

# Проверяем доступность модулей
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    print("ℹ️ pyttsx3 недоступен (опционально). Установите: pip install pyttsx3")


class TextToSpeech:
    """Система синтеза речи"""
    
    def __init__(self, engine: str = "macos_say", voice: str = "Milena"):
        self.engine = engine
        self.voice = voice
        self.is_speaking = False
        self.speech_queue = queue.Queue()
        
        # Инициализация движка
        if engine == "pyttsx3" and PYTTSX3_AVAILABLE:
            try:
                self.tts_engine = pyttsx3.init()
                self._setup_pyttsx3()
                print("✅ pyttsx3 TTS инициализирован")
            except Exception as e:
                print(f"⚠️ Ошибка инициализации pyttsx3: {e}")
                self.engine = "macos_say"  # Fallback
        
        if engine == "macos_say" or not PYTTSX3_AVAILABLE:
            # Проверяем доступность macOS say
            try:
                result = subprocess.run(['say', '--version'], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=5)
                if result.returncode == 0:
                    print("✅ macOS say TTS инициализирован")
                else:
                    print("⚠️ macOS say недоступен, используется fallback")
                    self.engine = "fallback"
            except Exception:
                print("⚠️ macOS say недоступен, используется fallback")
                self.engine = "fallback"
        
        # Запускаем поток для обработки очереди речи
        self.speech_thread = threading.Thread(
            target=self._speech_worker,
            daemon=True
        )
        self.speech_thread.start()
        
        print(f"🔊 TTS готов: {self.engine}")
    
    def _setup_pyttsx3(self):
        """Настройка pyttsx3"""
        try:
            # Настройка голоса
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if 'ru' in voice.id.lower() or 'russian' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
            
            # Настройка скорости и громкости
            self.tts_engine.setProperty('rate', 180)  # Слова в минуту
            self.tts_engine.setProperty('volume', 0.8)  # Громкость 0-1
            
        except Exception as e:
            print(f"⚠️ Ошибка настройки pyttsx3: {e}")
    
    def speak(self, text: str, priority: str = "normal") -> bool:
        """
        Произнести текст
        
        Args:
            text: Текст для произношения
            priority: Приоритет ("high", "normal", "low")
        """
        if not text.strip():
            return False
        
        # Добавляем в очередь
        self.speech_queue.put({
            'text': text,
            'priority': priority,
            'timestamp': self._get_timestamp()
        })
        
        print(f"🔊 Добавлено в очередь речи: '{text[:50]}...' (приоритет: {priority})")
        return True
    
    def speak_immediately(self, text: str) -> bool:
        """Произнести текст немедленно (прерывая текущую речь)"""
        print(f"🚨 Немедленное произношение: '{text}'")
        
        # Очищаем очередь
        while not self.speech_queue.empty():
            try:
                self.speech_queue.get_nowait()
            except queue.Empty:
                break
        
        # Останавливаем текущую речь
        self.stop_speaking()
        
        # Добавляем с высоким приоритетом
        return self.speak(text, priority="high")
    
    def stop_speaking(self):
        """Остановить текущую речь"""
        if self.engine == "macos_say":
            try:
                subprocess.run(['killall', 'say'], 
                             capture_output=True, 
                             check=False,
                             timeout=2)
            except Exception:
                pass
        elif self.engine == "pyttsx3" and PYTTSX3_AVAILABLE:
            try:
                self.tts_engine.stop()
            except Exception:
                pass
        
        self.is_speaking = False
        print("🔇 Речь остановлена")
    
    def _speech_worker(self):
        """Рабочий поток для обработки очереди речи"""
        while True:
            try:
                # Ждем элемент из очереди
                speech_item = self.speech_queue.get(timeout=1)
                
                if speech_item:
                    self._execute_speech(speech_item['text'])
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"⚠️ Ошибка в speech worker: {e}")
    
    def _execute_speech(self, text: str):
        """Выполнить синтез речи"""
        try:
            self.is_speaking = True
            print(f"🗣️ Произношу: '{text}'")
            
            if self.engine == "macos_say":
                self._speak_with_say(text)
            elif self.engine == "fallback":
                return self._fallback_speak(text)
            elif self.engine == "pyttsx3":
                self._speak_with_pyttsx3(text)
            else:
                self._fallback_speak(text)
            
        except Exception as e:
            print(f"⚠️ Ошибка синтеза речи: {e}")
        finally:
            self.is_speaking = False
    
    def _speak_with_say(self, text: str):
        """Синтез речи через macOS say"""
        try:
            cmd = ['say', '-v', self.voice, text]
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=30)
            
            if result.returncode != 0:
                print(f"⚠️ Ошибка say: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("⚠️ Таймаут синтеза речи")
        except Exception as e:
            print(f"⚠️ Ошибка say команды: {e}")
    
    def _speak_with_pyttsx3(self, text: str):
        """Синтез речи через pyttsx3"""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"⚠️ Ошибка pyttsx3: {e}")
    
    def _fallback_speak(self, text: str, priority: str = "normal") -> bool:
        """Fallback произношение через print и системный say если доступен"""
        print(f"🔊 [FALLBACK TTS] Произношу: '{text}'")
        
        # Пытаемся использовать системный say на macOS
        try:
            import subprocess
            import os
            
            # Проверяем, доступен ли say
            if os.system("which say > /dev/null 2>&1") == 0:
                # Используем say для реального произношения
                subprocess.run(['say', text], check=False, capture_output=True)
                print(f"🔊 [macOS say] Произнес: '{text}'")
            
        except Exception:
            # Если say недоступен, просто выводим в консоль
            pass
            
        return True
    
    def get_available_voices(self) -> list:
        """Получить список доступных голосов"""
        voices = []
        
        if self.engine == "macos_say":
            try:
                result = subprocess.run(['say', '-v', '?'], 
                                      capture_output=True, 
                                      text=True,
                                      timeout=10)
                
                for line in result.stdout.split('\n'):
                    if line.strip():
                        voice_name = line.split()[0]
                        voices.append(voice_name)
                        
            except Exception as e:
                print(f"⚠️ Ошибка получения голосов: {e}")
                
        elif self.engine == "pyttsx3" and PYTTSX3_AVAILABLE:
            try:
                engine_voices = self.tts_engine.getProperty('voices')
                voices = [voice.name for voice in engine_voices]
            except Exception as e:
                print(f"⚠️ Ошибка получения голосов pyttsx3: {e}")
        
        return voices
    
    def set_voice(self, voice_name: str) -> bool:
        """Установить голос"""
        try:
            self.voice = voice_name
            
            if self.engine == "pyttsx3" and PYTTSX3_AVAILABLE:
                voices = self.tts_engine.getProperty('voices')
                for voice in voices:
                    if voice_name in voice.name:
                        self.tts_engine.setProperty('voice', voice.id)
                        print(f"✅ Голос изменен на: {voice_name}")
                        return True
            
            print(f"✅ Голос установлен: {voice_name}")
            return True
            
        except Exception as e:
            print(f"⚠️ Ошибка установки голоса: {e}")
            return False
    
    def _get_timestamp(self) -> str:
        """Получить текущий timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()


# Предустановленные фразы для быстрых ответов
QUICK_RESPONSES = {
    'acknowledgment': [
        "Да сэр",
        "Конечно", 
        "Выполняю",
        "Понял",
        "Сейчас сделаю"
    ],
    'working': [
        "Работаю над этим",
        "Сейчас минуту", 
        "Обрабатываю запрос",
        "Выполняю команду"
    ],
    'completed': [
        "Готово",
        "Выполнено",
        "Задача завершена", 
        "Сделано"
    ],
    'error': [
        "Произошла ошибка",
        "Не удалось выполнить",
        "Возникла проблема"
    ],
    'opening': [
        "Да сэр, открываю",
        "Конечно, запускаю", 
        "Сейчас открою"
    ]
}


class VoiceAssistantResponses:
    """Помощник для генерации голосовых ответов"""
    
    def __init__(self, tts: TextToSpeech):
        self.tts = tts
    
    def acknowledge_command(self, command: str = None):
        """Подтвердить получение команды"""
        import random
        
        if command:
            command_lower = command.lower()
            if any(word in command_lower for word in ['открой', 'запусти', 'открыть', 'запустить']):
                responses = QUICK_RESPONSES['opening']
            else:
                responses = QUICK_RESPONSES['acknowledgment']
        else:
            responses = QUICK_RESPONSES['acknowledgment']
        
        response = random.choice(responses)
        self.tts.speak_immediately(response)
    
    def report_working(self):
        """Сообщить о работе"""
        import random
        response = random.choice(QUICK_RESPONSES['working'])
        self.tts.speak(response)
    
    def report_completed(self, task: str = None):
        """Сообщить о завершении"""
        import random
        
        if task:
            response = f"Задача {task} выполнена"
        else:
            response = random.choice(QUICK_RESPONSES['completed'])
        
        self.tts.speak(response)
    
    def report_error(self, error: str = None):
        """Сообщить об ошибке"""
        import random
        
        if error:
            response = f"Ошибка: {error}"
        else:
            response = random.choice(QUICK_RESPONSES['error'])
        
        self.tts.speak(response, priority="high")
    
    def say_custom(self, text: str, immediate: bool = False):
        """Произнести произвольный текст"""
        if immediate:
            self.tts.speak_immediately(text)
        else:
            self.tts.speak(text)


# Глобальные экземпляры для удобства
text_to_speech = TextToSpeech()
voice_responses = VoiceAssistantResponses(text_to_speech)
