"""
AI агент для работы с различными AI провайдерами
"""

import os
import time
from typing import Dict, Any, Optional
from pathlib import Path

# Загружаем переменные окружения из .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    try:
        # Fallback к старой библиотеке
        import google.generativeai as genai
        GEMINI_AVAILABLE = True
        LEGACY_GEMINI = True
    except ImportError:
        GEMINI_AVAILABLE = False
        LEGACY_GEMINI = False
else:
    LEGACY_GEMINI = False

from .module_config import AIConfig


class AIAgent:
    """AI агент для модулей"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Инициализация AI клиента"""
        if self.config.model.startswith("gemini") and GEMINI_AVAILABLE:
            self._initialize_gemini()
        else:
            # Для тестирования без API ключа
            self.client = None
            print(f"⚠️ AI клиент не инициализирован (модель: {self.config.model})")
    
    def _initialize_gemini(self):
        """Инициализация Gemini API"""
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            print("⚠️ GEMINI_API_KEY не найден, используется мок режим")
            self.client = None
            return
        
        try:
            if LEGACY_GEMINI:
                # Старая библиотека google-generativeai
                genai.configure(api_key=api_key)
                self.client = genai.GenerativeModel(self.config.model)
            else:
                # Новая библиотека google-genai
                self.client = genai.Client(api_key=api_key)
            
            print(f"✅ Gemini API инициализирован ({'legacy' if LEGACY_GEMINI else 'new'} API)")
            
        except Exception as e:
            print(f"⚠️ Ошибка инициализации Gemini API: {e}")
            self.client = None
    
    def generate(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Генерация ответа от AI
        
        Args:
            prompt: Промпт для AI
            context: Дополнительный контекст
            
        Returns:
            Ответ от AI
        """
        if not self.client:
            # Возвращаем мок ответ для тестирования
            return self._generate_mock_response(prompt)
        
        try:
            # Формируем полный промпт с контекстом
            full_prompt = self._build_full_prompt(prompt, context)
            
            # Генерация через Gemini
            if self.config.model.startswith("gemini"):
                if LEGACY_GEMINI:
                    return self._generate_gemini_legacy(full_prompt)
                else:
                    return self._generate_gemini_new(full_prompt)
            
        except Exception as e:
            raise RuntimeError(f"Ошибка генерации AI: {str(e)}")
    
    def _build_full_prompt(self, prompt: str, context: Optional[Dict[str, Any]]) -> str:
        """Построение полного промпта с контекстом"""
        if not context:
            return prompt
        
        # Добавляем контекст в промпт
        context_str = ""
        if context:
            context_str = "\n\nКОНТЕКСТ:\n"
            for key, value in context.items():
                if value:  # Только непустые значения
                    context_str += f"{key}: {value}\n"
        
        return f"{prompt}{context_str}"
    
    def _generate_gemini_legacy(self, prompt: str) -> str:
        """Генерация через старый Gemini API"""
        try:
            response = self.client.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=self.config.max_tokens,
                    temperature=self.config.temperature,
                )
            )
            
            if response.text:
                return response.text.strip()
            else:
                raise RuntimeError("Пустой ответ от Gemini")
                
        except Exception as e:
            raise RuntimeError(f"Ошибка Gemini API (legacy): {str(e)}")
    
    def _generate_gemini_new(self, prompt: str) -> str:
        """Генерация через новый Gemini API"""
        try:
            response = self.client.models.generate_content(
                model=self.config.model,
                contents=prompt
            )
            
            if hasattr(response, 'text') and response.text:
                return response.text.strip()
            elif hasattr(response, 'candidates') and response.candidates:
                # Новый формат ответа
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts') and candidate.content.parts:
                        return candidate.content.parts[0].text.strip()
            
            raise RuntimeError("Пустой ответ от Gemini")
                
        except Exception as e:
            raise RuntimeError(f"Ошибка Gemini API (new): {str(e)}")
    
    
    def _generate_mock_response(self, prompt: str) -> str:
        """Генерация мок ответа для тестирования"""
        if "youtube" in prompt.lower() or "тикток" in prompt.lower():
            return """
НАЗВАНИЕ: Открыть YouTube в Chrome

DSL КОД:
```atlas
# Открыть Chrome и перейти на YouTube
open ChromeApp
wait 2s
click ChromeNewTab
wait 1s
type "youtube.com"
press enter
wait 3s
```

ОПИСАНИЕ: Макрос для открытия YouTube в новой вкладке Chrome
"""
        else:
            return """
НАЗВАНИЕ: Тестовый макрос

DSL КОД:
```atlas
# Тестовая последовательность
open ChromeApp
wait 2s
click ChromeNewTab
```

ОПИСАНИЕ: Тестовый макрос для проверки системы
"""
    
    def analyze_user_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Анализ намерений пользователя
        
        Args:
            user_input: Ввод пользователя
            
        Returns:
            Словарь с анализом намерений
        """
        intent_prompt = f"""
        Проанализируй запрос пользователя и определи его намерения.
        
        ЗАПРОС: {user_input}
        
        Верни результат в JSON формате:
        {{
            "type": "automation|chat|question",
            "platforms": ["chrome", "tiktok", "youtube"],
            "actions": ["open", "click", "type", "search"],
            "apps": ["chrome", "calculator", "terminal"],
            "complexity": "simple|medium|complex",
            "confidence": 0.95
        }}
        
        Только JSON, без дополнительного текста.
        """
        
        try:
            response = self.generate(intent_prompt)
            # Попытка парсинга JSON
            import json
            return json.loads(response)
        except:
            # Fallback анализ
            return self._fallback_intent_analysis(user_input)
    
    def _fallback_intent_analysis(self, user_input: str) -> Dict[str, Any]:
        """Fallback анализ намерений без AI"""
        user_lower = user_input.lower()
        
        # Простая эвристика
        intent = {
            "type": "chat",
            "platforms": [],
            "actions": [],
            "apps": [],
            "complexity": "simple",
            "confidence": 0.5
        }
        
        # Определение типа
        automation_keywords = ["открой", "запусти", "кликни", "найди", "создай", "сделай"]
        if any(keyword in user_lower for keyword in automation_keywords):
            intent["type"] = "automation"
        
        # Определение платформ
        platforms = {
            "chrome": ["хром", "chrome", "браузер"],
            "tiktok": ["тикток", "tiktok"],
            "youtube": ["ютуб", "youtube"],
        }
        
        for platform, keywords in platforms.items():
            if any(keyword in user_lower for keyword in keywords):
                intent["platforms"].append(platform)
        
        # Определение приложений
        apps = {
            "chrome": ["хром", "chrome", "браузер"],
            "calculator": ["калькулятор", "calculator"],
            "terminal": ["терминал", "terminal"],
        }
        
        for app, keywords in apps.items():
            if any(keyword in user_lower for keyword in keywords):
                intent["apps"].append(app)
        
        return intent
