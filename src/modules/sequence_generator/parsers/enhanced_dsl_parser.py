"""
Расширенный DSL парсер с поддержкой условий, циклов и переменных
"""

from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import logging

from ..dsl.conditions import Condition, ConditionalBlock, ConditionParser
from ..dsl.loops import LoopBlock, RepeatLoop, WhileLoop, ForEachLoop, LoopParser
from ..dsl.variables import VariableManager, VariableParser, VariableValidator

logger = logging.getLogger(__name__)


class BlockType(Enum):
    """Типы блоков DSL"""
    COMMAND = "command"
    CONDITIONAL = "conditional"
    LOOP = "loop"
    VARIABLE_DECLARATION = "variable_declaration"
    COMMENT = "comment"


@dataclass
class DSLBlock:
    """Базовый блок DSL"""
    block_type: BlockType
    content: Any
    line_number: int
    raw_lines: List[str]


@dataclass
class ParsedDSL:
    """Результат парсинга DSL"""
    blocks: List[DSLBlock]
    variables: VariableManager
    errors: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]


class EnhancedDSLParser:
    """Расширенный парсер DSL с поддержкой условий, циклов и переменных"""
    
    def __init__(self):
        self.variable_manager = VariableManager()
        self.errors = []
        self.warnings = []
        self.current_line = 0
        
        # Ключевые слова для определения блоков
        self.conditional_keywords = {"if"}
        self.loop_keywords = {"repeat", "while", "for_each"}
        self.variable_keywords = {"set", "param"}
        self.block_end_keywords = {
            "endif", "else", 
            "end_repeat", "end_while", "end_for"
        }
    
    def parse(self, dsl_code: str) -> ParsedDSL:
        """
        Парсинг DSL кода
        
        Args:
            dsl_code: DSL код для парсинга
            
        Returns:
            Результат парсинга
        """
        self._reset_state()
        
        lines = self._preprocess_lines(dsl_code)
        blocks = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if not line or line.startswith('#'):
                # Комментарий или пустая строка
                if line.startswith('#'):
                    blocks.append(DSLBlock(
                        block_type=BlockType.COMMENT,
                        content=line,
                        line_number=i + 1,
                        raw_lines=[line]
                    ))
                i += 1
                continue
            
            try:
                block, next_i = self._parse_block(lines, i)
                if block:
                    blocks.append(block)
                i = next_i
                
            except Exception as e:
                self.errors.append(f"Строка {i + 1}: Ошибка парсинга - {str(e)}")
                i += 1
        
        # Валидация переменных
        self._validate_variable_usage(blocks)
        
        return ParsedDSL(
            blocks=blocks,
            variables=self.variable_manager,
            errors=self.errors,
            warnings=self.warnings,
            metadata={
                "total_blocks": len(blocks),
                "has_conditionals": any(b.block_type == BlockType.CONDITIONAL for b in blocks),
                "has_loops": any(b.block_type == BlockType.LOOP for b in blocks),
                "variable_count": len(self.variable_manager.get_all_variables())
            }
        )
    
    def _reset_state(self):
        """Сброс состояния парсера"""
        self.variable_manager = VariableManager()
        self.errors = []
        self.warnings = []
        self.current_line = 0
    
    def _preprocess_lines(self, dsl_code: str) -> List[str]:
        """Предобработка строк DSL"""
        lines = dsl_code.split('\n')
        
        # Убираем лишние пробелы и нормализуем
        processed_lines = []
        for line in lines:
            # Сохраняем отступы, но убираем trailing spaces
            processed_line = line.rstrip()
            processed_lines.append(processed_line)
        
        return processed_lines
    
    def _parse_block(self, lines: List[str], start_i: int) -> Tuple[Optional[DSLBlock], int]:
        """
        Парсинг одного блока DSL
        
        Args:
            lines: Все строки DSL
            start_i: Индекс начальной строки
            
        Returns:
            Tuple (блок, индекс следующей строки)
        """
        line = lines[start_i].strip()
        first_word = line.split()[0] if line.split() else ""
        
        # Условный блок
        if first_word in self.conditional_keywords:
            return self._parse_conditional_block(lines, start_i)
        
        # Цикл
        elif first_word in self.loop_keywords:
            return self._parse_loop_block(lines, start_i)
        
        # Объявление переменной
        elif first_word in self.variable_keywords:
            return self._parse_variable_declaration(lines, start_i)
        
        # Обычная команда
        else:
            return self._parse_command(lines, start_i)
    
    def _parse_conditional_block(self, lines: List[str], start_i: int) -> Tuple[Optional[DSLBlock], int]:
        """Парсинг условного блока"""
        if_line = lines[start_i].strip()
        
        # Парсим условие
        condition_str = if_line[2:].strip()  # Убираем "if"
        try:
            condition = ConditionParser.parse_condition(condition_str)
        except Exception as e:
            self.errors.append(f"Строка {start_i + 1}: Ошибка парсинга условия - {str(e)}")
            return None, start_i + 1
        
        # Парсим тело if блока
        if_body = []
        else_body = []
        current_body = if_body
        
        i = start_i + 1
        block_lines = [if_line]
        
        while i < len(lines):
            line = lines[i].strip()
            block_lines.append(lines[i])
            
            if line == "else":
                current_body = else_body
            elif line == "endif":
                break
            elif line and not line.startswith('#'):
                current_body.append(line)
            
            i += 1
        
        if i >= len(lines):
            self.errors.append(f"Строка {start_i + 1}: Незакрытый if блок")
            return None, len(lines)
        
        conditional_block = ConditionalBlock(
            condition=condition,
            if_block=if_body,
            else_block=else_body if else_body else None
        )
        
        return DSLBlock(
            block_type=BlockType.CONDITIONAL,
            content=conditional_block,
            line_number=start_i + 1,
            raw_lines=block_lines
        ), i + 1
    
    def _parse_loop_block(self, lines: List[str], start_i: int) -> Tuple[Optional[DSLBlock], int]:
        """Парсинг блока цикла"""
        header_line = lines[start_i].strip()
        
        # Парсим заголовок цикла
        loop_info = LoopParser.parse_loop_header(header_line)
        if not loop_info.get("type"):
            self.errors.append(f"Строка {start_i + 1}: Неизвестный тип цикла")
            return None, start_i + 1
        
        # Определяем ключевое слово окончания
        end_keywords = {
            "repeat": "end_repeat",
            "while": "end_while", 
            "for_each": "end_for"
        }
        
        loop_type = header_line.split()[0]
        end_keyword = end_keywords.get(loop_type)
        
        if not end_keyword:
            self.errors.append(f"Строка {start_i + 1}: Неизвестное окончание для цикла {loop_type}")
            return None, start_i + 1
        
        # Парсим тело цикла
        body = []
        i = start_i + 1
        block_lines = [header_line]
        
        while i < len(lines):
            line = lines[i].strip()
            block_lines.append(lines[i])
            
            if line == end_keyword:
                break
            elif line and not line.startswith('#'):
                body.append(line)
            
            i += 1
        
        if i >= len(lines):
            self.errors.append(f"Строка {start_i + 1}: Незакрытый цикл {loop_type}")
            return None, len(lines)
        
        # Создаем объект цикла
        loop_block = LoopParser.create_loop(loop_info, body)
        if not loop_block:
            self.errors.append(f"Строка {start_i + 1}: Не удалось создать цикл")
            return None, i + 1
        
        return DSLBlock(
            block_type=BlockType.LOOP,
            content=loop_block,
            line_number=start_i + 1,
            raw_lines=block_lines
        ), i + 1
    
    def _parse_variable_declaration(self, lines: List[str], start_i: int) -> Tuple[Optional[DSLBlock], int]:
        """Парсинг объявления переменной"""
        line = lines[start_i].strip()
        
        var_info = VariableParser.parse_variable_declaration(line)
        if not var_info:
            self.errors.append(f"Строка {start_i + 1}: Неверный синтаксис объявления переменной")
            return None, start_i + 1
        
        # Валидация имени переменной
        name_errors = VariableValidator.validate_variable_name(var_info["name"])
        if name_errors:
            for error in name_errors:
                self.errors.append(f"Строка {start_i + 1}: {error}")
            return None, start_i + 1
        
        # Добавляем переменную в менеджер
        try:
            if var_info["is_parameter"]:
                self.variable_manager.set_parameter(var_info["name"], var_info["value"])
            else:
                self.variable_manager.set_variable(var_info["name"], var_info["value"])
        except Exception as e:
            self.errors.append(f"Строка {start_i + 1}: Ошибка установки переменной - {str(e)}")
            return None, start_i + 1
        
        return DSLBlock(
            block_type=BlockType.VARIABLE_DECLARATION,
            content=var_info,
            line_number=start_i + 1,
            raw_lines=[line]
        ), start_i + 1
    
    def _parse_command(self, lines: List[str], start_i: int) -> Tuple[Optional[DSLBlock], int]:
        """Парсинг обычной команды"""
        line = lines[start_i].strip()
        
        # Подстановка переменных
        substituted_line = self.variable_manager.substitute_variables(line)
        
        return DSLBlock(
            block_type=BlockType.COMMAND,
            content=substituted_line,
            line_number=start_i + 1,
            raw_lines=[line]
        ), start_i + 1
    
    def _validate_variable_usage(self, blocks: List[DSLBlock]):
        """Валидация использования переменных"""
        available_vars = set(self.variable_manager.get_all_variables().keys())
        
        for block in blocks:
            if block.block_type == BlockType.COMMAND:
                warnings = VariableValidator.validate_variable_usage(
                    block.content, available_vars
                )
                for warning in warnings:
                    self.warnings.append(f"Строка {block.line_number}: {warning}")
            
            elif block.block_type == BlockType.CONDITIONAL:
                conditional = block.content
                # Проверяем условие
                condition_str = str(conditional.condition)
                warnings = VariableValidator.validate_variable_usage(
                    condition_str, available_vars
                )
                for warning in warnings:
                    self.warnings.append(f"Строка {block.line_number}: {warning}")
                
                # Проверяем тело блоков
                for cmd in conditional.if_block + (conditional.else_block or []):
                    warnings = VariableValidator.validate_variable_usage(
                        cmd, available_vars
                    )
                    for warning in warnings:
                        self.warnings.append(f"Строка {block.line_number}: {warning}")


class DSLOptimizer:
    """Оптимизатор DSL кода"""
    
    @staticmethod
    def optimize(parsed_dsl: ParsedDSL) -> ParsedDSL:
        """
        Оптимизация распарсенного DSL
        
        Args:
            parsed_dsl: Результат парсинга
            
        Returns:
            Оптимизированный DSL
        """
        optimized_blocks = []
        
        for block in parsed_dsl.blocks:
            # Оптимизация циклов
            if block.block_type == BlockType.LOOP:
                optimized_block = DSLOptimizer._optimize_loop(block)
                optimized_blocks.append(optimized_block)
            
            # Оптимизация условий
            elif block.block_type == BlockType.CONDITIONAL:
                optimized_block = DSLOptimizer._optimize_conditional(block)
                optimized_blocks.append(optimized_block)
            
            else:
                optimized_blocks.append(block)
        
        return ParsedDSL(
            blocks=optimized_blocks,
            variables=parsed_dsl.variables,
            errors=parsed_dsl.errors,
            warnings=parsed_dsl.warnings,
            metadata=parsed_dsl.metadata
        )
    
    @staticmethod
    def _optimize_loop(block: DSLBlock) -> DSLBlock:
        """Оптимизация цикла"""
        loop = block.content
        
        # Удаляем пустые команды из тела цикла
        if hasattr(loop, 'body'):
            loop.body = [cmd for cmd in loop.body if cmd.strip()]
        
        return block
    
    @staticmethod
    def _optimize_conditional(block: DSLBlock) -> DSLBlock:
        """Оптимизация условного блока"""
        conditional = block.content
        
        # Удаляем пустые команды
        conditional.if_block = [cmd for cmd in conditional.if_block if cmd.strip()]
        if conditional.else_block:
            conditional.else_block = [cmd for cmd in conditional.else_block if cmd.strip()]
        
        return block


# Примеры использования
if __name__ == "__main__":
    # Тест парсера
    dsl_code = """
# Тестовый макрос с условиями и циклами
param username = "admin"
set search_term = "Python tutorial"

if element_exists "//button[@id='login']"
    click "//button[@id='login']"
    type_in_field "//input[@name='username']" $username
    wait 2s
else
    click "//button[@id='signup']"
endif

repeat 3 times
    click "//button[@class='next']"
    wait 2s
    if page_contains "End of results"
        break
    endif
end_repeat

navigate "https://youtube.com"
type_in_field "//input[@id='search']" $search_term
"""
    
    parser = EnhancedDSLParser()
    result = parser.parse(dsl_code)
    
    print(f"Parsed {result.metadata['total_blocks']} blocks")
    print(f"Variables: {result.variables.get_all_variables()}")
    print(f"Errors: {result.errors}")
    print(f"Warnings: {result.warnings}")
    
    for i, block in enumerate(result.blocks):
        print(f"Block {i + 1}: {block.block_type.value} at line {block.line_number}")
        if block.block_type == BlockType.CONDITIONAL:
            print(f"  Condition: {block.content.condition}")
        elif block.block_type == BlockType.LOOP:
            print(f"  Loop: {type(block.content).__name__}")
