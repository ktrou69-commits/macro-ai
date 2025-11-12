# Модульная AI Архитектура - Техническая Документация

## 🏗️ Архитектурный Обзор

### Основная Концепция
Модульная AI система представляет собой микросервисную архитектуру для автоматизации macOS, где каждый модуль является независимым AI-агентом, специализирующимся на конкретных задачах.

### Ключевые Принципы
- **Separation of Concerns**: Каждый модуль отвечает за свою область
- **Plugin Architecture**: Динамическая загрузка и регистрация модулей
- **AI-First Design**: AI интегрирован на всех уровнях системы
- **Graceful Degradation**: Система работает даже при отказе отдельных компонентов

## 🔧 Компоненты Системы

### 1. Core Infrastructure (`src/modules/base/`)

#### AIAgent (`ai_agent.py`)
```python
class AIAgent:
    """Универсальный AI агент с поддержкой multiple providers"""
    - Поддержка Gemini API (новый + legacy)
    - Автоматический fallback между версиями
    - Mock режим для тестирования
    - Загрузка .env конфигурации
```

**Особенности:**
- Dual API support: `google-genai` → `google-generativeai`
- Environment detection и graceful fallback
- Structured error handling с детальными сообщениями

#### ModuleConfig (`module_config.py`)
```python
@dataclass
class ModuleConfig:
    """Конфигурация модуля"""
    - AIConfig: настройки AI модели
    - ExecutorConfig: конфигурация исполнителя
    - ResourcesConfig: требуемые ресурсы
    - Metadata: метаинформация модуля
```

#### AIModule (`ai_module.py`)
```python
class AIModule(ABC):
    """Базовый класс для всех AI модулей"""
    - Стандартизированный lifecycle
    - Интеграция с AI агентом
    - Система логирования
    - Resource management
```

#### Executor (`executor.py`)
```python
class DSLExecutor(Executor):
    """Исполнитель DSL кода"""
    - Интеграция с AtlasDSLParser
    - Поддержка MacroRunner
    - Error handling и recovery
```

#### ModuleResult (`module_result.py`)
```python
@dataclass
class ModuleResult:
    """Стандартизированный результат выполнения"""
    - Unified response format
    - Structured error reporting
    - Execution metrics
    - Serialization support
```

### 2. Coordination Layer (`src/modules/coordinator/`)

#### AICoordinator (`ai_coordinator.py`)
```python
class AICoordinator:
    """Главный маршрутизатор системы"""
    - Intent analysis и routing
    - Module selection logic
    - Chat fallback mechanism
    - Statistics collection
```

**Архитектурные решения:**
- **Router Pattern**: Централизованная маршрутизация запросов
- **Strategy Pattern**: Выбор стратегии обработки (module vs chat)
- **Observer Pattern**: Логирование и метрики

#### IntentAnalyzer (`intent_analyzer.py`)
```python
class IntentAnalyzer:
    """Анализатор намерений пользователя"""
    - Platform detection (chrome, youtube, etc.)
    - Action classification (open, create, etc.)
    - Complexity assessment
    - Confidence scoring
```

**NLP Pipeline:**
1. Text preprocessing и tokenization
2. Keyword extraction и matching
3. Pattern recognition
4. Confidence calculation

#### ModuleSelector (`module_selector.py`)
```python
class ModuleSelector:
    """Селектор модулей на основе намерений"""
    - Keyword matching algorithm
    - Priority-based selection
    - Fallback strategies
```

### 3. Module Registry (`src/modules/registry.py`)

```python
class ModuleRegistry:
    """Система управления модулями"""
    - Dynamic module discovery
    - Configuration loading
    - Dependency resolution
    - Health monitoring
```

**Discovery Algorithm:**
1. Filesystem scan для модулей
2. Configuration validation
3. Dependency checking
4. Registration в coordinator

## 🤖 Первый Модуль: sequence_generator

### Архитектура Модуля
```
src/modules/sequence_generator/
├── module.py              # Главный класс модуля
├── config.yaml           # Конфигурация
├── prompts/              # AI промпты
│   ├── base_prompt.txt   # Основной промпт
│   └── context_template.txt # Шаблон контекста
└── __init__.py           # Инициализация
```

### Класс SequenceGeneratorModule
```python
class SequenceGeneratorModule(AIModule):
    """Генератор DSL последовательностей"""
    
    def execute(self, user_input: str) -> ModuleResult:
        # 1. Загрузка ресурсов через AIMacroGenerator
        # 2. Построение AI промпта с контекстом
        # 3. Генерация DSL через AI агент
        # 4. Парсинг и валидация результата
        # 5. Сохранение .atlas файла
        # 6. Возврат структурированного результата
```

### Интеграция с Legacy System
- **AIMacroGenerator**: Загрузка templates, variables, DOM selectors
- **AtlasDSLParser**: Валидация и выполнение DSL
- **MacroRunner**: Исполнение сгенерированных макросов

### AI Prompt Engineering
```
СИСТЕМА: Ты AI генератор макросов...
КОНТЕКСТ: {templates}, {variables}, {dom_selectors}
ЗАДАЧА: {user_input}
ФОРМАТ: НАЗВАНИЕ + DSL КОД + ОПИСАНИЕ
```

## 🔄 Data Flow

### 1. Request Processing
```
User Input → AICoordinator → IntentAnalyzer → Intent
```

### 2. Module Selection
```
Intent → ModuleSelector → Module Selection → Module Instance
```

### 3. Module Execution
```
Module → AIAgent → Gemini API → DSL Generation → File Save → Result
```

### 4. Response Formation
```
ModuleResult → AICoordinator → User Response
```

## 🛠️ Technical Stack

### Core Dependencies
- **Python 3.8+**: Основной язык
- **google-genai**: Новый Gemini API
- **google-generativeai**: Legacy Gemini API (fallback)
- **pyyaml**: Конфигурационные файлы
- **python-dotenv**: Environment variables

### Integration Points
- **AtlasDSLParser**: DSL parsing и validation
- **MacroRunner**: Macro execution engine
- **AIMacroGenerator**: Resource loading system

## 🔒 Error Handling Strategy

### 1. AI API Failures
- Automatic fallback: new API → legacy API → mock mode
- Graceful degradation с информативными сообщениями
- Retry logic с exponential backoff

### 2. Module Failures
- Isolated failure containment
- Fallback to chat mode
- Detailed error logging

### 3. Configuration Errors
- Validation на startup
- Default value fallbacks
- User-friendly error messages

## 📊 Monitoring & Observability

### Logging Strategy
- **Coordinator Level**: Request routing и statistics
- **Module Level**: Execution details и performance
- **AI Agent Level**: API calls и responses

### Metrics Collection
```python
{
    "total_requests": int,
    "chat_requests": int, 
    "module_requests": int,
    "successful_executions": int,
    "failed_executions": int,
    "success_rate": float,
    "average_response_time": float
}
```

## 🚀 Performance Considerations

### Lazy Loading
- Модули загружаются только при необходимости
- AI клиенты инициализируются по требованию
- Resource caching в AIMacroGenerator

### Memory Management
- Singleton pattern для координатора
- Module instance caching
- Cleanup на shutdown

### Scalability
- Stateless module design
- Horizontal scaling готовность
- Plugin architecture для расширения

## 🔧 Development Workflow

### Adding New Module
1. Создать директорию `src/modules/new_module/`
2. Implement `NewModule(AIModule)`
3. Создать `config.yaml`
4. Добавить промпты в `prompts/`
5. Registry автоматически обнаружит модуль

### Testing Strategy
- Unit tests для каждого компонента
- Integration tests для module workflows
- Mock режим для AI testing
- Demo applications для E2E testing

## 📈 Future Architecture Considerations

### Planned Extensions
- **Voice Module**: Speech-to-text integration
- **DOM Extractor**: Web scraping automation
- **Variable Creator**: DSL variable management
- **Learning Module**: Pattern recognition и optimization

### Scalability Roadmap
- **Distributed Architecture**: Multi-machine deployment
- **Event-Driven**: Async message passing
- **Microservices**: Container-based deployment
- **API Gateway**: External API exposure
