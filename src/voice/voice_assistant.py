#!/usr/bin/env python3
"""
voice_assistant.py
Главный голосовой ассистент - объединяет все компоненты
"""

import threading
import time
from typing import Optional, Dict, Any, Callable
from pathlib import Path

# Импорты голосовых модулей
from .speech_recognition import VoiceRecognizer, HotwordDetector
from .text_to_speech import TextToSpeech, VoiceAssistantResponses

# Импорты существующих модулей
try:
    from src.system.system_orchestrator import system_orchestrator
    from src.voice.ai_voice_integration import ai_assistant
    SYSTEM_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    SYSTEM_ORCHESTRATOR_AVAILABLE = False
    print("⚠️ SystemOrchestrator недоступен")

try:
    from src.memory.state_manager import state_manager
    STATE_MANAGER_AVAILABLE = True
except ImportError:
    STATE_MANAGER_AVAILABLE = False
    print("⚠️ StateManager недоступен")

try:
    from src.ai.macro_generator import MacroGenerator
    AI_GENERATOR_AVAILABLE = True
except ImportError:
    AI_GENERATOR_AVAILABLE = False
    print("⚠️ AI MacroGenerator недоступен")


class VoiceAssistant:
    """Главный класс голосового ассистента"""
    
    def __init__(self, 
                 recognition_engine: str = "google",
                 tts_engine: str = "macos_say",
                 voice: str = "Milena"):
        
        self.is_active = False
        self.is_listening = False
        
        # Инициализация компонентов
        self.voice_recognizer = VoiceRecognizer(engine=recognition_engine)
        self.hotword_detector = HotwordDetector()
        self.tts = TextToSpeech(engine=tts_engine, voice=voice)
        self.voice_responses = VoiceAssistantResponses(self.tts)
        
        # Интеграция с существующими модулями
        self.system_orchestrator = system_orchestrator if SYSTEM_ORCHESTRATOR_AVAILABLE else None
        self.state_manager = state_manager if STATE_MANAGER_AVAILABLE else None
        
        # AI генератор (опционально)
        self.ai_generator = None
        if AI_GENERATOR_AVAILABLE:
            try:
                self.ai_generator = MacroGenerator()
            except Exception as e:
                print(f"⚠️ Не удалось инициализировать AI генератор: {e}")
        
        # Статистика
        self.stats = {
            'commands_processed': 0,
            'successful_executions': 0,
            'errors': 0,
            'session_start': None
        }
        
        print("🤖 Голосовой ассистент инициализирован")
        self._show_capabilities()
    
    def _show_capabilities(self):
        """Показать возможности ассистента"""
        print("\n🎯 Возможности голосового ассистента:")
        print("   🎤 Распознавание речи:", "✅" if self.voice_recognizer else "❌")
        print("   🔊 Синтез речи:", "✅" if self.tts else "❌")
        print("   🔧 Системные команды:", "✅" if self.system_orchestrator else "❌")
        print("   🧠 AI генератор:", "✅" if self.ai_generator else "❌")
        print("   💾 Управление состоянием:", "✅" if self.state_manager else "❌")
        
        print("\n🗣️ Примеры команд:")
        print("   • 'Окей ассистент, открой Safari'")
        print("   • 'Окей ассистент, сделай скриншот'")
        print("   • 'Окей ассистент, создай макрос для открытия гугла'")
        print("   • 'Окей ассистент, покажи активные процессы'")
    
    def start(self):
        """Запустить голосового ассистента"""
        if self.is_active:
            print("⚠️ Ассистент уже активен")
            return
        
        self.is_active = True
        self.stats['session_start'] = time.time()
        
        print("🚀 Запуск голосового ассистента...")
        
        # Приветствие
        self.voice_responses.say_custom("Голосовой ассистент активирован", immediate=True)
        
        # Запускаем распознавание речи
        self.voice_recognizer.start_listening(self._on_speech_recognized)
        
        print("🎤 Ассистент слушает... Скажите 'Окей ассистент' для активации")
    
    def stop(self):
        """Остановить голосового ассистента"""
        if not self.is_active:
            return
        
        self.is_active = False
        
        print("🛑 Остановка голосового ассистента...")
        
        # Останавливаем распознавание
        self.voice_recognizer.stop_listening()
        
        # Останавливаем речь
        self.tts.stop_speaking()
        
        # Прощание
        self.voice_responses.say_custom("Ассистент деактивирован", immediate=True)
        
        # Показываем статистику
        self._show_session_stats()
        
        print("✅ Ассистент остановлен")
    
    def _on_speech_recognized(self, text: str):
        """Обработка распознанной речи"""
        if not self.is_active:
            return
        
        print(f"🎤 Получен текст: '{text}'")
        
        # Проверяем на ключевые слова
        if self.hotword_detector.detect_hotword(text):
            # Извлекаем команду
            command = self.hotword_detector.extract_command(text)
            
            if command:
                print(f"🎯 Активация! Команда: '{command}'")
                self._process_voice_command(command)
            else:
                print("🤷 Ключевое слово найдено, но команда не извлечена")
                self.voice_responses.say_custom("Да, слушаю")
        else:
            print("🔇 Ключевое слово не обнаружено, игнорируем")
    
    def _process_voice_command(self, command: str):
        """Обработка голосовой команды с AI"""
        self.stats['commands_processed'] += 1
        
        try:
            print(f"🤖 Обрабатываю через AI: '{command}'")
            
            # Обрабатываем через AI ассистента
            if ai_assistant.is_available():
                ai_result = ai_assistant.process_voice_message(command)
                
                # Произносим AI ответ
                self.tts.speak(ai_result['response'])
                
                # Выполняем действие в зависимости от типа
                if ai_result['action'] == 'command':
                    self._execute_ai_system_command(ai_result)
                elif ai_result['action'] == 'macro':
                    self._execute_ai_macro_request(ai_result)
                elif ai_result['response'] == "Извините, произошла ошибка. Попробуйте еще раз.":
                    # AI недоступен, используем fallback
                    print("🔄 AI недоступен, используем локальную обработку")
                    self._execute_local_command_analysis(command)
                elif ai_result['action'] == 'chat':
                    # Для обычного разговора убеждаемся что ответ произносится
                    print(f"💬 Обычный разговор, произношу ответ: '{ai_result['response']}'")
                    # AI ответ уже произнесен выше, но добавим дополнительную проверку
                    if not self.tts.is_speaking:
                        self.tts.speak(ai_result['response'])
                
            else:
                # Fallback к старой логике
                self._execute_local_command_analysis(command)
            
            self.stats['successful_executions'] += 1
            
        except Exception as e:
            print(f"❌ Ошибка обработки команды: {e}")
            self.stats['errors'] += 1
            self.voice_responses.report_error(str(e))
    
    def _is_simple_system_command(self, command: str) -> bool:
        """Проверка, является ли команда простой системной"""
        command_lower = command.lower()
        
        simple_commands = [
            'открой', 'запусти', 'закрой', 'сделай скриншот', 
            'скриншот', 'копируй', 'процессы', 'приложения'
        ]
        
        return any(cmd in command_lower for cmd in simple_commands)
    
    def _is_ai_command(self, command: str) -> bool:
        """Проверка, требует ли команда AI"""
        command_lower = command.lower()
        
        ai_commands = [
            'создай макрос', 'сгенерируй', 'напиши макрос',
            'автоматизируй', 'помоги с', 'как сделать'
        ]
        
        return any(cmd in command_lower for cmd in ai_commands)
    
    def _execute_simple_system_command(self, command: str):
        """Выполнение простых системных команд"""
        if not self.system_orchestrator:
            self.voice_responses.report_error("Системные команды недоступны")
            return
        
        command_lower = command.lower()
        
        # Парсим команду и выполняем
        if 'открой' in command_lower or 'запусти' in command_lower:
            app_name = self._extract_app_name(command)
            if app_name:
                result = self.system_orchestrator.execute_system_command('open_app', app_name)
                if result['success']:
                    self.voice_responses.report_completed(f"открытие {app_name}")
                else:
                    self.voice_responses.report_error(result.get('error', 'Неизвестная ошибка'))
            else:
                self.voice_responses.report_error("Не удалось определить приложение")
        
        elif 'скриншот' in command_lower:
            result = self.system_orchestrator.execute_system_command('take_screenshot')
            if result['success']:
                self.voice_responses.report_completed("создание скриншота")
            else:
                self.voice_responses.report_error(result.get('error', 'Ошибка скриншота'))
        
        elif 'процессы' in command_lower:
            result = self.system_orchestrator.execute_system_command('list_processes')
            if result['success']:
                count = result.get('count', 0)
                self.voice_responses.say_custom(f"Найдено {count} активных процессов")
            else:
                self.voice_responses.report_error("Ошибка получения процессов")
        
        else:
            self.voice_responses.report_error("Команда не распознана")
    
    def _execute_ai_command(self, command: str):
        """Выполнение команд через AI"""
        if not self.ai_generator:
            self.voice_responses.report_error("AI генератор недоступен")
            return
        
        self.voice_responses.report_working()
        
        try:
            # Генерируем макрос через AI
            print(f"🧠 Отправляем в AI: '{command}'")
            
            # Здесь будет интеграция с AI генератором
            # Пока что заглушка
            self.voice_responses.say_custom("AI обработка команды пока не реализована")
            
        except Exception as e:
            print(f"❌ Ошибка AI: {e}")
            self.voice_responses.report_error("Ошибка AI генератора")
    
    def _execute_generic_command(self, command: str):
        """Выполнение общих команд"""
        # Пытаемся интерпретировать как системную команду
        self.voice_responses.report_working()
        
        # Простая эвристика для определения действия
        command_lower = command.lower()
        
        if any(word in command_lower for word in ['покажи', 'что', 'какой', 'сколько']):
            # Информационные команды
            if 'приложение' in command_lower or 'программа' in command_lower:
                if self.system_orchestrator:
                    result = self.system_orchestrator.execute_system_command('get_current_app')
                    if result['success']:
                        app_name = result.get('app_name', 'Неизвестно')
                        self.voice_responses.say_custom(f"Активное приложение: {app_name}")
                    else:
                        self.voice_responses.report_error("Не удалось определить приложение")
                else:
                    self.voice_responses.report_error("Системные команды недоступны")
            else:
                self.voice_responses.say_custom("Уточните, что именно показать")
        else:
            self.voice_responses.say_custom("Команда не распознана. Попробуйте переформулировать")
    
    def _extract_app_name(self, command: str) -> Optional[str]:
        """Извлечение имени приложения из команды"""
        command_lower = command.lower()
        
        # Словарь популярных приложений
        app_mapping = {
            'сафари': 'Safari',
            'safari': 'Safari',
            'хром': 'Google Chrome',
            'chrome': 'Google Chrome',
            'гугл хром': 'Google Chrome',
            'калькулятор': 'Calculator',
            'calculator': 'Calculator',
            'терминал': 'Terminal',
            'terminal': 'Terminal',
            'файндер': 'Finder',
            'finder': 'Finder',
            'заметки': 'Notes',
            'notes': 'Notes'
        }
        
        for key, app_name in app_mapping.items():
            if key in command_lower:
                return app_name
        
        # Если не нашли в словаре, пытаемся извлечь последнее слово
        words = command.split()
        if words:
            return words[-1].capitalize()
        
        return None
    
    def _show_session_stats(self):
        """Показать статистику сессии"""
        if self.stats['session_start']:
            duration = time.time() - self.stats['session_start']
            print(f"\n📊 Статистика сессии:")
            print(f"   ⏱️ Длительность: {duration:.1f} секунд")
            print(f"   🎤 Команд обработано: {self.stats['commands_processed']}")
            print(f"   ✅ Успешных выполнений: {self.stats['successful_executions']}")
            print(f"   ❌ Ошибок: {self.stats['errors']}")
    
    def _execute_ai_system_command(self, ai_result: Dict[str, Any]):
        """Выполнение системной команды через AI"""
        command = ai_result.get('command')
        app_name = ai_result.get('app_name')
        
        if not command:
            return
        
        try:
            print(f"🔧 Выполняю команду: {command}")
            if app_name:
                print(f"📱 Приложение: {app_name}")
            
            if command in ['open_app', 'close_app']:
                if app_name:
                    result = system_orchestrator.execute_system_command(command, f'"{app_name}"')
                else:
                    print(f"❌ Команда {command} требует название приложения")
                    return
            else:
                result = system_orchestrator.execute_system_command(command)
            
            if result['success']:
                print(f"✅ Команда {command} выполнена: {result.get('message', 'Готово')}")
                self.tts.speak("Готово")
            else:
                print(f"❌ Ошибка выполнения {command}: {result.get('error', 'Неизвестная ошибка')}")
                self.tts.speak("Произошла ошибка при выполнении команды")
                
        except Exception as e:
            print(f"❌ Ошибка выполнения AI команды: {e}")
            self.tts.speak("Произошла ошибка")
    
    def _execute_ai_macro_request(self, ai_result: Dict[str, Any]):
        """Обработка запроса на создание макроса через AI"""
        macro_request = ai_result.get('macro_request')
        
        if not macro_request:
            return
        
        print(f"🔧 Запрос на макрос: {macro_request}")
        
        # Здесь можно интегрировать с существующим AI генератором макросов
        # Пока просто уведомляем пользователя
        self.tts.speak("Функция создания макросов будет добавлена в следующей версии")
    
    def _execute_local_command_analysis(self, command: str):
        """Локальная обработка команд без AI"""
        command_lower = command.lower()
        
        # База приложений для локального анализа
        app_mapping = {
            'safari': 'Safari',
            'хром': 'Google Chrome',
            'chrome': 'Google Chrome',
            'гугл хром': 'Google Chrome',
            'калькулятор': 'Calculator',
            'calculator': 'Calculator',
            'терминал': 'Terminal',
            'terminal': 'Terminal',
            'файндер': 'Finder',
            'finder': 'Finder',
            'заметки': 'Notes',
            'notes': 'Notes',
            'телеграм': 'Telegram',
            'telegram': 'Telegram'
        }
        
        try:
            if any(word in command_lower for word in ["открой", "запусти", "открыть", "запустить"]):
                # Команда открытия приложения
                app_name = None
                for russian_name, english_name in app_mapping.items():
                    if russian_name in command_lower:
                        app_name = english_name
                        break
                
                if app_name:
                    self.tts.speak(f"Открываю {app_name}")
                    result = system_orchestrator.execute_system_command("open_app", f'"{app_name}"')
                    if result['success']:
                        print(f"✅ Открыто: {app_name}")
                        self.tts.speak("Готово")
                    else:
                        print(f"❌ Ошибка открытия {app_name}: {result.get('error')}")
                        self.tts.speak("Не удалось открыть приложение")
                else:
                    self.tts.speak("Не могу определить какое приложение открыть")
                    
            elif any(word in command_lower for word in ["скриншот", "снимок"]):
                self.tts.speak("Делаю скриншот")
                result = system_orchestrator.execute_system_command("take_screenshot")
                if result['success']:
                    print(f"✅ Скриншот создан")
                    self.tts.speak("Скриншот готов")
                else:
                    self.tts.speak("Не удалось сделать скриншот")
                    
            elif any(word in command_lower for word in ["процессы", "приложения"]):
                self.tts.speak("Показываю процессы")
                result = system_orchestrator.execute_system_command("list_processes")
                if result['success']:
                    self.tts.speak("Список процессов готов")
                    
            else:
                # Обычный разговор
                self.tts.speak("Понял, но не знаю как это выполнить")
                
        except Exception as e:
            print(f"❌ Ошибка локальной обработки: {e}")
            self.tts.speak("Произошла ошибка")
    
    def process_text_command(self, command: str):
        """Обработка текстовой команды (для тестирования)"""
        print(f"💬 Текстовая команда: '{command}'")
        self._process_voice_command(command)


# Глобальный экземпляр для удобства
voice_assistant = None

def get_voice_assistant(**kwargs) -> VoiceAssistant:
    """Получить экземпляр голосового ассистента"""
    global voice_assistant
    if voice_assistant is None:
        voice_assistant = VoiceAssistant(**kwargs)
    return voice_assistant
