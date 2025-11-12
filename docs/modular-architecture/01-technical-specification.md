# 🏗️ Техническая спецификация модульной AI архитектуры

## 🎯 Обзор системы

**Цель:** Создание модульной AI-библиотеки для локальной автоматизации macOS/Windows через DSL и UI Automation с самообучением.

**Ключевые принципы:**
- 🧠 **Главный AI Coordinator** - маршрутизирует запросы между модулями
- 🔧 **Модульные AI агенты** - специализированные исполнители
- 📝 **DSL как язык выполнения** - детерминированные команды
- 🎤 **Голосовая интеграция** - мгновенный отклик + выполнение
- 📊 **Самообучение** - анализ логов и создание паттернов

## 🏗️ Архитектура системы

### **1. Главный AI Coordinator (Router)**
```python
class AICoordinator:
    """Главный маршрутизатор запросов пользователя"""
    
    def __init__(self):
        self.modules = self.load_available_modules()
        self.context_manager = ContextManager()
        self.tts = TTSManager()
        
    def process_user_input(self, input_text: str, input_type: str = "text"):
        """
        Основной метод обработки пользовательского ввода
        
        Логика:
        1. Анализ намерений пользователя
        2. Решение: обычный диалог ИЛИ запуск модуля
        3. Мгновенный отклик пользователю
        4. Выполнение через выбранный модуль
        """
        
        # Анализ намерений
        intent = self.analyze_user_intent(input_text)
        
        if intent.type == "casual_chat":
            return self.respond_normally(input_text)
        
        # Выбор модуля
        selected_module = self.select_module(intent)
        
        # Мгновенный отклик
        if input_type == "voice":
            self.tts.speak(f"Понял! Запускаю {selected_module.name}")
        
        # Выполнение
        return self.execute_module(selected_module, input_text, intent)
```

### **2. Базовый класс модуля**
```python
class AIModule:
    """Базовый класс для всех AI модулей"""
    
    def __init__(self, config: ModuleConfig):
        self.name = config.name
        self.description = config.description
        self.prompt_template = self.load_prompt(config.prompt_path)
        self.ai_agent = self.initialize_ai_agent()
        self.executor = self.initialize_executor()
        
    def execute(self, user_input: str, context: Dict) -> ModuleResult:
        """
        Главный метод выполнения модуля
        
        Этапы:
        1. Формирование промпта с контекстом
        2. AI генерация результата
        3. Парсинг и валидация
        4. Выполнение через executor
        5. Логирование результата
        """
        
        # 1. Формирование промпта
        full_prompt = self.build_prompt(user_input, context)
        
        # 2. AI генерация
        ai_result = self.ai_agent.generate(full_prompt)
        
        # 3. Парсинг
        parsed_result = self.parse_ai_result(ai_result)
        
        # 4. Выполнение
        execution_result = self.executor.execute(parsed_result)
        
        # 5. Логирование
        self.log_execution(user_input, ai_result, execution_result)
        
        return ModuleResult(
            success=execution_result.success,
            data=execution_result.data,
            logs=execution_result.logs
        )
```

### **3. Структура модулей**
```
src/modules/
├── __init__.py
├── base/
│   ├── ai_module.py              # Базовый класс AIModule
│   ├── module_config.py          # Конфигурация модулей
│   ├── ai_agent.py              # AI агент для модулей
│   └── executor.py              # Базовый исполнитель
├── coordinator/
│   ├── ai_coordinator.py        # Главный координатор
│   ├── intent_analyzer.py       # Анализ намерений
│   ├── module_selector.py       # Выбор модуля
│   └── context_manager.py       # Управление контекстом
├── sequence_generator/          # Генерация DSL последовательности
│   ├── module.py
│   ├── prompts/
│   │   ├── base_prompt.txt
│   │   ├── context_templates.txt
│   │   └── dsl_reference.txt
│   └── dsl_executor.py
├── variable_creator/            # Создание DSL переменных
│   ├── module.py
│   ├── prompts/
│   └── variable_manager.py
├── dom_extractor/              # Извлечение DOM селекторов
│   ├── module.py
│   ├── prompts/
│   └── selector_analyzer.py
├── voice_handler/              # Голосовой ввод
│   ├── module.py
│   ├── speech_processor.py
│   └── voice_router.py
├── template_architect/         # Архитектура шаблонов
│   ├── module.py
│   ├── prompts/
│   └── structure_generator.py
└── learning/                   # Самообучение
    ├── log_analyzer.py
    ├── pattern_extractor.py
    └── knowledge_updater.py
```

## 🔧 Конкретные модули

### **1. Sequence Generator Module (расширение опции 6)**
```python
class SequenceGeneratorModule(AIModule):
    """Генерация DSL последовательностей по описанию пользователя"""
    
    def __init__(self):
        config = ModuleConfig(
            name="sequence_generator",
            description="Создает DSL макросы по естественному описанию",
            prompt_path="sequence_generator/prompts/",
            when_to_use=[
                "автоматизация браузера",
                "создание макросов", 
                "последовательность действий",
                "открыть приложение и сделать"
            ]
        )
        super().__init__(config)
    
    def get_context_resources(self) -> Dict:
        """Загружает доступные ресурсы для AI"""
        return {
            "templates": self.load_templates_structure(),
            "variables": self.load_dsl_variables(), 
            "dom_selectors": self.load_dom_selectors(),
            "system_commands": self.load_system_commands(),
            "best_practices": self.load_best_practices()
        }
    
    def parse_ai_result(self, ai_result: str) -> DSLSequence:
        """Парсит AI результат в DSL последовательность"""
        # Извлечение DSL кода из AI ответа
        dsl_code = self.extract_dsl_code(ai_result)
        
        # Валидация синтаксиса
        if not self.validate_dsl_syntax(dsl_code):
            raise DSLSyntaxError("Invalid DSL syntax generated")
        
        return DSLSequence(code=dsl_code, metadata=self.extract_metadata(ai_result))
```

### **2. Variable Creator Module**
```python
class VariableCreatorModule(AIModule):
    """Создание переиспользуемых DSL переменных"""
    
    def __init__(self):
        config = ModuleConfig(
            name="variable_creator",
            description="Создает DSL переменные для повторного использования",
            prompt_path="variable_creator/prompts/",
            when_to_use=[
                "создать переменную",
                "сохранить как шаблон",
                "переиспользуемый блок"
            ]
        )
        super().__init__(config)
    
    def parse_ai_result(self, ai_result: str) -> DSLVariable:
        """Парсит AI результат в DSL переменную"""
        return DSLVariable(
            name=self.extract_variable_name(ai_result),
            code=self.extract_variable_code(ai_result),
            parameters=self.extract_parameters(ai_result),
            description=self.extract_description(ai_result)
        )
    
    def execute_result(self, variable: DSLVariable) -> ExecutionResult:
        """Сохраняет переменную в USER_VARIABLES.txt"""
        variable_manager = DSLVariableManager()
        return variable_manager.save_variable(variable)
```

### **3. DOM Extractor Module**
```python
class DOMExtractorModule(AIModule):
    """Извлечение DOM селекторов из веб-страниц"""
    
    def __init__(self):
        config = ModuleConfig(
            name="dom_extractor",
            description="Анализирует веб-страницы и извлекает селекторы",
            prompt_path="dom_extractor/prompts/",
            when_to_use=[
                "анализ веб-страницы",
                "извлечь селекторы",
                "работа с сайтом"
            ]
        )
        super().__init__(config)
    
    def analyze_webpage(self, url: str) -> WebPageAnalysis:
        """Анализирует веб-страницу и извлекает структуру"""
        selenium_analyzer = SeleniumAnalyzer()
        page_structure = selenium_analyzer.analyze_page(url)
        
        # AI анализ структуры
        ai_analysis = self.ai_agent.analyze_dom_structure(page_structure)
        
        return WebPageAnalysis(
            url=url,
            selectors=ai_analysis.selectors,
            elements=ai_analysis.elements,
            recommendations=ai_analysis.recommendations
        )
```

### **4. Voice Handler Module**
```python
class VoiceHandlerModule(AIModule):
    """Обработка голосового ввода с маршрутизацией"""
    
    def __init__(self):
        config = ModuleConfig(
            name="voice_handler",
            description="Обрабатывает голосовые команды и маршрутизирует",
            prompt_path="voice_handler/prompts/"
        )
        super().__init__(config)
        self.speech_recognizer = SpeechRecognizer()
        self.tts = TTSManager()
    
    def process_voice_input(self, audio_data: bytes) -> VoiceProcessingResult:
        """Обрабатывает голосовой ввод"""
        
        # 1. Speech-to-Text
        text_command = self.speech_recognizer.recognize(audio_data)
        
        # 2. Мгновенный отклик
        self.tts.speak("Понял, выполняю...")
        
        # 3. Анализ контекста команды
        command_context = self.analyze_voice_command(text_command)
        
        # 4. Маршрутизация
        if command_context.is_system_command():
            return self.route_to_system_module(text_command)
        elif command_context.is_web_command():
            return self.route_to_web_automation(text_command)
        else:
            return self.route_to_general_coordinator(text_command)
```

## 🎤 Голосовая интеграция

### **Архитектура голосового ввода**
```python
class VoiceIntegration:
    """Интеграция голосового ввода в модульную систему"""
    
    def __init__(self):
        self.coordinator = AICoordinator()
        self.voice_module = VoiceHandlerModule()
        self.wake_word_detector = WakeWordDetector("эй макро")
        
    def start_voice_listening(self):
        """Запуск постоянного прослушивания"""
        while True:
            audio_chunk = self.capture_audio()
            
            if self.wake_word_detector.detect(audio_chunk):
                # Активация системы
                self.tts.speak("Слушаю!")
                
                # Захват команды
                command_audio = self.capture_command()
                
                # Обработка через координатор
                result = self.coordinator.process_user_input(
                    command_audio, 
                    input_type="voice"
                )
                
                # Голосовой отчет о результате
                self.report_result(result)
```

## 📊 Система самообучения

### **Learning Module**
```python
class LearningModule:
    """Модуль самообучения на основе логов выполнения"""
    
    def __init__(self):
        self.log_analyzer = LogAnalyzer()
        self.pattern_extractor = PatternExtractor()
        self.knowledge_updater = KnowledgeUpdater()
    
    def analyze_execution_logs(self, logs: List[ExecutionLog]):
        """Анализирует логи и извлекает паттерны"""
        
        patterns = []
        
        for log in logs:
            # Анализ ошибок
            if log.has_errors():
                error_patterns = self.extract_error_patterns(log)
                patterns.extend(error_patterns)
            
            # Анализ таймингов
            if log.has_timing_data():
                timing_patterns = self.extract_timing_patterns(log)
                patterns.extend(timing_patterns)
            
            # Анализ успешных выполнений
            if log.is_successful():
                success_patterns = self.extract_success_patterns(log)
                patterns.extend(success_patterns)
        
        # Обновление базы знаний
        self.knowledge_updater.update_patterns(patterns)
        
        return patterns
    
    def extract_error_patterns(self, log: ExecutionLog) -> List[Pattern]:
        """Извлекает паттерны из ошибок"""
        patterns = []
        
        for error in log.errors:
            if error.type == "timeout":
                pattern = Pattern(
                    rule=f"После {error.action} всегда ждать {error.suggested_wait}с",
                    context=error.context,
                    confidence=0.8,
                    source="error_analysis"
                )
                patterns.append(pattern)
        
        return patterns
```

## 🔌 UI Automation интеграция

### **macOS Accessibility API**
```python
class MacOSUIAutomation:
    """Интеграция с macOS Accessibility API"""
    
    def __init__(self):
        self.ax_api = AXUIElementAPI()
        
    def get_application_elements(self, app_name: str) -> List[UIElement]:
        """Получает все UI элементы приложения"""
        app = self.ax_api.get_application(app_name)
        return self.ax_api.get_all_elements(app)
    
    def click_element_by_id(self, element_id: str) -> bool:
        """Клик по элементу через ID"""
        element = self.ax_api.find_element_by_id(element_id)
        if element:
            return self.ax_api.click_element(element)
        return False
    
    def get_element_tree(self, app_name: str) -> Dict:
        """Получает дерево элементов приложения"""
        elements = self.get_application_elements(app_name)
        return self.build_element_tree(elements)
```

### **DSL команды для UI Automation**
```atlas
# Новые DSL команды для UI Automation
click_ui_element "button_id_123"
fill_ui_field "text_field_id" "Hello World"
select_ui_option "dropdown_id" "Option 1"
get_ui_text "label_id"
wait_for_ui_element "element_id" 10s
```

## 📋 Конфигурация модулей

### **Module Registry**
```python
# src/modules/registry.py
MODULE_REGISTRY = {
    "sequence_generator": {
        "class": SequenceGeneratorModule,
        "description": "Создает DSL последовательности по описанию",
        "keywords": ["автоматизация", "макрос", "последовательность", "открыть и сделать"],
        "priority": 1
    },
    "variable_creator": {
        "class": VariableCreatorModule, 
        "description": "Создает переиспользуемые DSL переменные",
        "keywords": ["переменная", "шаблон", "сохранить", "переиспользовать"],
        "priority": 2
    },
    "dom_extractor": {
        "class": DOMExtractorModule,
        "description": "Извлекает селекторы из веб-страниц", 
        "keywords": ["веб-страница", "селекторы", "сайт", "анализ"],
        "priority": 3
    },
    "voice_handler": {
        "class": VoiceHandlerModule,
        "description": "Обрабатывает голосовые команды",
        "keywords": ["голос", "речь", "говорить"],
        "priority": 0  # Высший приоритет
    }
}
```

## 🚀 API интерфейс

### **Главный API**
```python
class ModularAI:
    """Главный API для модульной AI системы"""
    
    def __init__(self):
        self.coordinator = AICoordinator()
        self.voice_integration = VoiceIntegration()
        self.learning_module = LearningModule()
    
    # Текстовый ввод
    def process_text(self, text: str) -> AIResponse:
        return self.coordinator.process_user_input(text, "text")
    
    # Голосовой ввод
    def process_voice(self, audio_data: bytes) -> AIResponse:
        return self.coordinator.process_user_input(audio_data, "voice")
    
    # Запуск голосового прослушивания
    def start_voice_mode(self):
        self.voice_integration.start_voice_listening()
    
    # Добавление нового модуля
    def register_module(self, module_class: AIModule, config: Dict):
        self.coordinator.register_module(module_class, config)
    
    # Анализ логов для обучения
    def analyze_and_learn(self):
        logs = self.get_execution_logs()
        patterns = self.learning_module.analyze_execution_logs(logs)
        return patterns
```

---

**Следующий файл:** [02-implementation-plan.md](02-implementation-plan.md) - Детальный план реализации
