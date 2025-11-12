"""
DSL конструкции для циклов и повторений
"""

from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
from .conditions import Condition, ConditionParser


class LoopType(Enum):
    """Типы циклов"""
    REPEAT = "repeat"
    WHILE = "while"
    FOR_EACH = "for_each"


@dataclass
class LoopBlock:
    """Базовый класс для циклов"""
    loop_type: LoopType
    body: List[str]
    
    def __str__(self) -> str:
        return f"{self.loop_type.value} loop with {len(self.body)} commands"


@dataclass
class RepeatLoop(LoopBlock):
    """Цикл с фиксированным количеством повторений"""
    count: int
    
    def __init__(self, count: int, body: List[str]):
        super().__init__(LoopType.REPEAT, body)
        self.count = count
    
    def __str__(self) -> str:
        result = [f"repeat {self.count} times"]
        for line in self.body:
            result.append(f"    {line}")
        result.append("end_repeat")
        return "\n".join(result)


@dataclass
class WhileLoop(LoopBlock):
    """Цикл с условием"""
    condition: Condition
    
    def __init__(self, condition: Condition, body: List[str]):
        super().__init__(LoopType.WHILE, body)
        self.condition = condition
    
    def __str__(self) -> str:
        result = [f"while {self.condition}"]
        for line in self.body:
            result.append(f"    {line}")
        result.append("end_while")
        return "\n".join(result)


@dataclass
class ForEachLoop(LoopBlock):
    """Цикл по элементам"""
    selector: str
    variable_name: str
    
    def __init__(self, selector: str, variable_name: str, body: List[str]):
        super().__init__(LoopType.FOR_EACH, body)
        self.selector = selector
        self.variable_name = variable_name
    
    def __str__(self) -> str:
        result = [f'for_each "{self.selector}" as {self.variable_name}']
        for line in self.body:
            result.append(f"    {line}")
        result.append("end_for")
        return "\n".join(result)


class LoopParser:
    """Парсер циклов"""
    
    @staticmethod
    def parse_loop_header(header_line: str) -> Dict[str, Any]:
        """
        Парсинг заголовка цикла
        
        Args:
            header_line: Строка заголовка цикла
            
        Returns:
            Словарь с информацией о цикле
        """
        header_line = header_line.strip()
        
        # repeat N times
        if header_line.startswith("repeat") and "times" in header_line:
            # Извлекаем число
            parts = header_line.split()
            for part in parts:
                if part.isdigit():
                    return {
                        "type": LoopType.REPEAT,
                        "count": int(part)
                    }
        
        # while condition
        elif header_line.startswith("while"):
            condition_str = header_line[5:].strip()  # Убираем "while"
            condition = ConditionParser.parse_condition(condition_str)
            return {
                "type": LoopType.WHILE,
                "condition": condition
            }
        
        # for_each "selector" as variable
        elif header_line.startswith("for_each"):
            # Парсим: for_each "//div[@class='item']" as item
            parts = header_line.split()
            selector = None
            variable_name = None
            
            # Ищем селектор в кавычках
            for i, part in enumerate(parts):
                if part.startswith('"') and part.endswith('"'):
                    selector = part[1:-1]
                elif part == "as" and i + 1 < len(parts):
                    variable_name = parts[i + 1]
            
            if selector and variable_name:
                return {
                    "type": LoopType.FOR_EACH,
                    "selector": selector,
                    "variable_name": variable_name
                }
        
        return {"type": None}
    
    @staticmethod
    def create_loop(loop_info: Dict[str, Any], body: List[str]) -> Optional[LoopBlock]:
        """
        Создание объекта цикла
        
        Args:
            loop_info: Информация о цикле из parse_loop_header
            body: Тело цикла (список команд)
            
        Returns:
            Объект цикла или None
        """
        loop_type = loop_info.get("type")
        
        if loop_type == LoopType.REPEAT:
            count = loop_info.get("count", 1)
            return RepeatLoop(count, body)
        
        elif loop_type == LoopType.WHILE:
            condition = loop_info.get("condition")
            if condition:
                return WhileLoop(condition, body)
        
        elif loop_type == LoopType.FOR_EACH:
            selector = loop_info.get("selector")
            variable_name = loop_info.get("variable_name")
            if selector and variable_name:
                return ForEachLoop(selector, variable_name, body)
        
        return None


class LoopExecutor:
    """Исполнитель циклов"""
    
    def __init__(self, variables: Dict[str, Any] = None):
        self.variables = variables or {}
        self.break_requested = False
        self.continue_requested = False
    
    def execute_loop(self, loop: LoopBlock) -> bool:
        """
        Выполнение цикла
        
        Args:
            loop: Объект цикла для выполнения
            
        Returns:
            True если выполнение успешно, False иначе
        """
        self.break_requested = False
        self.continue_requested = False
        
        if isinstance(loop, RepeatLoop):
            return self._execute_repeat_loop(loop)
        elif isinstance(loop, WhileLoop):
            return self._execute_while_loop(loop)
        elif isinstance(loop, ForEachLoop):
            return self._execute_foreach_loop(loop)
        
        return False
    
    def _execute_repeat_loop(self, loop: RepeatLoop) -> bool:
        """Выполнение цикла repeat"""
        for i in range(loop.count):
            if self.break_requested:
                break
            
            # Устанавливаем переменную счетчика
            self.variables["_loop_counter"] = i + 1
            
            success = self._execute_loop_body(loop.body)
            if not success and not self.continue_requested:
                return False
            
            self.continue_requested = False
        
        return True
    
    def _execute_while_loop(self, loop: WhileLoop) -> bool:
        """Выполнение цикла while"""
        from .conditions import ConditionEvaluator
        
        evaluator = ConditionEvaluator(self.variables)
        iteration = 0
        max_iterations = 1000  # Защита от бесконечного цикла
        
        while evaluator.evaluate(loop.condition) and iteration < max_iterations:
            if self.break_requested:
                break
            
            self.variables["_loop_iteration"] = iteration + 1
            
            success = self._execute_loop_body(loop.body)
            if not success and not self.continue_requested:
                return False
            
            self.continue_requested = False
            iteration += 1
        
        if iteration >= max_iterations:
            print(f"Warning: While loop exceeded maximum iterations ({max_iterations})")
        
        return True
    
    def _execute_foreach_loop(self, loop: ForEachLoop) -> bool:
        """Выполнение цикла for_each"""
        # TODO: Интеграция с реальным поиском элементов
        # Пока используем заглушку
        elements = self._find_elements(loop.selector)
        
        for i, element in enumerate(elements):
            if self.break_requested:
                break
            
            # Устанавливаем переменную элемента
            self.variables[loop.variable_name] = element
            self.variables["_loop_index"] = i
            
            success = self._execute_loop_body(loop.body)
            if not success and not self.continue_requested:
                return False
            
            self.continue_requested = False
        
        return True
    
    def _execute_loop_body(self, body: List[str]) -> bool:
        """Выполнение тела цикла"""
        for command in body:
            command = command.strip()
            
            # Обработка команд управления циклом
            if command == "break":
                self.break_requested = True
                return True
            elif command == "continue":
                self.continue_requested = True
                return True
            
            # TODO: Выполнение обычных команд DSL
            # Пока просто логируем
            print(f"Executing: {command}")
        
        return True
    
    def _find_elements(self, selector: str) -> List[str]:
        """Поиск элементов по селектору (заглушка)"""
        # TODO: Интеграция с реальным поиском элементов
        # Возвращаем заглушку
        return [f"element_{i}" for i in range(3)]


class LoopValidator:
    """Валидатор циклов"""
    
    @staticmethod
    def validate_loop(loop: LoopBlock) -> List[str]:
        """
        Валидация цикла
        
        Args:
            loop: Цикл для валидации
            
        Returns:
            Список предупреждений
        """
        warnings = []
        
        if isinstance(loop, RepeatLoop):
            if loop.count <= 0:
                warnings.append("Количество повторений должно быть больше 0")
            elif loop.count > 100:
                warnings.append(f"Большое количество повторений ({loop.count}) может замедлить выполнение")
        
        elif isinstance(loop, WhileLoop):
            # Проверяем, что в теле цикла есть команды, которые могут изменить условие
            has_condition_modifiers = any(
                "click" in cmd or "type" in cmd or "navigate" in cmd 
                for cmd in loop.body
            )
            if not has_condition_modifiers:
                warnings.append("While цикл может стать бесконечным - нет команд, изменяющих условие")
        
        elif isinstance(loop, ForEachLoop):
            if not loop.selector:
                warnings.append("Селектор для for_each не может быть пустым")
            elif not loop.variable_name:
                warnings.append("Имя переменной для for_each не может быть пустым")
        
        # Проверка тела цикла
        if not loop.body:
            warnings.append("Тело цикла не может быть пустым")
        elif len(loop.body) > 50:
            warnings.append(f"Большое тело цикла ({len(loop.body)} команд) может быть сложным для отладки")
        
        return warnings


# Примеры использования
if __name__ == "__main__":
    # Тест парсинга циклов
    loop_headers = [
        "repeat 3 times",
        'while element_exists "//button[@class=\'load-more\']"',
        'for_each "//div[@class=\'item\']" as item'
    ]
    
    for header in loop_headers:
        loop_info = LoopParser.parse_loop_header(header)
        print(f"Parsed: {header} -> {loop_info}")
    
    # Тест создания циклов
    repeat_loop = RepeatLoop(
        count=3,
        body=[
            'click "//button[@class=\'next\']"',
            'wait 2s'
        ]
    )
    
    print(f"\nRepeat loop:\n{repeat_loop}")
    
    # Тест валидации
    warnings = LoopValidator.validate_loop(repeat_loop)
    if warnings:
        print(f"Warnings: {warnings}")
    else:
        print("No warnings for repeat loop")
