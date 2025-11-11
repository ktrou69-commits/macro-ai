#!/usr/bin/env python3
"""
speech_recognition.py
Система распознавания речи с постоянным прослушиванием
"""

import threading
import queue
import time
import wave
from typing import Callable, Optional, Dict, Any
from pathlib import Path

# Проверяем доступность модулей
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("⚠️ SpeechRecognition недоступен. Установите: pip install SpeechRecognition")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    print("⚠️ PyAudio недоступен. Установите: pip install pyaudio")

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
    print("ℹ️ Whisper недоступен (опционально). Установите: pip install openai-whisper")


class VoiceRecognizer:
    """Система распознавания голоса"""
    
    def __init__(self, 
                 engine: str = "google",
                 language: str = "ru-RU"):
        
        self.engine = engine
        self.language = language
        self.is_listening = False
        self.callback = None
        
        # Настройки аудио
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.channels = 1
        
        # Инициализация движка
        if engine == "google" and SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Калибровка микрофона
            print("🎤 Калибровка микрофона...")
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print("✅ Google Speech Recognition инициализирован")
            
        elif engine == "whisper" and WHISPER_AVAILABLE:
            print("🔄 Загрузка Whisper модели...")
            self.whisper_model = whisper.load_model("base")
            print("✅ Whisper модель загружена")
            
        else:
            # Fallback режим - имитация для тестирования
            print("⚠️ Используется fallback режим (без реального распознавания)")
            self.fallback_mode = True
    
    def start_listening(self, callback: Callable[[str], None]):
        """Начать постоянное прослушивание"""
        if self.is_listening:
            print("⚠️ Прослушивание уже активно")
            return
            
        self.callback = callback
        self.is_listening = True
        
        # Запускаем поток прослушивания
        self.listen_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True
        )
        self.listen_thread.start()
        
        print("🎤 Начато прослушивание... (говорите после звукового сигнала)")
    
    def stop_listening(self):
        """Остановить прослушивание"""
        self.is_listening = False
        if hasattr(self, 'listen_thread'):
            self.listen_thread.join(timeout=2)
        print("🔇 Прослушивание остановлено")
    
    def _listen_loop(self):
        """Основной цикл прослушивания"""
        if hasattr(self, 'fallback_mode'):
            self._fallback_listen_loop()
        elif self.engine == "google":
            self._google_listen_loop()
        elif self.engine == "whisper":
            self._whisper_listen_loop()
    
    def _fallback_listen_loop(self):
        """Fallback режим для тестирования без микрофона"""
        print("🎤 Fallback режим активен. Введите команды через консоль:")
        
        while self.is_listening:
            try:
                # Имитируем ввод через консоль
                print("\n💬 Введите голосовую команду (или 'quit' для выхода):")
                user_input = input(">>> ")
                
                if user_input.lower() in ['quit', 'exit', 'стоп']:
                    self.stop_listening()
                    break
                
                if user_input.strip():
                    print(f"🎤 Имитация распознавания: '{user_input}'")
                    if self.callback:
                        self.callback(user_input)
                        
            except (KeyboardInterrupt, EOFError):
                self.stop_listening()
                break
            except Exception as e:
                print(f"⚠️ Ошибка в fallback режиме: {e}")
                time.sleep(1)
    
    def _google_listen_loop(self):
        """Цикл прослушивания с Google Speech Recognition"""
        if not SPEECH_RECOGNITION_AVAILABLE:
            print("❌ Google Speech Recognition недоступен")
            return
            
        print("🎤 Google Speech Recognition слушает...")
        
        while self.is_listening:
            try:
                # Слушаем аудио
                with self.microphone as source:
                    print("🔊 Говорите...")
                    audio = self.recognizer.listen(
                        source, 
                        timeout=1, 
                        phrase_time_limit=5
                    )
                
                print("🔄 Распознавание...")
                
                # Распознаем через Google
                text = self.recognizer.recognize_google(
                    audio, 
                    language=self.language
                )
                
                if text:
                    print(f"🎤 Распознано: '{text}'")
                    if self.callback:
                        self.callback(text)
                        
            except sr.WaitTimeoutError:
                # Таймаут - продолжаем слушать
                pass
            except sr.UnknownValueError:
                print("🤷 Не удалось распознать речь")
            except sr.RequestError as e:
                print(f"❌ Ошибка сервиса распознавания: {e}")
                time.sleep(5)  # Ждем перед повторной попыткой
            except Exception as e:
                print(f"⚠️ Ошибка распознавания: {e}")
                time.sleep(1)
    
    def _whisper_listen_loop(self):
        """Цикл прослушивания с Whisper (локально)"""
        if not WHISPER_AVAILABLE or not PYAUDIO_AVAILABLE:
            print("❌ Whisper или PyAudio недоступны")
            return
            
        try:
            # Настройка PyAudio
            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            print("🎤 Whisper слушает...")
            
            audio_buffer = []
            silence_threshold = 500
            silence_duration = 0
            max_silence = 30  # ~1 секунда тишины
            
            while self.is_listening:
                try:
                    # Читаем аудио данные
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    audio_buffer.append(data)
                    
                    # Проверяем уровень звука
                    audio_level = max(data) if data else 0
                    
                    if audio_level < silence_threshold:
                        silence_duration += 1
                    else:
                        silence_duration = 0
                    
                    # Если накопили достаточно аудио и есть пауза
                    if len(audio_buffer) > 50 and silence_duration > max_silence:
                        self._process_audio_buffer(audio_buffer)
                        audio_buffer = []
                        silence_duration = 0
                        
                except Exception as e:
                    print(f"⚠️ Ошибка чтения аудио: {e}")
                    time.sleep(0.1)
            
            # Закрываем поток
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
        except Exception as e:
            print(f"❌ Ошибка в Whisper цикле: {e}")
    
    def _process_audio_buffer(self, audio_buffer: list):
        """Обработка буфера аудио данных для Whisper"""
        try:
            # Сохраняем во временный файл
            temp_file = "/tmp/voice_input.wav"
            
            with wave.open(temp_file, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(audio_buffer))
            
            # Распознаем с помощью Whisper
            result = self.whisper_model.transcribe(
                temp_file, 
                language="ru"
            )
            
            text = result["text"].strip()
            
            if text and len(text) > 2:
                print(f"🎤 Whisper распознал: '{text}'")
                if self.callback:
                    self.callback(text)
            
            # Удаляем временный файл
            Path(temp_file).unlink(missing_ok=True)
            
        except Exception as e:
            print(f"⚠️ Ошибка обработки аудио: {e}")


class HotwordDetector:
    """Детектор ключевых слов для активации"""
    
    def __init__(self, hotwords: list = None):
        self.hotwords = hotwords or [
            "окей ассистент", 
            "привет ассистент", 
            "эй макро", 
            "слушай",
            "ассистент"
        ]
        self.is_active = False
        
        print(f"🔑 Ключевые слова: {', '.join(self.hotwords)}")
    
    def detect_hotword(self, text: str) -> bool:
        """Проверка наличия ключевого слова"""
        text_lower = text.lower().strip()
        
        for hotword in self.hotwords:
            if hotword.lower() in text_lower:
                # Проверяем, что это не часть другого слова
                hotword_pos = text_lower.find(hotword.lower())
                if hotword_pos >= 0:
                    # Проверяем границы слова
                    start_ok = hotword_pos == 0 or not text_lower[hotword_pos-1].isalpha()
                    end_pos = hotword_pos + len(hotword.lower())
                    end_ok = end_pos >= len(text_lower) or not text_lower[end_pos].isalpha()
                    
                    if start_ok and end_ok:
                        print(f"🎯 Обнаружено ключевое слово: '{hotword}'")
                        return True
        return False
    
    def extract_command(self, text: str) -> str:
        """Извлечение команды после ключевого слова"""
        text_lower = text.lower().strip()
        
        for hotword in self.hotwords:
            hotword_lower = hotword.lower()
            if hotword_lower in text_lower:
                # Находим позицию после ключевого слова
                pos = text_lower.find(hotword_lower) + len(hotword_lower)
                command = text[pos:].strip()
                
                # Убираем знаки препинания в начале и пробелы
                command = command.lstrip(',.!?:; ')
                
                if command:
                    print(f"📝 Извлечена команда: '{command}'")
                    return command
        
        # Если ключевое слово не найдено, возвращаем весь текст
        return text


# Глобальный экземпляр для удобства
voice_recognizer = None
hotword_detector = HotwordDetector()
