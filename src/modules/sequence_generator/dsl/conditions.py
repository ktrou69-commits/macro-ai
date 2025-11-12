"""
DSL конструкции для условной логики
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


class ConditionType(Enum):
    """Типы условий"""
    ELEMENT_EXISTS = "element_exists"
    PAGE_CONTAINS = "page_contains"
    VARIABLE_EQUALS = "variable_equals"
    VARIABLE_NOT_EQUALS = "variable_not_equals"
    ELEMENT_VISIBLE = "element_visible"
    ELEMENT_CLICKABLE = "element_clickable"
    URL_CONTAINS = "url_contains"
    TITLE_CONTAINS = "title_contains"


@dataclass
class Condition:
    """Базовый класс для условий"""
    condition_type: ConditionType
    parameters: Dict[str, Any]
    
    def __str__(self) -> str:
        if self.condition_type == ConditionType.ELEMENT_EXISTS:
            return f'element_exists "{self.parameters["selector"]}"'
        elif self.condition_type == ConditionType.PAGE_CONTAINS:
            return f'page_contains "{self.parameters["text"]}"'
        elif self.condition_type == ConditionType.VARIABLE_EQUALS:
            return f'${self.parameters["variable"]} == "{self.parameters["value"]}"'
        elif self.condition_type == ConditionType.ELEMENT_VISIBLE:
            return f'element_visible "{self.parameters["selector"]}"'
        elif self.condition_type == ConditionType.ELEMENT_CLICKABLE:
            return f'element_clickable "{self.parameters["selector"]}"'
        elif self.condition_type == ConditionType.URL_CONTAINS:
            return f'url_contains "{self.parameters["text"]}"'
        elif self.condition_type == ConditionType.TITLE_CONTAINS:
            return f'title_contains "{self.parameters["text"]}"'
        return str(self.parameters)


@dataclass
class ConditionalBlock:
    """Блок условной логики (if/else)"""
    condition: Condition
    if_block: List[str]
    else_block: Optional[List[str]] = None
    
    def __str__(self) -> str:
        result = [f"if {self.condition}"]
        for line in self.if_block:
            result.append(f"    {line}")
        
        if self.else_block:
            result.append("else")
            for line in self.else_block:
                result.append(f"    {line}")
        
        result.append("endif")
        return "\n".join(result)


class ConditionParser:
    """Парсер условий"""
    
    @staticmethod
    def parse_condition(condition_str: str) -> Condition:
        """
        Парсинг строки условия в объект Condition
        
        Args:
            condition_str: Строка условия, например 'element_exists "//button"'
            
        Returns:
            Объект Condition
        """
        condition_str = condition_str.strip()
        
        # element_exists "selector"
        if condition_str.startswith('element_exists'):
            selector = ConditionParser._extract_quoted_string(condition_str, 'element_exists')
            return Condition(
                condition_type=ConditionType.ELEMENT_EXISTS,
                parameters={"selector": selector}
            )
        
        # page_contains "text"
        elif condition_str.startswith('page_contains'):
            text = ConditionParser._extract_quoted_string(condition_str, 'page_contains')
            return Condition(
                condition_type=ConditionType.PAGE_CONTAINS,
                parameters={"text": text}
            )
        
        # element_visible "selector"
        elif condition_str.startswith('element_visible'):
            selector = ConditionParser._extract_quoted_string(condition_str, 'element_visible')
            return Condition(
                condition_type=ConditionType.ELEMENT_VISIBLE,
                parameters={"selector": selector}
            )
        
        # element_clickable "selector"
        elif condition_str.startswith('element_clickable'):
            selector = ConditionParser._extract_quoted_string(condition_str, 'element_clickable')
            return Condition(
                condition_type=ConditionType.ELEMENT_CLICKABLE,
                parameters={"selector": selector}
            )
        
        # url_contains "text"
        elif condition_str.startswith('url_contains'):
            text = ConditionParser._extract_quoted_string(condition_str, 'url_contains')
            return Condition(
                condition_type=ConditionType.URL_CONTAINS,
                parameters={"text": text}
            )
        
        # title_contains "text"
        elif condition_str.startswith('title_contains'):
            text = ConditionParser._extract_quoted_string(condition_str, 'title_contains')
            return Condition(
                condition_type=ConditionType.TITLE_CONTAINS,
                parameters={"text": text}
            )
        
        # $variable == "value"
        elif '==' in condition_str:
            parts = condition_str.split('==')
            if len(parts) == 2:
                variable = parts[0].strip().lstrip('$')
                value = parts[1].strip().strip('"')
                return Condition(
                    condition_type=ConditionType.VARIABLE_EQUALS,
                    parameters={"variable": variable, "value": value}
                )
        
        # $variable != "value"
        elif '!=' in condition_str:
            parts = condition_str.split('!=')
            if len(parts) == 2:
                variable = parts[0].strip().lstrip('$')
                value = parts[1].strip().strip('"')
                return Condition(
                    condition_type=ConditionType.VARIABLE_NOT_EQUALS,
                    parameters={"variable": variable, "value": value}
                )
        
        # Fallback - неизвестное условие
        return Condition(
            condition_type=ConditionType.PAGE_CONTAINS,
            parameters={"text": condition_str}
        )
    
    @staticmethod
    def _extract_quoted_string(text: str, prefix: str) -> str:
        """Извлечение строки в кавычках после префикса"""
        # Убираем префикс
        after_prefix = text[len(prefix):].strip()
        
        # Ищем строку в кавычках
        if after_prefix.startswith('"') and after_prefix.endswith('"'):
            return after_prefix[1:-1]
        elif after_prefix.startswith("'") and after_prefix.endswith("'"):
            return after_prefix[1:-1]
        else:
            # Если нет кавычек, берем все что после префикса
            return after_prefix


class ConditionEvaluator:
    """Оценщик условий"""
    
    def __init__(self, variables: Dict[str, Any] = None):
        self.variables = variables or {}
    
    def evaluate(self, condition: Condition) -> bool:
        """
        Оценка условия
        
        Args:
            condition: Условие для оценки
            
        Returns:
            True если условие выполнено, False иначе
        """
        if condition.condition_type == ConditionType.ELEMENT_EXISTS:
            return self._check_element_exists(condition.parameters["selector"])
        
        elif condition.condition_type == ConditionType.PAGE_CONTAINS:
            return self._check_page_contains(condition.parameters["text"])
        
        elif condition.condition_type == ConditionType.VARIABLE_EQUALS:
            var_name = condition.parameters["variable"]
            expected_value = condition.parameters["value"]
            actual_value = self.variables.get(var_name)
            return str(actual_value) == str(expected_value)
        
        elif condition.condition_type == ConditionType.VARIABLE_NOT_EQUALS:
            var_name = condition.parameters["variable"]
            expected_value = condition.parameters["value"]
            actual_value = self.variables.get(var_name)
            return str(actual_value) != str(expected_value)
        
        elif condition.condition_type == ConditionType.ELEMENT_VISIBLE:
            return self._check_element_visible(condition.parameters["selector"])
        
        elif condition.condition_type == ConditionType.ELEMENT_CLICKABLE:
            return self._check_element_clickable(condition.parameters["selector"])
        
        elif condition.condition_type == ConditionType.URL_CONTAINS:
            return self._check_url_contains(condition.parameters["text"])
        
        elif condition.condition_type == ConditionType.TITLE_CONTAINS:
            return self._check_title_contains(condition.parameters["text"])
        
        return False
    
    def _check_element_exists(self, selector: str) -> bool:
        """Проверка существования элемента (заглушка)"""
        # TODO: Интеграция с реальной проверкой элементов
        return True
    
    def _check_page_contains(self, text: str) -> bool:
        """Проверка наличия текста на странице (заглушка)"""
        # TODO: Интеграция с реальной проверкой содержимого страницы
        return True
    
    def _check_element_visible(self, selector: str) -> bool:
        """Проверка видимости элемента (заглушка)"""
        # TODO: Интеграция с реальной проверкой видимости
        return True
    
    def _check_element_clickable(self, selector: str) -> bool:
        """Проверка кликабельности элемента (заглушка)"""
        # TODO: Интеграция с реальной проверкой кликабельности
        return True
    
    def _check_url_contains(self, text: str) -> bool:
        """Проверка содержания текста в URL (заглушка)"""
        # TODO: Интеграция с реальной проверкой URL
        return True
    
    def _check_title_contains(self, text: str) -> bool:
        """Проверка содержания текста в заголовке (заглушка)"""
        # TODO: Интеграция с реальной проверкой заголовка
        return True


# Примеры использования
if __name__ == "__main__":
    # Тест парсинга условий
    conditions = [
        'element_exists "//button[@id=\'login\']"',
        'page_contains "Welcome back"',
        '$username == "admin"',
        'element_visible "//div[@class=\'modal\']"'
    ]
    
    for condition_str in conditions:
        condition = ConditionParser.parse_condition(condition_str)
        print(f"Parsed: {condition_str} -> {condition}")
    
    # Тест условного блока
    condition = Condition(
        condition_type=ConditionType.ELEMENT_EXISTS,
        parameters={"selector": "//button[@id='login']"}
    )
    
    conditional_block = ConditionalBlock(
        condition=condition,
        if_block=[
            'click "//button[@id=\'login\']"',
            'wait 2s',
            'type_in_field "//input[@name=\'username\']" "user@example.com"'
        ],
        else_block=[
            'click "//button[@id=\'signup\']"',
            'wait 2s'
        ]
    )
    
    print("\nGenerated conditional block:")
    print(conditional_block)
