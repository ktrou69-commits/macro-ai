# 🎤 Этап 3: Голосовой ввод (1-2 недели)

**Время выполнения:** 1-2 недели  
**Приоритет:** Высокий  
**Зависимости:** Этапы 1 и 2 завершены

## 🎯 Цели этапа

1. Реализовать постоянное прослушивание микрофона
2. Интегрировать распознавание речи (Whisper/Vosk)
3. Создать систему синтеза речи для ответов ИИ
4. Интегрировать голосовой ассистент с существующим AI

## 🛠️ Технологический стек

### Распознавание речи (ASR)
- **OpenAI Whisper** - высокое качество, локально
- **SpeechRecognition** - простая интеграция
- **Vosk** - быстрая альтернатива

### Синтез речи (TTS)
- **macOS say** - встроенный, быстрый
- **pyttsx3** - кроссплатформенный
- **gTTS** - Google TTS (онлайн)

### Обнаружение активации
- **pvporcupine** - hotword detection
- **webrtcvad** - voice activity detection

## 📋 Детальная реализация

### Шаг 3.1: Создать speech_recognition.py

**Файл:** `src/voice/speech_recognition.py`

```python
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

try:
    import speech_recognition as sr
    import pyaudio
    SPEECH_AVAILABLE = True
except ImportError:
    SPEECH_AVAILABLE = False
    print("⚠️ Модули распознавания речи недоступны")

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


class VoiceRecognizer:
    """Система распознавания голоса"""
    
    def __init__(self, 
                 engine: str = "whisper",
                 model_size: str = "base",
                 language: str = "ru"):
        
        self.engine = engine
        self.language = language
        self.is_listening = False
        self.audio_queue = queue.Queue()
        self.callback = None
        
        # Настройки аудио
        self.sample_rate = 16000
        self.chunk_size = 1024
        self.channels = 1
        
        # Инициализация движка
        if engine == "whisper" and WHISPER_AVAILABLE:
            self.whisper_model = whisper.load_model(model_size)
            print(f"✅ Whisper модель '{model_size}' загружена")
        elif SPEECH_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            print("✅ SpeechRecognition инициализирован")
        else:
            raise RuntimeError("Модули распознавания речи недоступны")
    
    def start_listening(self, callback: Callable[[str], None]):
        """Начать постоянное прослушивание"""
        if self.is_listening:
            return
            
        self.callback = callback
        self.is_listening = True
        
        # Запускаем поток прослушивания
        self.listen_thread = threading.Thread(
            target=self._listen_loop,
            daemon=True
        )
        self.listen_thread.start()
        
        print("🎤 Начато прослушивание...")
    
    def stop_listening(self):
        """Остановить прослушивание"""
        self.is_listening = False
        if hasattr(self, 'listen_thread'):
            self.listen_thread.join(timeout=2)
        print("🔇 Прослушивание остановлено")
    
    def _listen_loop(self):
        """Основной цикл прослушивания"""
        if self.engine == "whisper":
            self._whisper_listen_loop()
        else:
            self._speech_recognition_loop()
    
    def _whisper_listen_loop(self):
        """Цикл прослушивания с Whisper"""
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
            silence_threshold = 500  # Порог тишины
            silence_duration = 0
            max_silence = 30  # 30 чанков тишины = ~1 секунда
            
            while self.is_listening:
                try:
                    # Читаем аудио данные
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    audio_buffer.append(data)
                    
                    # Проверяем уровень звука
                    audio_level = max(data)
                    
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
        """Обработка буфера аудио данных"""
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
                language=self.language
            )
            
            text = result["text"].strip()
            
            if text and len(text) > 2:  # Игнорируем очень короткие фразы
                print(f"🎤 Распознано: '{text}'")
                if self.callback:
                    self.callback(text)
            
            # Удаляем временный файл
            Path(temp_file).unlink(missing_ok=True)
            
        except Exception as e:
            print(f"⚠️ Ошибка обработки аудио: {e}")
    
    def _speech_recognition_loop(self):
        """Цикл прослушивания с SpeechRecognition"""
        try:
            # Калибровка микрофона
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source)
            
            print("🎤 SpeechRecognition слушает...")
            
            while self.is_listening:
                try:
                    # Слушаем аудио
                    with self.microphone as source:
                        audio = self.recognizer.listen(
                            source, 
                            timeout=1, 
                            phrase_time_limit=5
                        )
                    
                    # Распознаем
                    text = self.recognizer.recognize_google(
                        audio, 
                        language=self.language
                    )
                    
                    if text:
                        print(f"🎤 Распознано: '{text}'")
                        if self.callback:
                            self.callback(text)
                            
                except sr.WaitTimeoutError:
                    pass  # Таймаут - продолжаем слушать
                except sr.UnknownValueError:
                    pass  # Не удалось распознать - продолжаем
                except Exception as e:
                    print(f"⚠️ Ошибка распознавания: {e}")
                    time.sleep(1)
                    
        except Exception as e:
            print(f"❌ Ошибка в SpeechRecognition цикле: {e}")


class HotwordDetector:
    """Детектор ключевых слов для активации"""
    
    def __init__(self, hotwords: list = None):
        self.hotwords = hotwords or [
            "окей ассистент", "привет ассистент", 
            "эй макро", "слушай"
        ]
        self.is_active = False
    
    def detect_hotword(self, text: str) -> bool:
        """Проверка наличия ключевого слова"""
        text_lower = text.lower()
        
        for hotword in self.hotwords:
            if hotword.lower() in text_lower:
                return True
        return False
    
    def extract_command(self, text: str) -> str:
        """Извлечение команды после ключевого слова"""
        text_lower = text.lower()
        
        for hotword in self.hotwords:
            hotword_lower = hotword.lower()
            if hotword_lower in text_lower:
                # Находим позицию после ключевого слова
                pos = text_lower.find(hotword_lower) + len(hotword_lower)
                command = text[pos:].strip()
                
                # Убираем знаки препинания в начале
                command = command.lstrip(',.!?:;')
                return command
        
        return text  # Если ключевое слово не найдено, возвращаем весь текст
```

### Шаг 3.2: Создать text_to_speech.py

**Файл:** `src/voice/text_to_speech.py`

```python
#!/usr/bin/env python3
"""
text_to_speech.py
Система синтеза речи для ответов ИИ
"""

import subprocess
import threading
import queue
from typing import Optional, Dict, Any
from pathlib import Path

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False


class TextToSpeech:
    """Система синтеза речи"""
    
    def __init__(self, engine: str = "macos_say", voice: str = "Milena"):
        self.engine = engine
        self.voice = voice
        self.is_speaking = False
        self.speech_queue = queue.Queue()
        
        # Инициализация движка
        if engine == "pyttsx3" and PYTTSX3_AVAILABLE:
            self.tts_engine = pyttsx3.init()
            self._setup_pyttsx3()
        
        # Запускаем поток для обработки очереди речи
        self.speech_thread = threading.Thread(
            target=self._speech_worker,
            daemon=True
        )
        self.speech_thread.start()
        
        print(f"✅ TTS инициализирован: {engine}")
    
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
        
        return True
    
    def speak_immediately(self, text: str) -> bool:
        """Произнести текст немедленно (прерывая текущую речь)"""
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
                             check=False)
            except Exception:
                pass
        elif self.engine == "pyttsx3" and PYTTSX3_AVAILABLE:
            try:
                self.tts_engine.stop()
            except Exception:
                pass
        
        self.is_speaking = False
    
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
            
            if self.engine == "macos_say":
                self._speak_with_say(text)
            elif self.engine == "pyttsx3":
                self._speak_with_pyttsx3(text)
            else:
                print(f"⚠️ Неизвестный TTS движок: {self.engine}")
            
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
    
    def get_available_voices(self) -> list:
        """Получить список доступных голосов"""
        voices = []
        
        if self.engine == "macos_say":
            try:
                result = subprocess.run(['say', '-v', '?'], 
                                      capture_output=True, 
                                      text=True)
                
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
                        return True
            
            return True  # Для macOS say просто сохраняем имя
            
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
    ]
}


class VoiceAssistantResponses:
    """Помощник для генерации голосовых ответов"""
    
    def __init__(self, tts: TextToSpeech):
        self.tts = tts
    
    def acknowledge_command(self, command: str = None):
        """Подтвердить получение команды"""
        import random
        
        if command and any(word in command.lower() for word in ['открой', 'запусти', 'открыть']):
            responses = ["Да сэр, открываю", "Конечно, запускаю", "Сейчас открою"]
        else:
            responses = QUICK_RESPONSES['acknowledgment']
        
        response = random.choice(responses)
        self.tts.speak(response, priority="high")
    
    def report_working(self):
        """Сообщить о работе"""
        import random
        response = random.choice(QUICK_RESPONSES['working'])
        self.tts.speak(response)
    
    def report_completed(self, task: str = None):
        """Сообщить о завершении"""
        import random
        
        if task:
            response = f"Задача '{task}' выполнена"
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
```

## 📋 Чек-лист выполнения Этапа 3

- [ ] Реализован VoiceRecognizer с Whisper и SpeechRecognition
- [ ] Создан TextToSpeech с поддержкой macOS say и pyttsx3
- [ ] Добавлен HotwordDetector для активации
- [ ] Реализованы быстрые голосовые ответы
- [ ] Протестирована работа с микрофоном
- [ ] Проверена интеграция с предыдущими этапами

## ➡️ Следующий этап

После завершения голосового ввода переходим к [Этапу 4: GUI интеграция](./stage-4-gui-integration.md)
