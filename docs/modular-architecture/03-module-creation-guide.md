# 🔧 Руководство по созданию модулей

## 🎯 Обзор

Это руководство показывает, как легко создавать новые AI модули для модульной системы. Каждый модуль - это специализированный AI агент, который выполняет определенную задачу.

## 📋 Структура модуля

### **Минимальная структура модуля:**
```
src/modules/my_module/
├── __init__.py
├── module.py                    # Главный класс модуля
├── config.yaml                  # Конфигурация модуля
├── prompts/                     # Промпты для AI
│   ├── base_prompt.txt         # Основной промпт
│   ├── context_template.txt    # Шаблон контекста
│   └── examples/               # Примеры для few-shot learning
│       ├── example_1.txt
│       └── example_2.txt
└── executor.py                 # Исполнитель результатов (опционально)
```

## 🚀 Пошаговое создание модуля

### **Шаг 1: Создание базовой структуры**

```python
# src/modules/my_module/module.py
from src.modules.base.ai_module import AIModule
from src.modules.base.module_config import ModuleConfig

class MyModule(AIModule):
    """Описание функционала модуля"""
    
    def __init__(self):
        config = ModuleConfig(
            name="my_module",
            description="Краткое описание что делает модуль",
            prompt_path="my_module/prompts/",
            when_to_use=[
                "ключевое слово 1",
                "ключевое слово 2", 
                "фраза для активации"
            ]
        )
        super().__init__(config)
    
    def get_context_resources(self) -> Dict:
        """Загружает ресурсы, нужные модулю"""
        return {
            "custom_data": self.load_custom_data(),
            "templates": self.load_templates() if self.needs_templates() else None
        }
    
    def parse_ai_result(self, ai_result: str) -> Any:
        """Парсит результат AI в нужный формат"""
        # Ваша логика парсинга
        return self.extract_result_data(ai_result)
    
    def execute_result(self, parsed_result: Any) -> ExecutionResult:
        """Выполняет результат AI (опционально)"""
        # Если модуль только генерирует данные - можно не реализовывать
        return ExecutionResult(success=True, data=parsed_result)
```

### **Шаг 2: Конфигурация модуля**

```yaml
# src/modules/my_module/config.yaml
name: "my_module"
description: "Подробное описание функционала модуля"
version: "1.0.0"
author: "Ваше имя"

# AI Configuration
ai_config:
  model: "gemini-1.5-pro"
  max_tokens: 2048
  temperature: 0.7
  
# Prompts
prompts:
  base_prompt: "prompts/base_prompt.txt"
  context_template: "prompts/context_template.txt"
  
# Resources (что нужно модулю)
resources:
  templates: false      # Нужны ли шаблоны изображений
  variables: false      # Нужны ли DSL переменные
  dom_selectors: false  # Нужны ли DOM селекторы
  system_commands: false # Нужны ли системные команды
  custom_data: true     # Кастомные данные модуля
  
# Execution
executor:
  type: "custom"        # custom, dsl_executor, none
  timeout: 60
  retry_attempts: 2
  
# Keywords для выбора модуля координатором
keywords:
  - "ключевое слово"
  - "фраза активации"
  - "что делает модуль"
  
priority: 5             # 0 = высший, 10 = низший
enabled: true
```

### **Шаг 3: Создание промптов**

```txt
# src/modules/my_module/prompts/base_prompt.txt
Ты - специалист по [область модуля].
Твоя задача: [что должен делать модуль].

КОНТЕКСТ:
{context}

ДОСТУПНЫЕ РЕСУРСЫ:
{available_resources}

ЗАПРОС ПОЛЬЗОВАТЕЛЯ:
{user_input}

ИНСТРУКЦИИ:
1. Проанализируй запрос пользователя
2. [Специфичные инструкции для модуля]
3. Верни результат в указанном формате

ФОРМАТ ОТВЕТА:
```
[Формат выходных данных]
```

ПРИМЕРЫ:
{examples}
```

```txt
# src/modules/my_module/prompts/context_template.txt
КОНТЕКСТ ВЫПОЛНЕНИЯ:
- Пользователь: {user_context}
- Текущее приложение: {current_app}
- Время: {timestamp}
- Предыдущие действия: {previous_actions}

ДОСТУПНЫЕ РЕСУРСЫ:
{resources_list}
```

### **Шаг 4: Примеры для few-shot learning**

```txt
# src/modules/my_module/prompts/examples/example_1.txt
ПОЛЬЗОВАТЕЛЬ: [пример запроса]

АНАЛИЗ: [как модуль должен анализировать]

РЕЗУЛЬТАТ:
```
[пример правильного результата]
```
```

## 🎯 Специализированные типы модулей

### **1. Генеративный модуль (создает контент)**

```python
class ContentGeneratorModule(AIModule):
    """Модуль для генерации контента"""
    
    def parse_ai_result(self, ai_result: str) -> GeneratedContent:
        """Парсит сгенерированный контент"""
        return GeneratedContent(
            content=self.extract_content(ai_result),
            metadata=self.extract_metadata(ai_result)
        )
    
    def execute_result(self, content: GeneratedContent) -> ExecutionResult:
        """Сохраняет сгенерированный контент"""
        file_path = self.save_content(content)
        return ExecutionResult(
            success=True,
            data={"file_path": file_path, "content": content.content}
        )
```

### **2. Аналитический модуль (анализирует данные)**

```python
class DataAnalyzerModule(AIModule):
    """Модуль для анализа данных"""
    
    def get_context_resources(self) -> Dict:
        """Загружает данные для анализа"""
        return {
            "data_source": self.load_data_source(),
            "analysis_templates": self.load_analysis_templates()
        }
    
    def parse_ai_result(self, ai_result: str) -> AnalysisResult:
        """Парсит результат анализа"""
        return AnalysisResult(
            insights=self.extract_insights(ai_result),
            recommendations=self.extract_recommendations(ai_result),
            confidence=self.extract_confidence(ai_result)
        )
```

### **3. Исполнительный модуль (выполняет действия)**

```python
class ActionExecutorModule(AIModule):
    """Модуль для выполнения действий"""
    
    def __init__(self):
        super().__init__(config)
        self.action_executor = ActionExecutor()
    
    def parse_ai_result(self, ai_result: str) -> ActionSequence:
        """Парсит последовательность действий"""
        return ActionSequence(
            actions=self.extract_actions(ai_result),
            parameters=self.extract_parameters(ai_result)
        )
    
    def execute_result(self, sequence: ActionSequence) -> ExecutionResult:
        """Выполняет последовательность действий"""
        results = []
        for action in sequence.actions:
            result = self.action_executor.execute(action)
            results.append(result)
            
            if not result.success:
                break
        
        return ExecutionResult(
            success=all(r.success for r in results),
            data={"action_results": results}
        )
```

## 🔌 Интеграция с существующими системами

### **Использование DSL парсера:**

```python
class DSLIntegratedModule(AIModule):
    """Модуль с интеграцией DSL"""
    
    def __init__(self):
        super().__init__(config)
        self.dsl_parser = AtlasDSLParser()
        self.macro_executor = MacroSequence
    
    def execute_result(self, dsl_code: str) -> ExecutionResult:
        """Выполняет DSL код через существующую систему"""
        try:
            yaml_data = self.dsl_parser.parse(dsl_code)
            sequence = self.macro_executor(yaml_data)
            result = sequence.execute()
            
            return ExecutionResult(
                success=result.success,
                data=result.data,
                logs=result.logs
            )
        except Exception as e:
            return ExecutionResult(
                success=False,
                error=str(e)
            )
```

### **Использование голосового ввода:**

```python
class VoiceIntegratedModule(AIModule):
    """Модуль с голосовой интеграцией"""
    
    def __init__(self):
        super().__init__(config)
        self.tts = TextToSpeech()
    
    def execute(self, user_input: str, context: Dict) -> ModuleResult:
        """Выполнение с голосовым откликом"""
        
        # Мгновенный голосовой отклик
        self.tts.speak("Понял, выполняю...")
        
        # Обычное выполнение
        result = super().execute(user_input, context)
        
        # Голосовой отчет о результате
        if result.success:
            self.tts.speak("Задача выполнена успешно!")
        else:
            self.tts.speak("Произошла ошибка при выполнении")
        
        return result
```

## 📊 Система логирования модуля

### **Встроенное логирование:**

```python
class LoggingModule(AIModule):
    """Модуль с расширенным логированием"""
    
    def execute(self, user_input: str, context: Dict) -> ModuleResult:
        """Выполнение с подробным логированием"""
        
        start_time = time.time()
        
        # Логирование начала
        self.log_execution_start(user_input, context)
        
        try:
            result = super().execute(user_input, context)
            
            # Логирование успеха
            self.log_execution_success(result, time.time() - start_time)
            
            return result
            
        except Exception as e:
            # Логирование ошибки
            self.log_execution_error(e, time.time() - start_time)
            raise
    
    def log_execution_start(self, user_input: str, context: Dict):
        """Логирование начала выполнения"""
        self.logger.info(f"Module {self.name} started", extra={
            "user_input": user_input,
            "context": context,
            "timestamp": datetime.now()
        })
    
    def log_execution_success(self, result: ModuleResult, duration: float):
        """Логирование успешного выполнения"""
        self.logger.info(f"Module {self.name} completed successfully", extra={
            "duration": duration,
            "result_data": result.data,
            "timestamp": datetime.now()
        })
    
    def log_execution_error(self, error: Exception, duration: float):
        """Логирование ошибки"""
        self.logger.error(f"Module {self.name} failed", extra={
            "error": str(error),
            "duration": duration,
            "timestamp": datetime.now()
        })
```

## 🧪 Тестирование модуля

### **Базовые тесты:**

```python
# tests/modules/test_my_module.py
import pytest
from src.modules.my_module.module import MyModule

class TestMyModule:
    
    @pytest.fixture
    def module(self):
        return MyModule()
    
    def test_module_initialization(self, module):
        """Тест инициализации модуля"""
        assert module.name == "my_module"
        assert module.description is not None
        assert module.ai_agent is not None
    
    def test_context_loading(self, module):
        """Тест загрузки контекста"""
        context = module.get_context_resources()
        assert isinstance(context, dict)
        assert "custom_data" in context
    
    def test_ai_result_parsing(self, module):
        """Тест парсинга AI результата"""
        mock_ai_result = "test result"
        parsed = module.parse_ai_result(mock_ai_result)
        assert parsed is not None
    
    def test_execution(self, module):
        """Тест выполнения модуля"""
        result = module.execute("test input", {})
        assert isinstance(result, ModuleResult)
        assert result.success is not None
    
    @pytest.mark.integration
    def test_full_pipeline(self, module):
        """Интеграционный тест полного пайплайна"""
        user_input = "test user request"
        context = {"test": "context"}
        
        result = module.execute(user_input, context)
        
        assert result.success
        assert result.data is not None
```

## 📋 Регистрация модуля

### **Автоматическая регистрация:**

```python
# src/modules/my_module/__init__.py
from .module import MyModule

# Автоматическая регистрация при импорте
def register_module():
    from src.modules.registry import MODULE_REGISTRY
    
    MODULE_REGISTRY["my_module"] = {
        "class": MyModule,
        "description": "Описание модуля для координатора",
        "keywords": ["ключевое", "слово", "активации"],
        "priority": 5,
        "enabled": True
    }

# Вызов регистрации
register_module()
```

### **Ручная регистрация:**

```python
# src/modules/registry.py
from src.modules.my_module.module import MyModule

MODULE_REGISTRY["my_module"] = {
    "class": MyModule,
    "description": "Подробное описание для AI координатора",
    "keywords": ["когда", "использовать", "модуль"],
    "priority": 5,
    "enabled": True,
    "config_path": "my_module/config.yaml"
}
```

## 🎯 Лучшие практики

### **1. Промпт инжиниринг:**
- ✅ Четкие инструкции для AI
- ✅ Примеры правильных результатов
- ✅ Указание формата выходных данных
- ✅ Обработка edge cases

### **2. Обработка ошибок:**
- ✅ Валидация входных данных
- ✅ Graceful degradation при ошибках AI
- ✅ Подробное логирование ошибок
- ✅ Retry механизмы

### **3. Производительность:**
- ✅ Кэширование ресурсов
- ✅ Ленивая загрузка данных
- ✅ Оптимизация промптов
- ✅ Мониторинг времени выполнения

### **4. Тестирование:**
- ✅ Unit тесты для всех методов
- ✅ Integration тесты с AI
- ✅ Mock данные для тестов
- ✅ Performance тесты

## 🚀 Готовые шаблоны

### **Быстрый старт - Simple Module:**

```bash
# Создание модуля одной командой
python3 tools/create_module.py --name my_module --type simple
```

### **Шаблон для копирования:**

```python
# Минимальный рабочий модуль
class SimpleModule(AIModule):
    def __init__(self):
        config = ModuleConfig(
            name="simple_module",
            description="Простой модуль для примера",
            prompt_path="simple_module/prompts/",
            when_to_use=["пример", "тест"]
        )
        super().__init__(config)
    
    def parse_ai_result(self, ai_result: str) -> str:
        return ai_result.strip()
    
    def execute_result(self, result: str) -> ExecutionResult:
        return ExecutionResult(success=True, data={"result": result})
```

**Готово! Теперь вы можете создавать собственные AI модули легко и быстро!** 🎉
