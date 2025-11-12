"""
Анализатор намерений пользователя
"""

import re
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class UserIntent:
    """Намерения пользователя"""
    type: str  # automation, chat, question
    platforms: List[str]  # chrome, tiktok, youtube
    actions: List[str]  # open, click, type, search
    apps: List[str]  # chrome, calculator, terminal
    complexity: str  # simple, medium, complex
    confidence: float  # 0.0 - 1.0
    keywords: List[str]  # ключевые слова из запроса


class IntentAnalyzer:
    """Анализатор намерений пользователя"""
    
    def __init__(self):
        # Словари для анализа
        self.automation_keywords = [
            "открой", "запусти", "кликни", "найди", "создай", "сделай",
            "перейди", "введи", "нажми", "скролль", "закрой", "переключи"
        ]
        
        self.chat_keywords = [
            "привет", "как дела", "что умеешь", "помоги", "расскажи",
            "объясни", "покажи", "научи", "спасибо", "пока"
        ]
        
        self.platforms = {
            "chrome": ["хром", "chrome", "браузер", "browser"],
            "tiktok": ["тикток", "tiktok", "тик ток"],
            "youtube": ["ютуб", "youtube", "ютюб"],
            "instagram": ["инстаграм", "instagram", "инста"],
            "telegram": ["телеграм", "telegram", "тг"]
        }
        
        self.apps = {
            "chrome": ["хром", "chrome", "браузер"],
            "calculator": ["калькулятор", "calculator", "calc"],
            "terminal": ["терминал", "terminal", "консоль"],
            "finder": ["finder", "файндер", "проводник"],
            "safari": ["safari", "сафари"]
        }
        
        self.actions = {
            "open": ["открой", "запусти", "включи"],
            "click": ["кликни", "нажми", "тапни"],
            "type": ["введи", "напиши", "набери"],
            "search": ["найди", "поищи", "ищи"],
            "scroll": ["скролль", "прокрути", "листай"],
            "close": ["закрой", "выключи", "заверши"]
        }
    
    def analyze(self, user_input: str) -> UserIntent:
        """
        Анализ намерений пользователя
        
        Args:
            user_input: Ввод пользователя
            
        Returns:
            Объект с намерениями пользователя
        """
        user_lower = user_input.lower()
        
        # Определяем тип запроса
        intent_type = self._determine_type(user_lower)
        
        # Извлекаем компоненты
        platforms = self._extract_platforms(user_lower)
        actions = self._extract_actions(user_lower)
        apps = self._extract_apps(user_lower)
        keywords = self._extract_keywords(user_lower)
        
        # Определяем сложность
        complexity = self._determine_complexity(user_input, platforms, actions, apps)
        
        # Вычисляем уверенность
        confidence = self._calculate_confidence(intent_type, platforms, actions, apps)
        
        return UserIntent(
            type=intent_type,
            platforms=platforms,
            actions=actions,
            apps=apps,
            complexity=complexity,
            confidence=confidence,
            keywords=keywords
        )
    
    def _determine_type(self, user_input: str) -> str:
        """Определение типа запроса"""
        # Проверяем на автоматизацию
        automation_score = sum(1 for keyword in self.automation_keywords 
                             if keyword in user_input)
        
        # Проверяем на чат
        chat_score = sum(1 for keyword in self.chat_keywords 
                        if keyword in user_input)
        
        # Проверяем на вопрос
        question_indicators = ["как", "что", "где", "когда", "почему", "зачем", "?"]
        question_score = sum(1 for indicator in question_indicators 
                           if indicator in user_input)
        
        # Определяем тип по максимальному скору
        if automation_score > max(chat_score, question_score):
            return "automation"
        elif question_score > chat_score:
            return "question"
        else:
            return "chat"
    
    def _extract_platforms(self, user_input: str) -> List[str]:
        """Извлечение платформ из запроса"""
        found_platforms = []
        
        for platform, keywords in self.platforms.items():
            if any(keyword in user_input for keyword in keywords):
                found_platforms.append(platform)
        
        return found_platforms
    
    def _extract_actions(self, user_input: str) -> List[str]:
        """Извлечение действий из запроса"""
        found_actions = []
        
        for action, keywords in self.actions.items():
            if any(keyword in user_input for keyword in keywords):
                found_actions.append(action)
        
        return found_actions
    
    def _extract_apps(self, user_input: str) -> List[str]:
        """Извлечение приложений из запроса"""
        found_apps = []
        
        for app, keywords in self.apps.items():
            if any(keyword in user_input for keyword in keywords):
                found_apps.append(app)
        
        return found_apps
    
    def _extract_keywords(self, user_input: str) -> List[str]:
        """Извлечение ключевых слов"""
        # Простое извлечение слов (можно улучшить)
        words = re.findall(r'\b\w+\b', user_input)
        
        # Фильтруем стоп-слова
        stop_words = {"и", "в", "на", "с", "по", "для", "от", "до", "из", "к", "о"}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:10]  # Ограничиваем количество
    
    def _determine_complexity(self, user_input: str, platforms: List[str], 
                            actions: List[str], apps: List[str]) -> str:
        """Определение сложности запроса"""
        # Факторы сложности
        word_count = len(user_input.split())
        component_count = len(platforms) + len(actions) + len(apps)
        
        # Сложные индикаторы
        complex_indicators = ["если", "когда", "после", "перед", "пока", "повтори"]
        has_complex_logic = any(indicator in user_input.lower() 
                              for indicator in complex_indicators)
        
        # Определяем сложность
        if has_complex_logic or component_count > 3 or word_count > 15:
            return "complex"
        elif component_count > 1 or word_count > 8:
            return "medium"
        else:
            return "simple"
    
    def _calculate_confidence(self, intent_type: str, platforms: List[str], 
                            actions: List[str], apps: List[str]) -> float:
        """Вычисление уверенности в анализе"""
        confidence = 0.5  # Базовая уверенность
        
        # Увеличиваем уверенность за найденные компоненты
        if intent_type == "automation":
            confidence += 0.2
            if platforms:
                confidence += 0.1
            if actions:
                confidence += 0.1
            if apps:
                confidence += 0.1
        
        # Ограничиваем диапазон
        return min(1.0, max(0.1, confidence))
    
    def get_intent_summary(self, intent: UserIntent) -> str:
        """Получение краткого описания намерений"""
        summary_parts = [f"Тип: {intent.type}"]
        
        if intent.platforms:
            summary_parts.append(f"Платформы: {', '.join(intent.platforms)}")
        
        if intent.actions:
            summary_parts.append(f"Действия: {', '.join(intent.actions)}")
        
        if intent.apps:
            summary_parts.append(f"Приложения: {', '.join(intent.apps)}")
        
        summary_parts.append(f"Сложность: {intent.complexity}")
        summary_parts.append(f"Уверенность: {intent.confidence:.2f}")
        
        return " | ".join(summary_parts)
