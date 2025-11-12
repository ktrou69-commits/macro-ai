#!/usr/bin/env python3
"""
AI интеграция для голосового ассистента
Подключение Gemini API для полноценного общения
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from google import genai
    from dotenv import load_dotenv
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Gemini API недоступен. Установите: pip install google-genai python-dotenv")


class VoiceAIAssistant:
    """AI ассистент для голосового общения"""
    
    def __init__(self):
        self.model = None
        self.chat_session = None
        self.conversation_history = []
        self.system_prompt = self._create_system_prompt()
        
        # Загружаем переменные окружения
        load_dotenv()
        
        if GEMINI_AVAILABLE:
            self._initialize_gemini()
    
    def _initialize_gemini(self):
        """Инициализация Gemini API"""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                print("❌ GEMINI_API_KEY не найден в .env файле")
                return False
            
            # Создаем клиент с API ключом
            self.client = genai.Client(api_key=api_key)
            
            print("✅ Gemini AI подключен для голосового общения")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка инициализации Gemini: {e}")
            return False
    
    def _create_system_prompt(self) -> str:
        """Создание системного промпта для голосового ассистента"""
        return """Ты - голосовой AI ассистент для системы автоматизации macOS "Macro AI".

ТВОЯ РОЛЬ:
- Дружелюбный и полезный голосовой помощник
- Отвечаешь кратко и по делу (1-2 предложения)
- Говоришь естественно, как живой собеседник
- Помогаешь с автоматизацией задач на macOS

БАЗА ПРИЛОЖЕНИЙ macOS (ИСПОЛЬЗУЙ ТОЧНЫЕ АНГЛИЙСКИЕ НАЗВАНИЯ):
Браузеры:
- Safari → "Safari"
- Хром, Chrome, Гугл Хром → "Google Chrome"
- Файрфокс, Firefox → "Firefox"
- Эдж, Edge → "Microsoft Edge"

Системные:
- Калькулятор, Calculator → "Calculator"
- Терминал, Terminal → "Terminal"
- Файндер, Finder → "Finder"
- Заметки, Notes → "Notes"
- Календарь, Calendar → "Calendar"
- Почта, Mail → "Mail"
- Настройки, Системные настройки → "System Preferences"

Офис:
- Ворд, Word → "Microsoft Word"
- Эксель, Excel → "Microsoft Excel"
- Пауэрпоинт, PowerPoint → "Microsoft PowerPoint"
- Кейнот, Keynote → "Keynote"
- Пейджес, Pages → "Pages"
- Намберс, Numbers → "Numbers"

Разработка:
- Иксод, Xcode → "Xcode"
- ВС Код, VS Code, Visual Studio Code → "Visual Studio Code"
- Атом, Atom → "Atom"
- Сублайм, Sublime → "Sublime Text"

Медиа:
- Спотифай, Spotify → "Spotify"
- Айтюнс, iTunes → "iTunes"
- Музыка, Music → "Music"
- ТВ, TV → "TV"
- Фотос, Photos → "Photos"

Мессенджеры:
- Телеграм, Telegram → "Telegram"
- Ватсап, WhatsApp → "WhatsApp"
- Скайп, Skype → "Skype"
- Дискорд, Discord → "Discord"
- Слак, Slack → "Slack"

ДОСТУПНЫЕ СИСТЕМНЫЕ КОМАНДЫ:
- open_app "AppName" - открыть приложение (ИСПОЛЬЗУЙ АНГЛИЙСКИЕ НАЗВАНИЯ ИЗ БАЗЫ!)
- close_app "AppName" - закрыть приложение
- take_screenshot - сделать скриншот
- copy_to_clipboard "text" - скопировать в буфер
- read_clipboard - прочитать буфер
- get_current_app - узнать активное приложение
- list_processes - показать процессы
- focus_window "AppName" - переключиться на окно

ВАЖНЫЕ ПРАВИЛА:
1. ВСЕГДА переводи русские названия приложений на английские из базы
2. Если пользователь говорит "открой хром" → используй "Google Chrome"
3. Если пользователь говорит "запусти калькулятор" → используй "Calculator"
4. Если приложения нет в базе, используй наиболее вероятное английское название

СТИЛЬ ОБЩЕНИЯ:
- Используй "Да сэр", "Конечно", "Выполняю" для подтверждений
- Будь вежливым но не слишком формальным
- Объясняй что делаешь: "Открываю Safari для вас"
- При ошибках предлагай альтернативы

ПРИМЕРЫ ПРАВИЛЬНЫХ ОТВЕТОВ:
Пользователь: "Открой Safari"
Ты: "Да сэр, открываю Safari для вас"

Пользователь: "Запусти хром"
Ты: "Конечно! Открываю Google Chrome"

Пользователь: "Открой калькулятор"
Ты: "Выполняю! Запускаю Calculator"

Пользователь: "Как дела?"  
Ты: "Отлично! Готов помочь с автоматизацией. Что нужно сделать?"

ВАЖНО: ВСЕГДА используй точные английские названия из базы для команд open_app!"""
    
    def process_voice_message(self, user_message: str) -> Dict[str, Any]:
        """
        Обработка голосового сообщения пользователя
        
        Returns:
            Dict с ключами:
            - response: текстовый ответ для TTS
            - action: тип действия (chat/command/macro)
            - command: системная команда (если нужна)
            - macro_request: запрос на создание макроса (если нужен)
        """
        
        if not hasattr(self, 'client') or not self.client:
            return {
                "response": "Извините, AI помощник недоступен. Работаю в базовом режиме.",
                "action": "chat",
                "command": None,
                "macro_request": None
            }
        
        try:
            # Создаем структурированный промпт для AI
            prompt = f"""
Ты - голосовой AI ассистент для macOS. Проанализируй команду и ответь ТОЧНО в указанном формате.

КОМАНДА ПОЛЬЗОВАТЕЛЯ: "{user_message}"

БАЗА ПРИЛОЖЕНИЙ (используй точные английские названия):
- Safari, Хром/Chrome → "Safari", "Google Chrome"
- Калькулятор/Calculator → "Calculator"
- Терминал/Terminal → "Terminal"
- Файндер/Finder → "Finder"
- Заметки/Notes → "Notes"
- Календарь/Calendar → "Calendar"
- Почта/Mail → "Mail"
- Настройки → "System Preferences"
- Ворд/Word → "Microsoft Word"
- Эксель/Excel → "Microsoft Excel"
- Телеграм/Telegram → "Telegram"
- Спотифай/Spotify → "Spotify"

АНАЛИЗ КОМАНДЫ:
1. Если команда "открой/запусти/открыть [приложение]":
   - Найди приложение в базе
   - Ответь: "Конечно! Открываю [английское название]"
   - Действие: COMMAND
   - Команда: open_app
   - Приложение: [точное английское название из базы]

2. Если команда "закрой [приложение]":
   - Ответь: "Закрываю [приложение]"
   - Действие: COMMAND
   - Команда: close_app

3. Если команда "сделай скриншот/скриншот":
   - Ответь: "Да сэр, делаю скриншот"
   - Действие: COMMAND
   - Команда: take_screenshot

4. Если обычный разговор:
   - Ответь дружелюбно
   - Действие: CHAT

ФОРМАТ ОТВЕТА (отвечай ТОЛЬКО текстом для произношения):
[твой дружелюбный ответ для произношения]

ВАЖНО: Используй ТОЛЬКО точные английские названия из базы!
"""
            
            # Отправляем запрос в Gemini используя новый API
            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            ai_response = response.text.strip()
            
            # Сохраняем в историю
            self.conversation_history.append({
                "user": user_message,
                "assistant": ai_response,
                "timestamp": self._get_timestamp()
            })
            
            # Анализируем тип запроса
            action_type = self._analyze_request_type(user_message, ai_response)
            
            result = {
                "response": ai_response,
                "action": action_type["action"],
                "command": action_type.get("command"),
                "macro_request": action_type.get("macro_request")
            }
            
            print(f"🤖 AI ответ: {ai_response}")
            return result
            
        except Exception as e:
            print(f"❌ Ошибка AI обработки: {e}")
            return {
                "response": "Извините, произошла ошибка. Попробуйте еще раз.",
                "action": "chat",
                "command": None,
                "macro_request": None
            }
    
    def _analyze_request_type(self, user_message: str, ai_response: str) -> Dict[str, Any]:
        """Анализ типа запроса пользователя с улучшенным извлечением приложений"""
        
        user_lower = user_message.lower()
        response_lower = ai_response.lower()
        
        # База приложений для точного извлечения
        app_mapping = {
            # Русские названия → английские
            'safari': 'Safari',
            'хром': 'Google Chrome',
            'chrome': 'Google Chrome',
            'гугл хром': 'Google Chrome',
            'google chrome': 'Google Chrome',
            'firefox': 'Firefox',
            'файрфокс': 'Firefox',
            'калькулятор': 'Calculator',
            'calculator': 'Calculator',
            'терминал': 'Terminal',
            'terminal': 'Terminal',
            'файндер': 'Finder',
            'finder': 'Finder',
            'заметки': 'Notes',
            'notes': 'Notes',
            'календарь': 'Calendar',
            'calendar': 'Calendar',
            'почта': 'Mail',
            'mail': 'Mail',
            'настройки': 'System Preferences',
            'системные настройки': 'System Preferences',
            'ворд': 'Microsoft Word',
            'word': 'Microsoft Word',
            'microsoft word': 'Microsoft Word',
            'эксель': 'Microsoft Excel',
            'excel': 'Microsoft Excel',
            'microsoft excel': 'Microsoft Excel',
            'телеграм': 'Telegram',
            'telegram': 'Telegram',
            'спотифай': 'Spotify',
            'spotify': 'Spotify',
            'музыка': 'Music',
            'music': 'Music',
            'фотос': 'Photos',
            'photos': 'Photos'
        }
        
        # Определяем тип команды
        if any(word in user_lower for word in ["открой", "запусти", "открыть", "запустить"]):
            # Команда открытия приложения
            app_name = None
            
            # Ищем название приложения в сообщении пользователя
            for russian_name, english_name in app_mapping.items():
                if russian_name in user_lower:
                    app_name = english_name
                    break
            
            # Если не нашли в базе, пытаемся извлечь из AI ответа
            if not app_name:
                # Ищем паттерны в ответе AI
                if "открываю" in response_lower:
                    # Извлекаем название после "открываю"
                    import re
                    match = re.search(r'открываю\s+([^.!]+)', response_lower)
                    if match:
                        app_name = match.group(1).strip()
                        # Переводим на английский если нужно
                        app_name = app_mapping.get(app_name.lower(), app_name.title())
            
            return {
                "action": "command",
                "command": "open_app",
                "app_name": app_name
            }
            
        elif any(word in user_lower for word in ["закрой", "закрыть"]):
            # Команда закрытия приложения
            app_name = None
            for russian_name, english_name in app_mapping.items():
                if russian_name in user_lower:
                    app_name = english_name
                    break
                    
            return {
                "action": "command",
                "command": "close_app",
                "app_name": app_name
            }
            
        elif any(word in user_lower for word in ["скриншот", "снимок", "screenshot"]):
            return {
                "action": "command",
                "command": "take_screenshot"
            }
            
        elif any(word in user_lower for word in ["активное приложение", "текущее приложение", "current app"]):
            return {
                "action": "command",
                "command": "get_current_app"
            }
            
        elif any(word in user_lower for word in ["процессы", "processes"]):
            return {
                "action": "command",
                "command": "list_processes"
            }
            
        elif any(word in user_lower for word in ["буфер", "clipboard"]):
            return {
                "action": "command",
                "command": "read_clipboard"
            }
        
        # Запросы на создание макроса
        macro_keywords = ["создай макрос", "сделай макрос", "макрос для", "автоматизируй"]
        for keyword in macro_keywords:
            if keyword in user_lower:
                return {
                    "action": "macro",
                    "macro_request": user_message
                }
        
        # Обычный разговор
        return {"action": "chat"}
    
    def _extract_app_name(self, message: str, command_keyword: str) -> Optional[str]:
        """Извлечение названия приложения из команды с переводом на английский"""
        
        # База приложений для перевода
        app_translations = {
            # Браузеры
            'safari': 'Safari',
            'хром': 'Google Chrome',
            'chrome': 'Google Chrome', 
            'гугл хром': 'Google Chrome',
            'firefox': 'Firefox',
            'файрфокс': 'Firefox',
            'edge': 'Microsoft Edge',
            'эдж': 'Microsoft Edge',
            
            # Системные
            'калькулятор': 'Calculator',
            'calculator': 'Calculator',
            'терминал': 'Terminal',
            'terminal': 'Terminal',
            'файндер': 'Finder',
            'finder': 'Finder',
            'заметки': 'Notes',
            'notes': 'Notes',
            'календарь': 'Calendar',
            'calendar': 'Calendar',
            'почта': 'Mail',
            'mail': 'Mail',
            'настройки': 'System Preferences',
            'системные настройки': 'System Preferences',
            
            # Офис
            'ворд': 'Microsoft Word',
            'word': 'Microsoft Word',
            'эксель': 'Microsoft Excel',
            'excel': 'Microsoft Excel',
            'пауэрпоинт': 'Microsoft PowerPoint',
            'powerpoint': 'Microsoft PowerPoint',
            'кейнот': 'Keynote',
            'keynote': 'Keynote',
            'пейджес': 'Pages',
            'pages': 'Pages',
            'намберс': 'Numbers',
            'numbers': 'Numbers',
            
            # Разработка
            'xcode': 'Xcode',
            'иксод': 'Xcode',
            'vs code': 'Visual Studio Code',
            'вс код': 'Visual Studio Code',
            'visual studio code': 'Visual Studio Code',
            'atom': 'Atom',
            'атом': 'Atom',
            'sublime': 'Sublime Text',
            'сублайм': 'Sublime Text',
            
            # Медиа
            'spotify': 'Spotify',
            'спотифай': 'Spotify',
            'itunes': 'iTunes',
            'айтюнс': 'iTunes',
            'music': 'Music',
            'музыка': 'Music',
            'tv': 'TV',
            'тв': 'TV',
            'photos': 'Photos',
            'фотос': 'Photos',
            
            # Мессенджеры
            'telegram': 'Telegram',
            'телеграм': 'Telegram',
            'whatsapp': 'WhatsApp',
            'ватсап': 'WhatsApp',
            'skype': 'Skype',
            'скайп': 'Skype',
            'discord': 'Discord',
            'дискорд': 'Discord',
            'slack': 'Slack',
            'слак': 'Slack'
        }
        
        message_lower = message.lower()
        
        # Ищем точные совпадения в базе
        for russian_name, english_name in app_translations.items():
            if russian_name in message_lower:
                return english_name
        
        # Если не нашли в базе, пытаемся извлечь слово после команды
        try:
            words = message.split()
            keyword_index = -1
            
            for i, word in enumerate(words):
                if command_keyword in word.lower():
                    keyword_index = i
                    break
            
            if keyword_index >= 0 and keyword_index + 1 < len(words):
                app_name = words[keyword_index + 1]
                # Убираем знаки препинания
                app_name = app_name.strip('.,!?').capitalize()
                return app_name
                
        except Exception:
            pass
        
        return None
    
    def _get_timestamp(self) -> str:
        """Получение временной метки"""
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")
    
    def get_conversation_history(self) -> list:
        """Получение истории разговора"""
        return self.conversation_history.copy()
    
    def clear_history(self):
        """Очистка истории разговора"""
        self.conversation_history.clear()
        if self.chat_session:
            # Перезапускаем сессию для очистки контекста
            self.chat_session = self.model.start_chat(history=[])
    
    def is_available(self) -> bool:
        """Проверка доступности AI"""
        return GEMINI_AVAILABLE and hasattr(self, 'client') and self.client is not None


# Глобальный экземпляр AI ассистента
ai_assistant = VoiceAIAssistant()


def process_voice_with_ai(user_message: str) -> Dict[str, Any]:
    """
    Функция для обработки голосового сообщения через AI
    Используется в voice_assistant.py
    """
    return ai_assistant.process_voice_message(user_message)


if __name__ == "__main__":
    # Тест AI ассистента
    print("🤖 Тестирование AI голосового ассистента")
    
    if not ai_assistant.is_available():
        print("❌ AI недоступен")
        exit(1)
    
    test_messages = [
        "Привет! Как дела?",
        "Открой Safari",
        "Сделай скриншот",
        "Создай макрос для открытия гугла",
        "Покажи активное приложение"
    ]
    
    for message in test_messages:
        print(f"\n👤 Пользователь: {message}")
        result = ai_assistant.process_voice_message(message)
        print(f"🤖 Ответ: {result['response']}")
        print(f"🔧 Действие: {result['action']}")
        if result.get('command'):
            print(f"⚙️ Команда: {result['command']}")
