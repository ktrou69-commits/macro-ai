# 🚀 План реализации модульной AI архитектуры

## 📋 Этапы разработки

### **🏗️ Этап 1: Базовая инфраструктура (1-2 недели)**

#### **1.1 Создание базовых классов**
```python
# Приоритет: КРИТИЧЕСКИЙ
# Файлы для создания:
src/modules/base/ai_module.py          # Базовый класс модулей
src/modules/base/module_config.py      # Конфигурация модулей  
src/modules/base/ai_agent.py          # AI агент для модулей
src/modules/base/executor.py          # Базовый исполнитель
src/modules/base/module_result.py     # Результаты выполнения
```

**Задачи:**
- ✅ Создать абстрактный класс `AIModule`
- ✅ Реализовать `ModuleConfig` для конфигурации
- ✅ Создать `AIAgent` с интеграцией Gemini API
- ✅ Базовый `Executor` для выполнения результатов
- ✅ Система логирования модулей

#### **1.2 AI Coordinator (Главный маршрутизатор)**
```python
# Файлы для создания:
src/modules/coordinator/ai_coordinator.py    # Главный координатор
src/modules/coordinator/intent_analyzer.py  # Анализ намерений
src/modules/coordinator/module_selector.py  # Выбор модуля
src/modules/coordinator/context_manager.py  # Управление контекстом
```

**Задачи:**
- ✅ Реализовать анализ намерений пользователя
- ✅ Создать логику выбора модуля
- ✅ Система управления контекстом
- ✅ Интеграция с существующим TTS

#### **1.3 Module Registry (Реестр модулей)**
```python
# Файлы для создания:
src/modules/registry.py               # Реестр всех модулей
src/modules/loader.py                # Загрузчик модулей
```

**Задачи:**
- ✅ Создать централизованный реестр модулей
- ✅ Автоматическая загрузка модулей
- ✅ Система приоритетов модулей

---

### **🔧 Этап 2: Первые модули (2-3 недели)**

#### **2.1 Sequence Generator Module (расширение опции 6)**
```python
# Базируется на существующем AIMacroGenerator
# Файлы для создания:
src/modules/sequence_generator/module.py
src/modules/sequence_generator/dsl_executor.py
src/modules/sequence_generator/prompts/base_prompt.txt
src/modules/sequence_generator/prompts/context_templates.txt
```

**Задачи:**
- ✅ Адаптировать существующий `AIMacroGenerator` под модульную архитектуру
- ✅ Создать специализированные промпты
- ✅ Интегрировать с `AtlasDSLParser`
- ✅ Добавить контекстную фильтрацию ресурсов

#### **2.2 Variable Creator Module**
```python
# Базируется на существующем AIVariableGenerator
# Файлы для создания:
src/modules/variable_creator/module.py
src/modules/variable_creator/variable_manager.py
src/modules/variable_creator/prompts/variable_creation.txt
```

**Задачи:**
- ✅ Адаптировать `AIVariableGenerator`
- ✅ Улучшить систему создания переменных
- ✅ Автоматическое извлечение параметров
- ✅ Валидация создаваемых переменных

#### **2.3 Voice Handler Module**
```python
# Базируется на существующем голосовом ассистенте
# Файлы для создания:
src/modules/voice_handler/module.py
src/modules/voice_handler/speech_processor.py
src/modules/voice_handler/voice_router.py
```

**Задачи:**
- ✅ Интегрировать существующий голосовой ассистент
- ✅ Создать маршрутизацию голосовых команд
- ✅ Улучшить систему wake word detection
- ✅ Параллельная обработка TTS и выполнения

---

### **🌐 Этап 3: UI Automation (3-4 недели)**

#### **3.1 macOS Accessibility API интеграция**
```python
# Новые файлы:
src/ui_automation/macos_accessibility.py     # macOS Accessibility API
src/ui_automation/ui_element_finder.py      # Поиск UI элементов
src/ui_automation/ui_tree_builder.py        # Построение дерева элементов
```

**Задачи:**
- ✅ Интеграция с `AXUIElement`
- ✅ Создание системы поиска элементов по ID
- ✅ Построение дерева UI элементов приложений
- ✅ Кэширование структуры приложений

#### **3.2 Расширение DSL для UI Automation**
```atlas
# Новые DSL команды:
click_ui_element "button_id_123"
fill_ui_field "text_field_id" "Hello World"  
select_ui_option "dropdown_id" "Option 1"
get_ui_text "label_id"
wait_for_ui_element "element_id" 10s
```

**Задачи:**
- ✅ Расширить `AtlasDSLParser` новыми командами
- ✅ Создать UI селекторы аналогично DOM селекторам
- ✅ Интеграция с существующей системой шаблонов
- ✅ Fallback: UI Automation → Templates → System Commands

#### **3.3 Template Architect Module**
```python
# Файлы для создания:
src/modules/template_architect/module.py
src/modules/template_architect/structure_generator.py
src/modules/template_architect/ui_analyzer.py
```

**Задачи:**
- ✅ Автоматическое создание архитектуры шаблонов
- ✅ Анализ UI структуры приложений
- ✅ Генерация базовых кнопок и элементов
- ✅ Создание дерева элементов для AI

---

### **🧠 Этап 4: Самообучение (2-3 недели)**

#### **4.1 Learning Module**
```python
# Файлы для создания:
src/modules/learning/log_analyzer.py         # Анализ логов
src/modules/learning/pattern_extractor.py   # Извлечение паттернов
src/modules/learning/knowledge_updater.py   # Обновление знаний
src/modules/learning/performance_tracker.py # Отслеживание производительности
```

**Задачи:**
- ✅ Система анализа логов выполнения
- ✅ Извлечение паттернов из ошибок
- ✅ Автоматическая корректировка таймингов
- ✅ Обновление промптов на основе опыта

#### **4.2 Advanced Pattern Recognition**
```python
# Файлы для создания:
src/modules/learning/error_classifier.py    # Классификация ошибок
src/modules/learning/success_analyzer.py    # Анализ успешных выполнений
src/modules/learning/recommendation_engine.py # Рекомендации улучшений
```

**Задачи:**
- ✅ Классификация типов ошибок
- ✅ Анализ успешных паттернов
- ✅ Система рекомендаций для улучшения
- ✅ Автоматическое A/B тестирование подходов

---

### **🔌 Этап 5: Дополнительные модули (3-4 недели)**

#### **5.1 DOM Extractor Module**
```python
# Файлы для создания:
src/modules/dom_extractor/module.py
src/modules/dom_extractor/selenium_analyzer.py
src/modules/dom_extractor/selector_optimizer.py
```

**Задачи:**
- ✅ Автоматическое извлечение DOM селекторов
- ✅ AI анализ структуры веб-страниц
- ✅ Оптимизация селекторов для надежности
- ✅ Создание fallback цепочек

#### **5.2 System Integration Module**
```python
# Файлы для создания:
src/modules/system_integration/module.py
src/modules/system_integration/app_launcher.py
src/modules/system_integration/file_manager.py
```

**Задачи:**
- ✅ Расширенная интеграция с системными командами
- ✅ Управление файлами и папками
- ✅ Запуск и управление приложениями
- ✅ Системная информация и мониторинг

---

### **🎨 Этап 6: GUI и пользовательский интерфейс (2-3 недели)**

#### **6.1 Модульный GUI**
```python
# Файлы для создания:
gui/modular/main_window.py              # Главное окно модульной системы
gui/modular/module_manager.py           # Управление модулями
gui/modular/execution_monitor.py        # Мониторинг выполнения
gui/modular/voice_controls.py           # Голосовые элементы управления
```

**Задачи:**
- ✅ GUI для управления модулями
- ✅ Визуальный мониторинг выполнения
- ✅ Интерактивное создание модулей
- ✅ Голосовые элементы управления

#### **6.2 Module Builder GUI**
```python
# Файлы для создания:
gui/module_builder/builder_window.py    # Конструктор модулей
gui/module_builder/prompt_editor.py     # Редактор промптов
gui/module_builder/test_runner.py       # Тестирование модулей
```

**Задачи:**
- ✅ Визуальный конструктор модулей
- ✅ Редактор промптов с подсветкой
- ✅ Тестирование модулей в реальном времени
- ✅ Экспорт/импорт модулей

---

## 🛠️ Техническая реализация

### **Интеграция с существующей системой**

#### **Использование существующих компонентов:**
```python
# Существующие компоненты для интеграции:
from src.core.atlas_dsl_parser import AtlasDSLParser      # DSL парсер
from src.core.macro_sequence import MacroSequence         # Исполнитель
from src.ai.macro_generator import AIMacroGenerator        # AI генератор
from src.voice.voice_assistant import VoiceAssistant      # Голосовой ассистент
from src.voice.text_to_speech import TextToSpeech         # TTS
from src.system.system_orchestrator import SystemOrchestrator # Системные команды
```

#### **Адаптация под модульную архитектуру:**
```python
# Обертки для существующих компонентов
class LegacyDSLExecutor(Executor):
    """Обертка для существующего MacroSequence"""
    
    def __init__(self):
        self.parser = AtlasDSLParser()
        self.sequence_executor = MacroSequence
    
    def execute(self, dsl_code: str) -> ExecutionResult:
        yaml_data = self.parser.parse(dsl_code)
        sequence = self.sequence_executor(yaml_data)
        return sequence.execute()

class LegacyVoiceIntegration(AIModule):
    """Обертка для существующего голосового ассистента"""
    
    def __init__(self):
        self.voice_assistant = VoiceAssistant()
        super().__init__(self.get_config())
    
    def execute(self, audio_input, context):
        return self.voice_assistant.process_voice_command(audio_input)
```

### **Система конфигурации**

#### **Module Configuration Format:**
```yaml
# config/modules/sequence_generator.yaml
name: "sequence_generator"
description: "Создает DSL последовательности по описанию"
version: "1.0.0"
author: "Macro AI Team"

# AI Configuration
ai_config:
  model: "gemini-1.5-pro"
  max_tokens: 4096
  temperature: 0.7
  
# Prompts
prompts:
  base_prompt: "prompts/sequence_generation.txt"
  context_template: "prompts/context_template.txt"
  
# Resources
resources:
  templates: true
  variables: true
  dom_selectors: true
  system_commands: true
  
# Execution
executor:
  type: "dsl_executor"
  timeout: 300
  retry_attempts: 3
  
# Keywords for module selection
keywords:
  - "автоматизация"
  - "макрос" 
  - "последовательность"
  - "открыть и сделать"
  
priority: 1
enabled: true
```

### **Система промптов**

#### **Структура промптов:**
```
src/modules/{module_name}/prompts/
├── base_prompt.txt              # Основной промпт модуля
├── context_template.txt         # Шаблон контекста
├── examples/                    # Примеры для few-shot learning
│   ├── example_1.txt
│   ├── example_2.txt
│   └── example_3.txt
├── system_instructions.txt      # Системные инструкции
└── output_format.txt           # Формат выходных данных
```

#### **Пример промпта для Sequence Generator:**
```txt
# src/modules/sequence_generator/prompts/base_prompt.txt

Ты - эксперт по автоматизации macOS через DSL язык.
Создай последовательность команд для выполнения задачи пользователя.

ДОСТУПНЫЕ КОМАНДЫ:
{dsl_commands}

ДОСТУПНЫЕ ШАБЛОНЫ:
{available_templates}

ДОСТУПНЫЕ ПЕРЕМЕННЫЕ:
{available_variables}

СИСТЕМНЫЕ КОМАНДЫ:
{system_commands}

ЛУЧШИЕ ПРАКТИКИ:
{best_practices}

ЗАДАЧА ПОЛЬЗОВАТЕЛЯ: {user_request}

КОНТЕКСТ: {context}

Создай DSL последовательность в формате:
```atlas
# Описание макроса
{dsl_code}
```

ВАЖНО:
- Используй только доступные команды и шаблоны
- Добавляй wait команды между действиями
- Проверяй существование элементов перед кликом
- Используй переменные для повторяющихся действий
```

### **Система логирования**

#### **Структура логов:**
```python
@dataclass
class ExecutionLog:
    """Лог выполнения модуля"""
    
    module_name: str
    user_input: str
    ai_result: str
    execution_result: ExecutionResult
    timestamp: datetime
    duration: float
    success: bool
    errors: List[ExecutionError]
    performance_metrics: Dict[str, float]
    context: Dict[str, Any]
    
    def to_dict(self) -> Dict:
        """Сериализация для анализа"""
        return {
            "module": self.module_name,
            "input": self.user_input,
            "success": self.success,
            "duration": self.duration,
            "errors": [error.to_dict() for error in self.errors],
            "metrics": self.performance_metrics
        }
```

#### **Log Analysis Pipeline:**
```python
class LogAnalysisPipeline:
    """Пайплайн анализа логов для самообучения"""
    
    def analyze_daily_logs(self) -> AnalysisReport:
        """Ежедневный анализ логов"""
        
        logs = self.load_logs_for_period(days=1)
        
        analysis = AnalysisReport(
            total_executions=len(logs),
            success_rate=self.calculate_success_rate(logs),
            average_duration=self.calculate_average_duration(logs),
            common_errors=self.extract_common_errors(logs),
            performance_trends=self.analyze_performance_trends(logs),
            improvement_suggestions=self.generate_suggestions(logs)
        )
        
        return analysis
    
    def extract_patterns(self, logs: List[ExecutionLog]) -> List[Pattern]:
        """Извлечение паттернов из логов"""
        
        patterns = []
        
        # Паттерны ошибок
        error_patterns = self.extract_error_patterns(logs)
        patterns.extend(error_patterns)
        
        # Паттерны производительности
        performance_patterns = self.extract_performance_patterns(logs)
        patterns.extend(performance_patterns)
        
        # Паттерны успешных выполнений
        success_patterns = self.extract_success_patterns(logs)
        patterns.extend(success_patterns)
        
        return patterns
```

---

## 📊 Метрики и мониторинг

### **KPI системы:**
- **Успешность выполнения**: >95%
- **Время отклика**: <2 секунды для простых команд
- **Точность выбора модуля**: >90%
- **Удовлетворенность пользователей**: >4.5/5

### **Мониторинг производительности:**
```python
class PerformanceMonitor:
    """Мониторинг производительности модульной системы"""
    
    def track_module_performance(self, module_name: str, execution_time: float):
        """Отслеживание производительности модуля"""
        
    def track_ai_response_time(self, module_name: str, response_time: float):
        """Отслеживание времени ответа AI"""
        
    def track_success_rate(self, module_name: str, success: bool):
        """Отслеживание успешности выполнения"""
        
    def generate_performance_report(self) -> PerformanceReport:
        """Генерация отчета о производительности"""
```

---

## 🧪 Тестирование

### **Стратегия тестирования:**

#### **Unit Tests:**
```python
# tests/modules/test_sequence_generator.py
class TestSequenceGeneratorModule:
    
    def test_dsl_generation(self):
        """Тест генерации DSL кода"""
        
    def test_context_loading(self):
        """Тест загрузки контекста"""
        
    def test_ai_result_parsing(self):
        """Тест парсинга AI результата"""
```

#### **Integration Tests:**
```python
# tests/integration/test_modular_system.py
class TestModularSystem:
    
    def test_coordinator_module_selection(self):
        """Тест выбора модуля координатором"""
        
    def test_voice_to_execution_pipeline(self):
        """Тест полного пайплайна от голоса до выполнения"""
        
    def test_learning_system_integration(self):
        """Тест интеграции системы обучения"""
```

#### **End-to-End Tests:**
```python
# tests/e2e/test_user_scenarios.py
class TestUserScenarios:
    
    def test_voice_command_execution(self):
        """Тест: 'Эй макро, открой Chrome и зайди на YouTube'"""
        
    def test_variable_creation_workflow(self):
        """Тест создания переменной через модуль"""
        
    def test_error_recovery_and_learning(self):
        """Тест восстановления после ошибки и обучения"""
```

---

## 📅 Временные рамки

### **Общий план (12-16 недель):**

| Этап | Недели | Описание | Приоритет |
|------|--------|----------|-----------|
| 1 | 1-2 | Базовая инфраструктура | КРИТИЧЕСКИЙ |
| 2 | 3-5 | Первые модули | ВЫСОКИЙ |
| 3 | 6-9 | UI Automation | ВЫСОКИЙ |
| 4 | 10-12 | Самообучение | СРЕДНИЙ |
| 5 | 13-16 | Дополнительные модули | НИЗКИЙ |
| 6 | 15-17 | GUI и интерфейс | НИЗКИЙ |

### **Критический путь:**
1. **Базовые классы** → 2. **AI Coordinator** → 3. **Sequence Generator** → 4. **Voice Integration** → 5. **UI Automation**

---

## 🎯 Готовность к запуску

### **MVP (Minimum Viable Product) - 5 недель:**
- ✅ Базовая модульная архитектура
- ✅ AI Coordinator с выбором модулей
- ✅ Sequence Generator Module (адаптация опции 6)
- ✅ Voice Handler Module (адаптация голосового ассистента)
- ✅ Базовое логирование

### **Full Release - 12-16 недель:**
- ✅ Все основные модули
- ✅ UI Automation интеграция
- ✅ Система самообучения
- ✅ GUI интерфейс
- ✅ Полная документация

**Готов начать реализацию! С чего начинаем?** 🚀
