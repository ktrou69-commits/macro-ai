#!/usr/bin/env python3
"""
Умный AI Router - быстрый выбор модуля без загрузки всех компонентов
"""

import os
import logging
from typing import Dict, Any, Optional, Tuple
from pathlib import Path

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartAIRouter:
    """
    Быстрый AI Router для выбора оптимального модуля
    Работает без загрузки тяжелых компонентов
    """
    
    # Описания модулей для AI
    MODULE_DESCRIPTIONS = {
        "sequence_generator": {
            "description": "Генерация макросов автоматизации",
            "keywords": ["макрос", "автоматизация", "открой", "найди", "запусти", "кликни", "введи", "поиск", 
                        "youtube", "google", "twitter", "facebook", "instagram", "linkedin", "github", "amazon", "netflix",
                        "зайди", "перейди", "браузер", "сайт", "веб", "интернет"],
            "examples": [
                "открой калькулятор",
                "найди на YouTube видео про Python", 
                "зайди на Twitter и найди новости",
                "найди на Amazon товары",
                "найди файлы PDF через Spotlight",
                "создай макрос для покупки товаров"
            ],
            "load_time": "fast"  # быстрая загрузка
        },
        "dom_analyzer": {
            "description": "Анализ веб-страниц и извлечение селекторов",
            "keywords": ["селектор", "dom", "веб-страница", "элемент", "css", "xpath"],
            "examples": [
                "найди селекторы на странице",
                "проанализируй структуру сайта"
            ],
            "load_time": "medium"
        },
        "prompt_updater": {
            "description": "Обновление AI промптов и шаблонов",
            "keywords": ["промпт", "шаблон", "обновить", "улучшить"],
            "examples": [
                "обнови промпты",
                "улучши шаблоны"
            ],
            "load_time": "fast"
        }
    }
    
    def __init__(self):
        """Инициализация роутера"""
        self.gemini_api = None
        logger.info("🚀 SmartAIRouter инициализирован")
    
    def _init_gemini_if_needed(self):
        """Ленивая инициализация Gemini API"""
        if self.gemini_api is None:
            try:
                import google.generativeai as genai
                
                api_key = os.getenv('GEMINI_API_KEY')
                if not api_key:
                    raise ValueError("GEMINI_API_KEY не найден в переменных окружения")
                
                self.gemini_api = genai.Client(api_key=api_key)
                logger.info("✅ Gemini API инициализирован для роутера")
            except Exception as e:
                logger.error(f"❌ Ошибка инициализации Gemini API: {e}")
                raise
    
    def analyze_user_request(self, user_request: str) -> Tuple[str, float, Dict[str, Any]]:
        """
        Быстрый анализ запроса пользователя для выбора модуля
        
        Args:
            user_request: Запрос пользователя
            
        Returns:
            Tuple[module_name, confidence, context]
        """
        try:
            # Простой анализ по ключевым словам (быстро)
            request_lower = user_request.lower()
            
            # Проверяем ключевые слова для каждого модуля
            scores = {}
            for module_name, module_info in self.MODULE_DESCRIPTIONS.items():
                score = 0
                for keyword in module_info["keywords"]:
                    if keyword in request_lower:
                        score += 1
                
                # Дополнительные очки за точные совпадения
                for example in module_info["examples"]:
                    if example.lower() in request_lower:
                        score += 3
                
                scores[module_name] = score
            
            # Находим модуль с максимальным счетом
            best_module = max(scores, key=scores.get)
            confidence = min(scores[best_module] / 5.0, 1.0)  # Нормализуем до 0-1
            
            # Если уверенность низкая, используем AI анализ
            if confidence < 0.3:
                return self._ai_analyze_request(user_request)
            
            context = {
                "user_request": user_request,
                "analysis_method": "keyword_matching",
                "scores": scores
            }
            
            logger.info(f"🎯 Быстрый анализ: {best_module} (confidence: {confidence:.2f})")
            return best_module, confidence, context
            
        except Exception as e:
            logger.error(f"❌ Ошибка анализа запроса: {e}")
            # Fallback на sequence_generator
            return "sequence_generator", 0.5, {"error": str(e)}
    
    def _ai_analyze_request(self, user_request: str) -> Tuple[str, float, Dict[str, Any]]:
        """
        AI анализ запроса (используется при низкой уверенности)
        """
        try:
            self._init_gemini_if_needed()
            
            prompt = f"""
Ты эксперт по выбору AI модулей. Проанализируй запрос пользователя и выбери лучший модуль.

ДОСТУПНЫЕ МОДУЛИ:
{self._format_modules_for_prompt()}

ЗАПРОС ПОЛЬЗОВАТЕЛЯ: "{user_request}"

Ответь в формате:
MODULE: [имя_модуля]
CONFIDENCE: [0.0-1.0]
REASON: [краткое объяснение]
"""
            
            response = self.gemini_api.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            result_text = response.text.strip()
            
            # Парсим ответ AI
            module_name = "sequence_generator"  # default
            confidence = 0.7
            reason = "AI анализ"
            
            for line in result_text.split('\n'):
                if line.startswith('MODULE:'):
                    module_name = line.split(':', 1)[1].strip()
                elif line.startswith('CONFIDENCE:'):
                    try:
                        confidence = float(line.split(':', 1)[1].strip())
                    except:
                        confidence = 0.7
                elif line.startswith('REASON:'):
                    reason = line.split(':', 1)[1].strip()
            
            context = {
                "user_request": user_request,
                "analysis_method": "ai_analysis",
                "ai_response": result_text,
                "reason": reason
            }
            
            logger.info(f"🤖 AI анализ: {module_name} (confidence: {confidence:.2f}) - {reason}")
            return module_name, confidence, context
            
        except Exception as e:
            logger.error(f"❌ Ошибка AI анализа: {e}")
            return "sequence_generator", 0.5, {"error": str(e)}
    
    def _format_modules_for_prompt(self) -> str:
        """Форматирует описания модулей для промпта"""
        formatted = []
        for name, info in self.MODULE_DESCRIPTIONS.items():
            examples_str = ", ".join(info["examples"][:2])  # Первые 2 примера
            formatted.append(f"- {name}: {info['description']} (примеры: {examples_str})")
        return "\n".join(formatted)
    
    def route_request(self, user_request: str) -> Dict[str, Any]:
        """
        Главная функция роутинга запроса
        
        Args:
            user_request: Запрос пользователя
            
        Returns:
            Dict с информацией о выбранном модуле и контексте
        """
        try:
            logger.info(f"🔍 Анализ запроса: '{user_request[:50]}...'")
            
            # Быстрый анализ
            module_name, confidence, context = self.analyze_user_request(user_request)
            
            # Проверяем существование модуля
            if module_name not in self.MODULE_DESCRIPTIONS:
                logger.warning(f"⚠️ Неизвестный модуль: {module_name}, используем sequence_generator")
                module_name = "sequence_generator"
                confidence = 0.5
            
            result = {
                "module": module_name,
                "confidence": confidence,
                "context": context,
                "module_info": self.MODULE_DESCRIPTIONS[module_name],
                "user_request": user_request
            }
            
            logger.info(f"✅ Роутинг завершен: {module_name} ({confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка роутинга: {e}")
            return {
                "module": "sequence_generator",
                "confidence": 0.5,
                "context": {"error": str(e)},
                "module_info": self.MODULE_DESCRIPTIONS["sequence_generator"],
                "user_request": user_request
            }

def quick_route(user_request: str) -> Dict[str, Any]:
    """
    Быстрая функция для роутинга запроса
    """
    router = SmartAIRouter()
    return router.route_request(user_request)

if __name__ == "__main__":
    # Тестирование роутера
    test_requests = [
        "открой калькулятор",
        "найди на YouTube видео про Python",
        "создай макрос для покупки товаров",
        "найди селекторы на странице",
        "обнови промпты"
    ]
    
    router = SmartAIRouter()
    
    for request in test_requests:
        print(f"\n🧪 Тест: '{request}'")
        result = router.route_request(request)
        print(f"   → Модуль: {result['module']}")
        print(f"   → Уверенность: {result['confidence']:.2f}")
        print(f"   → Метод: {result['context'].get('analysis_method', 'unknown')}")
