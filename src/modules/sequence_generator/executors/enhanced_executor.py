"""
Расширенный исполнитель DSL с поддержкой условий, циклов и переменных
"""

from typing import Dict, Any, List, Optional, Callable
import time
import logging
from dataclasses import dataclass
from enum import Enum

from ..dsl.conditions import Condition, ConditionalBlock, ConditionEvaluator
from ..dsl.loops import LoopBlock, RepeatLoop, WhileLoop, ForEachLoop, LoopExecutor
from ..dsl.variables import VariableManager
from ..parsers.enhanced_dsl_parser import ParsedDSL, DSLBlock, BlockType

logger = logging.getLogger(__name__)


class ExecutionStatus(Enum):
    """Статусы выполнения"""
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    BREAK = "break"
    CONTINUE = "continue"


@dataclass
class ExecutionResult:
    """Результат выполнения"""
    status: ExecutionStatus
    message: str = ""
    data: Any = None
    execution_time: float = 0.0
    
    def is_success(self) -> bool:
        return self.status == ExecutionStatus.SUCCESS
    
    def is_control_flow(self) -> bool:
        return self.status in [ExecutionStatus.BREAK, ExecutionStatus.CONTINUE]


@dataclass
class ExecutionContext:
    """Контекст выполнения"""
    variables: VariableManager
    break_requested: bool = False
    continue_requested: bool = False
    debug_mode: bool = False
    dry_run: bool = False
    execution_log: List[str] = None
    
    def __post_init__(self):
        if self.execution_log is None:
            self.execution_log = []
    
    def log(self, message: str):
        """Добавление записи в лог выполнения"""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.execution_log.append(log_entry)
        if self.debug_mode:
            print(log_entry)


class EnhancedExecutor:
    """Расширенный исполнитель DSL"""
    
    def __init__(self):
        self.command_handlers: Dict[str, Callable] = {}
        self.condition_evaluator = None
        self.loop_executor = None
        self._register_default_handlers()
    
    def execute(self, parsed_dsl: ParsedDSL, parameters: Dict[str, Any] = None, 
                debug_mode: bool = False, dry_run: bool = False) -> ExecutionResult:
        """
        Выполнение распарсенного DSL
        
        Args:
            parsed_dsl: Результат парсинга DSL
            parameters: Параметры для выполнения
            debug_mode: Режим отладки
            dry_run: Режим симуляции (без реального выполнения)
            
        Returns:
            Результат выполнения
        """
        start_time = time.time()
        
        # Проверяем ошибки парсинга
        if parsed_dsl.errors:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=f"Ошибки парсинга: {'; '.join(parsed_dsl.errors)}",
                execution_time=time.time() - start_time
            )
        
        # Создаем контекст выполнения
        context = ExecutionContext(
            variables=parsed_dsl.variables,
            debug_mode=debug_mode,
            dry_run=dry_run
        )
        
        # Устанавливаем параметры
        if parameters:
            for name, value in parameters.items():
                if context.variables.has_variable(name):
                    context.variables.update_parameter(name, value)
                    context.log(f"Параметр {name} установлен в {value}")
        
        # Инициализируем компоненты
        self.condition_evaluator = ConditionEvaluator(context.variables.get_all_variables())
        self.loop_executor = LoopExecutor(context.variables.get_all_variables())
        
        context.log(f"Начало выполнения DSL с {len(parsed_dsl.blocks)} блоками")
        
        # Выполняем блоки
        try:
            for i, block in enumerate(parsed_dsl.blocks):
                if context.break_requested:
                    context.log("Выполнение прервано по break")
                    break
                
                result = self._execute_block(block, context)
                
                if not result.is_success() and not result.is_control_flow():
                    context.log(f"Ошибка выполнения блока {i + 1}: {result.message}")
                    return ExecutionResult(
                        status=ExecutionStatus.FAILED,
                        message=f"Блок {i + 1}: {result.message}",
                        execution_time=time.time() - start_time
                    )
                
                # Обработка управления потоком
                if result.status == ExecutionStatus.BREAK:
                    context.break_requested = True
                elif result.status == ExecutionStatus.CONTINUE:
                    context.continue_requested = True
            
            execution_time = time.time() - start_time
            context.log(f"Выполнение завершено за {execution_time:.2f}с")
            
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                message="DSL выполнен успешно",
                data={
                    "execution_log": context.execution_log,
                    "final_variables": context.variables.get_all_variables(),
                    "blocks_executed": len(parsed_dsl.blocks)
                },
                execution_time=execution_time
            )
            
        except Exception as e:
            logger.error(f"Критическая ошибка выполнения: {e}")
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=f"Критическая ошибка: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    def _execute_block(self, block: DSLBlock, context: ExecutionContext) -> ExecutionResult:
        """Выполнение одного блока DSL"""
        context.log(f"Выполнение блока {block.block_type.value} (строка {block.line_number})")
        
        try:
            if block.block_type == BlockType.COMMAND:
                return self._execute_command(block.content, context)
            
            elif block.block_type == BlockType.CONDITIONAL:
                return self._execute_conditional(block.content, context)
            
            elif block.block_type == BlockType.LOOP:
                return self._execute_loop(block.content, context)
            
            elif block.block_type == BlockType.VARIABLE_DECLARATION:
                return self._execute_variable_declaration(block.content, context)
            
            elif block.block_type == BlockType.COMMENT:
                return ExecutionResult(status=ExecutionStatus.SKIPPED, message="Комментарий пропущен")
            
            else:
                return ExecutionResult(
                    status=ExecutionStatus.FAILED,
                    message=f"Неизвестный тип блока: {block.block_type}"
                )
                
        except Exception as e:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=f"Ошибка выполнения блока: {str(e)}"
            )
    
    def _execute_command(self, command: str, context: ExecutionContext) -> ExecutionResult:
        """Выполнение обычной команды"""
        command = command.strip()
        
        # Обработка команд управления потоком
        if command == "break":
            context.log("Команда break")
            return ExecutionResult(status=ExecutionStatus.BREAK, message="Break выполнен")
        
        elif command == "continue":
            context.log("Команда continue")
            return ExecutionResult(status=ExecutionStatus.CONTINUE, message="Continue выполнен")
        
        # Подстановка переменных
        substituted_command = context.variables.substitute_variables(command)
        if substituted_command != command:
            context.log(f"Подстановка переменных: {command} -> {substituted_command}")
        
        # Парсинг команды
        parts = substituted_command.split()
        if not parts:
            return ExecutionResult(status=ExecutionStatus.SKIPPED, message="Пустая команда")
        
        command_name = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Выполнение команды через обработчик
        if command_name in self.command_handlers:
            if context.dry_run:
                context.log(f"[DRY RUN] {substituted_command}")
                return ExecutionResult(status=ExecutionStatus.SUCCESS, message="Симуляция команды")
            else:
                return self.command_handlers[command_name](args, context)
        else:
            # Неизвестная команда - логируем как предупреждение
            context.log(f"Неизвестная команда: {command_name}")
            return ExecutionResult(
                status=ExecutionStatus.SUCCESS,
                message=f"Команда {command_name} выполнена (заглушка)"
            )
    
    def _execute_conditional(self, conditional: ConditionalBlock, context: ExecutionContext) -> ExecutionResult:
        """Выполнение условного блока"""
        # Обновляем переменные в evaluator
        self.condition_evaluator.variables = context.variables.get_all_variables()
        
        # Оцениваем условие
        condition_result = self.condition_evaluator.evaluate(conditional.condition)
        context.log(f"Условие '{conditional.condition}' = {condition_result}")
        
        # Выбираем блок для выполнения
        if condition_result:
            commands_to_execute = conditional.if_block
            context.log("Выполняется if блок")
        else:
            commands_to_execute = conditional.else_block or []
            context.log("Выполняется else блок" if conditional.else_block else "else блок отсутствует")
        
        # Выполняем команды блока
        for command in commands_to_execute:
            if context.break_requested or context.continue_requested:
                break
            
            result = self._execute_command(command, context)
            if not result.is_success() and not result.is_control_flow():
                return result
            
            # Передаем управление потоком наверх
            if result.is_control_flow():
                return result
        
        return ExecutionResult(status=ExecutionStatus.SUCCESS, message="Условный блок выполнен")
    
    def _execute_loop(self, loop: LoopBlock, context: ExecutionContext) -> ExecutionResult:
        """Выполнение цикла"""
        context.log(f"Начало выполнения цикла {type(loop).__name__}")
        
        # Обновляем переменные в loop executor
        self.loop_executor.variables = context.variables.get_all_variables()
        
        if isinstance(loop, RepeatLoop):
            return self._execute_repeat_loop(loop, context)
        elif isinstance(loop, WhileLoop):
            return self._execute_while_loop(loop, context)
        elif isinstance(loop, ForEachLoop):
            return self._execute_foreach_loop(loop, context)
        else:
            return ExecutionResult(
                status=ExecutionStatus.FAILED,
                message=f"Неизвестный тип цикла: {type(loop)}"
            )
    
    def _execute_repeat_loop(self, loop: RepeatLoop, context: ExecutionContext) -> ExecutionResult:
        """Выполнение цикла repeat"""
        context.log(f"Repeat цикл: {loop.count} итераций")
        
        for i in range(loop.count):
            if context.break_requested:
                context.log(f"Цикл прерван на итерации {i + 1}")
                break
            
            context.log(f"Итерация {i + 1}/{loop.count}")
            context.variables.set_variable("_loop_counter", i + 1)
            
            # Выполняем тело цикла
            for command in loop.body:
                if context.break_requested:
                    break
                
                result = self._execute_command(command, context)
                
                if result.status == ExecutionStatus.BREAK:
                    context.break_requested = True
                    break
                elif result.status == ExecutionStatus.CONTINUE:
                    context.continue_requested = True
                    break
                elif not result.is_success():
                    return result
            
            # Сброс continue для следующей итерации
            if context.continue_requested:
                context.continue_requested = False
        
        # Сброс break после выхода из цикла
        context.break_requested = False
        
        return ExecutionResult(status=ExecutionStatus.SUCCESS, message="Repeat цикл завершен")
    
    def _execute_while_loop(self, loop: WhileLoop, context: ExecutionContext) -> ExecutionResult:
        """Выполнение цикла while"""
        context.log(f"While цикл с условием: {loop.condition}")
        
        iteration = 0
        max_iterations = 1000  # Защита от бесконечного цикла
        
        # Обновляем evaluator
        self.condition_evaluator.variables = context.variables.get_all_variables()
        
        while self.condition_evaluator.evaluate(loop.condition) and iteration < max_iterations:
            if context.break_requested:
                context.log(f"While цикл прерван на итерации {iteration + 1}")
                break
            
            iteration += 1
            context.log(f"While итерация {iteration}")
            context.variables.set_variable("_loop_iteration", iteration)
            
            # Выполняем тело цикла
            for command in loop.body:
                if context.break_requested:
                    break
                
                result = self._execute_command(command, context)
                
                if result.status == ExecutionStatus.BREAK:
                    context.break_requested = True
                    break
                elif result.status == ExecutionStatus.CONTINUE:
                    context.continue_requested = True
                    break
                elif not result.is_success():
                    return result
            
            # Сброс continue для следующей итерации
            if context.continue_requested:
                context.continue_requested = False
            
            # Обновляем переменные для следующей проверки условия
            self.condition_evaluator.variables = context.variables.get_all_variables()
        
        if iteration >= max_iterations:
            context.log(f"While цикл достиг максимума итераций ({max_iterations})")
        
        # Сброс break после выхода из цикла
        context.break_requested = False
        
        return ExecutionResult(status=ExecutionStatus.SUCCESS, message=f"While цикл завершен ({iteration} итераций)")
    
    def _execute_foreach_loop(self, loop: ForEachLoop, context: ExecutionContext) -> ExecutionResult:
        """Выполнение цикла for_each"""
        context.log(f"ForEach цикл по селектору: {loop.selector}")
        
        # TODO: Интеграция с реальным поиском элементов
        # Пока используем заглушку
        elements = self._find_elements(loop.selector, context)
        context.log(f"Найдено элементов: {len(elements)}")
        
        for i, element in enumerate(elements):
            if context.break_requested:
                context.log(f"ForEach цикл прерван на элементе {i + 1}")
                break
            
            context.log(f"Обработка элемента {i + 1}/{len(elements)}")
            context.variables.set_variable(loop.variable_name, element)
            context.variables.set_variable("_loop_index", i)
            
            # Выполняем тело цикла
            for command in loop.body:
                if context.break_requested:
                    break
                
                # Подставляем переменную элемента в команду
                substituted_command = command.replace(loop.variable_name, str(element))
                
                result = self._execute_command(substituted_command, context)
                
                if result.status == ExecutionStatus.BREAK:
                    context.break_requested = True
                    break
                elif result.status == ExecutionStatus.CONTINUE:
                    context.continue_requested = True
                    break
                elif not result.is_success():
                    return result
            
            # Сброс continue для следующей итерации
            if context.continue_requested:
                context.continue_requested = False
        
        # Сброс break после выхода из цикла
        context.break_requested = False
        
        return ExecutionResult(status=ExecutionStatus.SUCCESS, message="ForEach цикл завершен")
    
    def _execute_variable_declaration(self, var_info: Dict[str, Any], context: ExecutionContext) -> ExecutionResult:
        """Выполнение объявления переменной"""
        name = var_info["name"]
        value = var_info["value"]
        is_parameter = var_info["is_parameter"]
        
        if is_parameter:
            context.log(f"Объявлен параметр: {name} = {value}")
        else:
            context.log(f"Объявлена переменная: {name} = {value}")
        
        return ExecutionResult(status=ExecutionStatus.SUCCESS, message="Переменная объявлена")
    
    def _find_elements(self, selector: str, context: ExecutionContext) -> List[str]:
        """Поиск элементов по селектору (заглушка)"""
        # TODO: Интеграция с реальным поиском элементов
        context.log(f"Поиск элементов по селектору: {selector}")
        return [f"element_{i}" for i in range(3)]  # Заглушка
    
    def _register_default_handlers(self):
        """Регистрация обработчиков команд по умолчанию"""
        self.command_handlers.update({
            'open': self._handle_open,
            'click': self._handle_click,
            'type': self._handle_type,
            'wait': self._handle_wait,
            'navigate': self._handle_navigate,
            'press': self._handle_press,
            'system_command': self._handle_system_command
        })
    
    def register_command_handler(self, command: str, handler: Callable):
        """Регистрация пользовательского обработчика команды"""
        self.command_handlers[command.lower()] = handler
    
    # Обработчики команд (заглушки для демонстрации)
    def _handle_open(self, args: List[str], context: ExecutionContext) -> ExecutionResult:
        app_name = args[0] if args else "Unknown"
        context.log(f"Открытие приложения: {app_name}")
        return ExecutionResult(status=ExecutionStatus.SUCCESS, message=f"Приложение {app_name} открыто")
    
    def _handle_click(self, args: List[str], context: ExecutionContext) -> ExecutionResult:
        element = args[0] if args else "Unknown"
        context.log(f"Клик по элементу: {element}")
        return ExecutionResult(status=ExecutionStatus.SUCCESS, message=f"Клик по {element}")
    
    def _handle_type(self, args: List[str], context: ExecutionContext) -> ExecutionResult:
        text = ' '.join(args).strip('"')
        context.log(f"Ввод текста: {text}")
        return ExecutionResult(status=ExecutionStatus.SUCCESS, message=f"Введен текст: {text}")
    
    def _handle_wait(self, args: List[str], context: ExecutionContext) -> ExecutionResult:
        duration_str = args[0] if args else "1s"
        duration = float(duration_str.rstrip('s'))
        context.log(f"Ожидание {duration}с")
        if not context.dry_run:
            time.sleep(duration)
        return ExecutionResult(status=ExecutionStatus.SUCCESS, message=f"Ожидание {duration}с завершено")
    
    def _handle_navigate(self, args: List[str], context: ExecutionContext) -> ExecutionResult:
        url = args[0].strip('"') if args else "Unknown"
        context.log(f"Переход на URL: {url}")
        return ExecutionResult(status=ExecutionStatus.SUCCESS, message=f"Переход на {url}")
    
    def _handle_press(self, args: List[str], context: ExecutionContext) -> ExecutionResult:
        key = args[0] if args else "Unknown"
        context.log(f"Нажатие клавиши: {key}")
        return ExecutionResult(status=ExecutionStatus.SUCCESS, message=f"Нажата клавиша {key}")
    
    def _handle_system_command(self, args: List[str], context: ExecutionContext) -> ExecutionResult:
        command = ' '.join(args).strip('"')
        context.log(f"Системная команда: {command}")
        return ExecutionResult(status=ExecutionStatus.SUCCESS, message=f"Системная команда выполнена: {command}")


# Примеры использования
if __name__ == "__main__":
    from ..parsers.enhanced_dsl_parser import EnhancedDSLParser
    
    # Тестовый DSL код
    dsl_code = """
set counter = 0
param max_count = 3

repeat $max_count times
    set counter = $counter + 1
    click "button_$counter"
    wait 1s
    
    if $counter == 2
        type "Special action for counter 2"
    endif
end_repeat

type "All done! Counter is $counter"
"""
    
    # Парсинг и выполнение
    parser = EnhancedDSLParser()
    parsed_dsl = parser.parse(dsl_code)
    
    executor = EnhancedExecutor()
    result = executor.execute(
        parsed_dsl, 
        parameters={"max_count": 5},
        debug_mode=True,
        dry_run=True
    )
    
    print(f"Execution result: {result.status.value}")
    print(f"Message: {result.message}")
    print(f"Execution time: {result.execution_time:.2f}s")
    
    if result.data:
        print("\nExecution log:")
        for log_entry in result.data["execution_log"]:
            print(f"  {log_entry}")
        
        print(f"\nFinal variables: {result.data['final_variables']}")
        print(f"Blocks executed: {result.data['blocks_executed']}")
