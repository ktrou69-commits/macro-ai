"""
Реестр модулей для модульной AI системы
"""

import os
import yaml
import importlib
from typing import Dict, Any, List, Optional
from pathlib import Path

from .coordinator.ai_coordinator import AICoordinator


class ModuleRegistry:
    """Реестр и загрузчик модулей"""
    
    def __init__(self, coordinator: AICoordinator):
        self.coordinator = coordinator
        self.modules_dir = Path(__file__).parent
        self.registered_modules = {}
        
    def auto_discover_modules(self):
        """Автоматическое обнаружение и регистрация модулей"""
        print("🔍 Поиск модулей...")
        
        # Сканируем папки модулей
        for module_dir in self.modules_dir.iterdir():
            if (module_dir.is_dir() and 
                module_dir.name not in ["base", "coordinator", "__pycache__"] and
                not module_dir.name.startswith(".")):
                
                self._try_load_module(module_dir)
    
    def _try_load_module(self, module_dir: Path):
        """Попытка загрузки модуля из папки"""
        module_name = module_dir.name
        
        # Ищем module.py
        module_file = module_dir / "module.py"
        if not module_file.exists():
            print(f"⚠️ Модуль {module_name}: module.py не найден")
            return
        
        # Ищем конфигурацию
        config_file = module_dir / "config.yaml"
        config = self._load_module_config(config_file, module_name)
        
        try:
            # Импортируем модуль
            module_path = f"src.modules.{module_name}.module"
            module_spec = importlib.util.spec_from_file_location(
                module_path, module_file
            )
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module)
            
            # Ищем класс модуля (предполагаем что он называется как папка + Module)
            class_name = self._guess_module_class_name(module_name)
            module_class = getattr(module, class_name, None)
            
            if module_class:
                # Регистрируем модуль
                self.register_module(module_name, module_class, config)
                print(f"✅ Модуль {module_name} загружен")
            else:
                print(f"⚠️ Модуль {module_name}: класс {class_name} не найден")
                
        except Exception as e:
            print(f"❌ Ошибка загрузки модуля {module_name}: {e}")
    
    def _load_module_config(self, config_file: Path, module_name: str) -> Dict[str, Any]:
        """Загрузка конфигурации модуля"""
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f)
            except Exception as e:
                print(f"⚠️ Ошибка загрузки конфигурации {module_name}: {e}")
        
        # Конфигурация по умолчанию
        return {
            "name": module_name,
            "description": f"Модуль {module_name}",
            "keywords": [module_name],
            "priority": 5,
            "enabled": True
        }
    
    def _guess_module_class_name(self, module_name: str) -> str:
        """Угадывание имени класса модуля"""
        # Преобразуем snake_case в PascalCase
        parts = module_name.split('_')
        class_name = ''.join(word.capitalize() for word in parts) + 'Module'
        return class_name
    
    def register_module(self, module_name: str, module_class, config: Dict[str, Any]):
        """Регистрация модуля в координаторе"""
        enhanced_config = config.copy()
        enhanced_config["class"] = module_class
        
        self.coordinator.register_module(module_name, module_class, enhanced_config)
        self.registered_modules[module_name] = {
            "class": module_class,
            "config": enhanced_config
        }
    
    def manual_register_module(self, module_name: str, module_class, 
                              description: str, keywords: List[str], 
                              priority: int = 5):
        """Ручная регистрация модуля"""
        config = {
            "name": module_name,
            "description": description,
            "keywords": keywords,
            "priority": priority,
            "enabled": True,
            "class": module_class
        }
        
        self.register_module(module_name, module_class, config)
    
    def get_registered_modules(self) -> Dict[str, Dict[str, Any]]:
        """Получение всех зарегистрированных модулей"""
        return self.registered_modules.copy()
    
    def create_default_modules(self):
        """Создание модулей по умолчанию (заглушки)"""
        print("🔧 Создание модулей по умолчанию...")
        
        # Заглушка для sequence_generator (адаптация опции 6)
        self._create_sequence_generator_stub()
        
        # Заглушка для voice_handler
        self._create_voice_handler_stub()
        
        print("✅ Модули по умолчанию созданы")
    
    def _create_sequence_generator_stub(self):
        """Создание заглушки для sequence_generator"""
        from .base.ai_module import AIModule
        from .base.module_config import ModuleConfig
        
        class SequenceGeneratorModule(AIModule):
            def __init__(self):
                config = ModuleConfig(
                    name="sequence_generator",
                    description="Генерирует DSL последовательности по описанию пользователя",
                    when_to_use=[
                        "автоматизация", "макрос", "последовательность",
                        "открыть и сделать", "создай макрос"
                    ]
                )
                super().__init__(config)
            
            def parse_ai_result(self, ai_result: str) -> str:
                # Простая заглушка - возвращаем результат как есть
                return ai_result
        
        self.manual_register_module(
            "sequence_generator",
            SequenceGeneratorModule,
            "Генерирует DSL последовательности по описанию пользователя",
            ["автоматизация", "макрос", "последовательность", "создай"],
            priority=1
        )
    
    def _create_voice_handler_stub(self):
        """Создание заглушки для voice_handler"""
        from .base.ai_module import AIModule
        from .base.module_config import ModuleConfig
        
        class VoiceHandlerModule(AIModule):
            def __init__(self):
                config = ModuleConfig(
                    name="voice_handler",
                    description="Обрабатывает голосовые команды",
                    when_to_use=["голос", "речь", "говорить"]
                )
                super().__init__(config)
            
            def parse_ai_result(self, ai_result: str) -> str:
                return ai_result
        
        self.manual_register_module(
            "voice_handler",
            VoiceHandlerModule,
            "Обрабатывает голосовые команды",
            ["голос", "речь", "говорить"],
            priority=0  # Высший приоритет
        )


# Глобальный реестр модулей
_global_registry = None


def get_module_registry() -> ModuleRegistry:
    """Получение глобального реестра модулей"""
    global _global_registry
    if _global_registry is None:
        coordinator = AICoordinator()
        _global_registry = ModuleRegistry(coordinator)
    return _global_registry


def initialize_modular_system() -> AICoordinator:
    """
    Инициализация модульной системы
    
    Returns:
        Настроенный AI координатор
    """
    print("🚀 Инициализация модульной AI системы...")
    
    # Получаем реестр
    registry = get_module_registry()
    
    # Создаем модули по умолчанию
    registry.create_default_modules()
    
    # Автоматическое обнаружение модулей
    registry.auto_discover_modules()
    
    # Получаем координатор
    coordinator = registry.coordinator
    
    # Выводим статистику
    modules = coordinator.get_available_modules()
    print(f"✅ Модульная система инициализирована")
    print(f"📊 Загружено модулей: {len(modules)}")
    
    for module_name, module_info in modules.items():
        status = "🟢" if module_info["enabled"] else "🔴"
        print(f"   {status} {module_name}: {module_info['description']}")
    
    return coordinator


# Удобные функции для быстрого использования
def quick_process(user_input: str, input_type: str = "text") -> Dict[str, Any]:
    """Быстрая обработка пользовательского ввода"""
    coordinator = get_module_registry().coordinator
    result = coordinator.process_user_input(user_input, input_type)
    return result.to_dict()


def quick_analyze_intent(user_input: str) -> Dict[str, Any]:
    """Быстрый анализ намерений"""
    coordinator = get_module_registry().coordinator
    intent = coordinator.analyze_user_intent_only(user_input)
    return {
        "type": intent.type,
        "platforms": intent.platforms,
        "actions": intent.actions,
        "apps": intent.apps,
        "complexity": intent.complexity,
        "confidence": intent.confidence,
        "keywords": intent.keywords
    }
