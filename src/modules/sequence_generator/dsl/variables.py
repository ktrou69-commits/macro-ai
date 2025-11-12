"""
DSL система переменных и параметров
"""

from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass
from enum import Enum
import re


class VariableType(Enum):
    """Типы переменных"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"


@dataclass
class Variable:
    """Переменная DSL"""
    name: str
    value: Any
    var_type: VariableType
    is_parameter: bool = False
    default_value: Any = None
    description: Optional[str] = None
    
    def __str__(self) -> str:
        if self.is_parameter:
            return f"param {self.name} = {repr(self.value)}"
        else:
            return f"set {self.name} = {repr(self.value)}"


class VariableManager:
    """Менеджер переменных и параметров"""
    
    def __init__(self):
        self.variables: Dict[str, Variable] = {}
        self.parameters: Dict[str, Variable] = {}
    
    def set_variable(self, name: str, value: Any, var_type: VariableType = None) -> None:
        """
        Установка переменной
        
        Args:
            name: Имя переменной
            value: Значение переменной
            var_type: Тип переменной (автоопределение если None)
        """
        if var_type is None:
            var_type = self._infer_type(value)
        
        self.variables[name] = Variable(
            name=name,
            value=value,
            var_type=var_type,
            is_parameter=False
        )
    
    def set_parameter(self, name: str, default_value: Any, description: str = None) -> None:
        """
        Установка параметра макроса
        
        Args:
            name: Имя параметра
            default_value: Значение по умолчанию
            description: Описание параметра
        """
        var_type = self._infer_type(default_value)
        
        self.parameters[name] = Variable(
            name=name,
            value=default_value,
            var_type=var_type,
            is_parameter=True,
            default_value=default_value,
            description=description
        )
    
    def get_variable(self, name: str) -> Any:
        """
        Получение значения переменной
        
        Args:
            name: Имя переменной
            
        Returns:
            Значение переменной или None если не найдена
        """
        # Сначала ищем в переменных
        if name in self.variables:
            return self.variables[name].value
        
        # Потом в параметрах
        if name in self.parameters:
            return self.parameters[name].value
        
        return None
    
    def has_variable(self, name: str) -> bool:
        """Проверка существования переменной"""
        return name in self.variables or name in self.parameters
    
    def update_parameter(self, name: str, value: Any) -> bool:
        """
        Обновление значения параметра
        
        Args:
            name: Имя параметра
            value: Новое значение
            
        Returns:
            True если параметр обновлен, False если не найден
        """
        if name in self.parameters:
            # Проверяем совместимость типов
            expected_type = self.parameters[name].var_type
            actual_type = self._infer_type(value)
            
            if expected_type == actual_type or self._types_compatible(expected_type, actual_type):
                self.parameters[name].value = value
                return True
            else:
                print(f"Warning: Type mismatch for parameter '{name}'. Expected {expected_type}, got {actual_type}")
                return False
        
        return False
    
    def substitute_variables(self, text: str) -> str:
        """
        Подстановка переменных в тексте
        
        Args:
            text: Текст с переменными вида $variable_name
            
        Returns:
            Текст с подставленными значениями
        """
        # Находим все переменные в тексте
        variable_pattern = r'\$([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(variable_pattern, text)
        
        result = text
        for var_name in matches:
            value = self.get_variable(var_name)
            if value is not None:
                # Заменяем $variable_name на значение
                result = result.replace(f'${var_name}', str(value))
            else:
                print(f"Warning: Variable '${var_name}' not found")
        
        return result
    
    def get_all_variables(self) -> Dict[str, Any]:
        """Получение всех переменных и параметров"""
        result = {}
        
        for name, var in self.variables.items():
            result[name] = var.value
        
        for name, param in self.parameters.items():
            result[name] = param.value
        
        return result
    
    def get_parameters_info(self) -> List[Dict[str, Any]]:
        """Получение информации о параметрах для документации"""
        return [
            {
                "name": param.name,
                "type": param.var_type.value,
                "default_value": param.default_value,
                "description": param.description or f"Parameter {param.name}"
            }
            for param in self.parameters.values()
        ]
    
    def clear_variables(self) -> None:
        """Очистка всех переменных (параметры остаются)"""
        self.variables.clear()
    
    def reset_parameters(self) -> None:
        """Сброс параметров к значениям по умолчанию"""
        for param in self.parameters.values():
            param.value = param.default_value
    
    def _infer_type(self, value: Any) -> VariableType:
        """Автоопределение типа переменной"""
        if isinstance(value, bool):
            return VariableType.BOOLEAN
        elif isinstance(value, int):
            return VariableType.INTEGER
        elif isinstance(value, float):
            return VariableType.FLOAT
        elif isinstance(value, list):
            return VariableType.LIST
        elif isinstance(value, dict):
            return VariableType.DICT
        else:
            return VariableType.STRING
    
    def _types_compatible(self, type1: VariableType, type2: VariableType) -> bool:
        """Проверка совместимости типов"""
        # Числовые типы совместимы между собой
        numeric_types = {VariableType.INTEGER, VariableType.FLOAT}
        if type1 in numeric_types and type2 in numeric_types:
            return True
        
        # Строки совместимы с любыми типами (приведение к строке)
        if type1 == VariableType.STRING or type2 == VariableType.STRING:
            return True
        
        return type1 == type2


class VariableParser:
    """Парсер переменных и параметров"""
    
    @staticmethod
    def parse_variable_declaration(line: str) -> Optional[Dict[str, Any]]:
        """
        Парсинг объявления переменной
        
        Args:
            line: Строка с объявлением переменной
            
        Returns:
            Словарь с информацией о переменной или None
        """
        line = line.strip()
        
        # set variable_name = "value"
        if line.startswith("set "):
            return VariableParser._parse_assignment(line[4:], is_parameter=False)
        
        # param parameter_name = "default_value"
        elif line.startswith("param "):
            return VariableParser._parse_assignment(line[6:], is_parameter=True)
        
        return None
    
    @staticmethod
    def _parse_assignment(assignment: str, is_parameter: bool) -> Optional[Dict[str, Any]]:
        """Парсинг присваивания переменной"""
        if "=" not in assignment:
            return None
        
        parts = assignment.split("=", 1)
        if len(parts) != 2:
            return None
        
        name = parts[0].strip()
        value_str = parts[1].strip()
        
        # Парсим значение
        value = VariableParser._parse_value(value_str)
        
        return {
            "name": name,
            "value": value,
            "is_parameter": is_parameter
        }
    
    @staticmethod
    def _parse_value(value_str: str) -> Any:
        """Парсинг значения переменной"""
        value_str = value_str.strip()
        
        # Строка в кавычках
        if (value_str.startswith('"') and value_str.endswith('"')) or \
           (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]
        
        # Булево значение
        if value_str.lower() in ("true", "false"):
            return value_str.lower() == "true"
        
        # Число с плавающей точкой
        if "." in value_str:
            try:
                return float(value_str)
            except ValueError:
                pass
        
        # Целое число
        try:
            return int(value_str)
        except ValueError:
            pass
        
        # Список (простой формат)
        if value_str.startswith("[") and value_str.endswith("]"):
            try:
                # Простой парсинг списка строк
                content = value_str[1:-1].strip()
                if not content:
                    return []
                
                items = [item.strip().strip('"\'') for item in content.split(",")]
                return items
            except:
                pass
        
        # По умолчанию - строка
        return value_str


class VariableValidator:
    """Валидатор переменных"""
    
    @staticmethod
    def validate_variable_name(name: str) -> List[str]:
        """
        Валидация имени переменной
        
        Args:
            name: Имя переменной
            
        Returns:
            Список ошибок
        """
        errors = []
        
        if not name:
            errors.append("Имя переменной не может быть пустым")
            return errors
        
        # Проверка на допустимые символы
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', name):
            errors.append(f"Недопустимое имя переменной '{name}'. Используйте только буквы, цифры и подчеркивания")
        
        # Проверка на зарезервированные слова
        reserved_words = {
            "if", "else", "endif", "while", "end_while", "repeat", "end_repeat",
            "for_each", "end_for", "break", "continue", "set", "param"
        }
        
        if name.lower() in reserved_words:
            errors.append(f"'{name}' является зарезервированным словом")
        
        # Проверка длины
        if len(name) > 50:
            errors.append(f"Имя переменной '{name}' слишком длинное (максимум 50 символов)")
        
        return errors
    
    @staticmethod
    def validate_variable_usage(text: str, available_variables: set) -> List[str]:
        """
        Валидация использования переменных в тексте
        
        Args:
            text: Текст с переменными
            available_variables: Множество доступных переменных
            
        Returns:
            Список предупреждений
        """
        warnings = []
        
        # Находим все использования переменных
        variable_pattern = r'\$([a-zA-Z_][a-zA-Z0-9_]*)'
        matches = re.findall(variable_pattern, text)
        
        for var_name in set(matches):  # Убираем дубликаты
            if var_name not in available_variables:
                warnings.append(f"Переменная '${var_name}' не объявлена")
        
        return warnings


# Примеры использования
if __name__ == "__main__":
    # Тест менеджера переменных
    vm = VariableManager()
    
    # Установка переменных
    vm.set_variable("search_term", "Python tutorial")
    vm.set_variable("max_results", 5)
    vm.set_parameter("username", "default_user", "Username for login")
    
    print("Variables:", vm.get_all_variables())
    print("Parameters info:", vm.get_parameters_info())
    
    # Тест подстановки
    text = 'Search for "$search_term" with max $max_results results for user $username'
    substituted = vm.substitute_variables(text)
    print(f"Original: {text}")
    print(f"Substituted: {substituted}")
    
    # Тест парсинга
    declarations = [
        'set search_term = "Python tutorial"',
        'param username = "admin"',
        'set count = 42',
        'set enabled = true'
    ]
    
    for decl in declarations:
        parsed = VariableParser.parse_variable_declaration(decl)
        print(f"Parsed: {decl} -> {parsed}")
    
    # Тест валидации
    invalid_names = ["123invalid", "if", "my-variable", ""]
    for name in invalid_names:
        errors = VariableValidator.validate_variable_name(name)
        if errors:
            print(f"Validation errors for '{name}': {errors}")
