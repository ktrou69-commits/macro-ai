"""
Селектор модулей на основе намерений пользователя
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass

from .intent_analyzer import UserIntent
from ..base.ai_module import AIModule


@dataclass
class ModuleMatch:
    """Соответствие модуля запросу"""
    module_name: str
    score: float
    reasons: List[str]
    confidence: float


class ModuleSelector:
    """Селектор подходящего модуля для выполнения запроса"""
    
    def __init__(self):
        self.registered_modules = {}
        self.module_configs = {}
    
    def register_module(self, module_name: str, module_class, config: Dict[str, Any]):
        """
        Регистрация модуля
        
        Args:
            module_name: Имя модуля
            module_class: Класс модуля
            config: Конфигурация модуля
        """
        self.registered_modules[module_name] = {
            "class": module_class,
            "config": config,
            "enabled": config.get("enabled", True),
            "priority": config.get("priority", 5),
            "keywords": config.get("keywords", []),
            "description": config.get("description", "")
        }
        
        self.module_configs[module_name] = config
    
    def select_module(self, intent: UserIntent) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Выбор подходящего модуля на основе намерений
        
        Args:
            intent: Намерения пользователя
            
        Returns:
            Кортеж (имя_модуля, конфигурация) или None
        """
        if intent.type == "chat":
            return None  # Обычный чат, модуль не нужен
        
        # Получаем все возможные соответствия
        matches = self._calculate_module_matches(intent)
        
        if not matches:
            return None
        
        # Сортируем по скору
        matches.sort(key=lambda x: x.score, reverse=True)
        
        # Возвращаем лучшее соответствие
        best_match = matches[0]
        
        if best_match.score < 0.3:  # Минимальный порог
            return None
        
        return best_match.module_name, self.module_configs[best_match.module_name]
    
    def _calculate_module_matches(self, intent: UserIntent) -> List[ModuleMatch]:
        """Вычисление соответствий модулей"""
        matches = []
        
        for module_name, module_info in self.registered_modules.items():
            if not module_info["enabled"]:
                continue
            
            score, reasons = self._calculate_module_score(intent, module_info)
            
            if score > 0:
                match = ModuleMatch(
                    module_name=module_name,
                    score=score,
                    reasons=reasons,
                    confidence=min(score, intent.confidence)
                )
                matches.append(match)
        
        return matches
    
    def _calculate_module_score(self, intent: UserIntent, 
                               module_info: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Вычисление скора соответствия модуля"""
        score = 0.0
        reasons = []
        
        keywords = module_info.get("keywords", [])
        priority = module_info.get("priority", 5)
        
        # Базовый скор на основе приоритета (инвертируем: 0 = высший приоритет)
        base_score = (10 - priority) / 10
        score += base_score * 0.2
        
        # Соответствие ключевых слов
        keyword_matches = 0
        for keyword in keywords:
            if self._keyword_matches_intent(keyword.lower(), intent):
                keyword_matches += 1
                reasons.append(f"Ключевое слово: {keyword}")
        
        if keyword_matches > 0:
            keyword_score = min(keyword_matches / len(keywords), 1.0)
            score += keyword_score * 0.4
        
        # Соответствие типу намерения
        if intent.type == "automation":
            # Модули автоматизации получают бонус
            automation_modules = ["sequence_generator", "variable_creator", "dom_extractor"]
            if module_info.get("name") in automation_modules:
                score += 0.3
                reasons.append("Модуль автоматизации")
        
        # Соответствие платформам
        if intent.platforms:
            platform_score = self._calculate_platform_score(intent.platforms, keywords)
            score += platform_score * 0.2
            if platform_score > 0:
                reasons.append(f"Платформы: {', '.join(intent.platforms)}")
        
        # Соответствие действиям
        if intent.actions:
            action_score = self._calculate_action_score(intent.actions, keywords)
            score += action_score * 0.1
            if action_score > 0:
                reasons.append(f"Действия: {', '.join(intent.actions)}")
        
        return min(score, 1.0), reasons
    
    def _keyword_matches_intent(self, keyword: str, intent: UserIntent) -> bool:
        """Проверка соответствия ключевого слова намерениям"""
        # Проверяем в ключевых словах намерения
        if keyword in [kw.lower() for kw in intent.keywords]:
            return True
        
        # Проверяем в платформах
        if keyword in intent.platforms:
            return True
        
        # Проверяем в действиях
        if keyword in intent.actions:
            return True
        
        # Проверяем в приложениях
        if keyword in intent.apps:
            return True
        
        # Частичное соответствие
        for intent_keyword in intent.keywords:
            if keyword in intent_keyword.lower() or intent_keyword.lower() in keyword:
                return True
        
        return False
    
    def _calculate_platform_score(self, platforms: List[str], keywords: List[str]) -> float:
        """Вычисление скора соответствия платформ"""
        if not platforms:
            return 0.0
        
        matches = 0
        for platform in platforms:
            if platform in [kw.lower() for kw in keywords]:
                matches += 1
        
        return matches / len(platforms)
    
    def _calculate_action_score(self, actions: List[str], keywords: List[str]) -> float:
        """Вычисление скора соответствия действий"""
        if not actions:
            return 0.0
        
        matches = 0
        for action in actions:
            if action in [kw.lower() for kw in keywords]:
                matches += 1
        
        return matches / len(actions)
    
    def get_all_modules(self) -> Dict[str, Dict[str, Any]]:
        """Получение всех зарегистрированных модулей"""
        return self.registered_modules.copy()
    
    def get_module_info(self, module_name: str) -> Optional[Dict[str, Any]]:
        """Получение информации о модуле"""
        return self.registered_modules.get(module_name)
    
    def enable_module(self, module_name: str):
        """Включение модуля"""
        if module_name in self.registered_modules:
            self.registered_modules[module_name]["enabled"] = True
    
    def disable_module(self, module_name: str):
        """Отключение модуля"""
        if module_name in self.registered_modules:
            self.registered_modules[module_name]["enabled"] = False
    
    def get_selection_explanation(self, intent: UserIntent, 
                                 selected_module: Optional[str]) -> str:
        """Получение объяснения выбора модуля"""
        if not selected_module:
            return "Модуль не выбран - запрос определен как обычный чат"
        
        matches = self._calculate_module_matches(intent)
        selected_match = next((m for m in matches if m.module_name == selected_module), None)
        
        if not selected_match:
            return f"Модуль {selected_module} выбран по умолчанию"
        
        explanation = f"Выбран модуль '{selected_module}' (скор: {selected_match.score:.2f})\n"
        explanation += "Причины:\n"
        for reason in selected_match.reasons:
            explanation += f"- {reason}\n"
        
        return explanation
