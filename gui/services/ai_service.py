"""
AI Service - Сервис для работы с AI генерацией
Обертка над src/ai/prompt_updater.py и utils/dsl_generator.py
"""

from PySide6.QtCore import QObject, Signal, QThread
from pathlib import Path
import threading
from typing import Callable, Optional, Dict, Any
import traceback

class AIWorker(QThread):
    """Рабочий поток для AI операций"""
    
    # Сигналы для коммуникации с UI
    generation_finished = Signal(bool, str, dict)  # success, result, metadata
    progress_updated = Signal(str)  # status message
    
    def __init__(self, operation: str, **kwargs):
        super().__init__()
        self.operation = operation
        self.kwargs = kwargs
        
    def run(self):
        """Выполнение AI операции в отдельном потоке"""
        try:
            if self.operation == "generate_macro":
                self._generate_macro()
            elif self.operation == "create_dsl_variable":
                self._create_dsl_variable()
            elif self.operation == "add_platform":
                self._add_platform()
        except Exception as e:
            error_msg = f"Ошибка AI операции: {str(e)}"
            print(f"❌ {error_msg}")
            print(traceback.format_exc())
            self.generation_finished.emit(False, error_msg, {})
    
    def _generate_macro(self):
        """Генерация макроса через AI"""
        user_request = self.kwargs.get('user_request', '')
        project_root = self.kwargs.get('project_root')
        
        self.progress_updated.emit("🤖 Анализирую запрос...")
        
        try:
            # Импортируем DSL генератор
            import sys
            sys.path.insert(0, str(project_root))
            from utils.dsl_generator import DSLGenerator
            
            self.progress_updated.emit("🔄 Генерирую макрос через AI...")
            
            # Создаем генератор
            generator = DSLGenerator(project_root)
            
            # Генерируем макрос
            result = generator.generate_macro_from_description(user_request)
            
            if result and result.get('success'):
                macro_code = result.get('macro_code', '')
                description = result.get('description', '')
                platform = result.get('platform', 'Unknown')
                
                self.progress_updated.emit("✅ Макрос сгенерирован!")
                
                # Возвращаем результат
                self.generation_finished.emit(True, macro_code, {
                    'description': description,
                    'platform': platform,
                    'type': 'macro'
                })
            else:
                error_msg = result.get('error', 'Неизвестная ошибка генерации')
                self.generation_finished.emit(False, f"❌ {error_msg}", {})
                
        except ImportError as e:
            self.generation_finished.emit(False, f"❌ Модуль не найден: {e}", {})
        except Exception as e:
            self.generation_finished.emit(False, f"❌ Ошибка генерации: {e}", {})
    
    def _create_dsl_variable(self):
        """Создание DSL переменной через AI"""
        description = self.kwargs.get('description', '')
        project_root = self.kwargs.get('project_root')
        
        self.progress_updated.emit("🤖 Создаю DSL переменную...")
        
        try:
            import sys
            sys.path.insert(0, str(project_root))
            from utils.dsl_generator import DSLGenerator
            
            generator = DSLGenerator(project_root)
            result = generator.generate_dsl_variable_from_description(description)
            
            if result and result.get('success'):
                var_name = result.get('name', '')
                var_code = result.get('code', '')
                var_description = result.get('description', '')
                
                self.progress_updated.emit("✅ DSL переменная создана!")
                
                self.generation_finished.emit(True, var_code, {
                    'name': var_name,
                    'description': var_description,
                    'type': 'dsl_variable'
                })
            else:
                error_msg = result.get('error', 'Ошибка создания переменной')
                self.generation_finished.emit(False, f"❌ {error_msg}", {})
                
        except Exception as e:
            self.generation_finished.emit(False, f"❌ Ошибка: {e}", {})
    
    def _add_platform(self):
        """Добавление новой платформы через AI"""
        platform_name = self.kwargs.get('platform_name', '')
        description = self.kwargs.get('description', '')
        project_root = self.kwargs.get('project_root')
        
        self.progress_updated.emit(f"🤖 Создаю структуру для {platform_name}...")
        
        try:
            import sys
            sys.path.insert(0, str(project_root))
            from src.ai.prompt_updater import PromptUpdater
            
            updater = PromptUpdater(project_root)
            success = updater.add_platform(platform_name, description)
            
            if success:
                self.progress_updated.emit("✅ Платформа добавлена!")
                self.generation_finished.emit(True, f"Платформа {platform_name} успешно добавлена", {
                    'platform': platform_name,
                    'type': 'platform'
                })
            else:
                self.generation_finished.emit(False, "❌ Ошибка добавления платформы", {})
                
        except Exception as e:
            self.generation_finished.emit(False, f"❌ Ошибка: {e}", {})


class AIService(QObject):
    """Сервис для работы с AI генерацией"""
    
    # Сигналы для UI
    generation_started = Signal()
    generation_finished = Signal(bool, str, dict)  # success, result, metadata
    progress_updated = Signal(str)  # status message
    
    def __init__(self, project_root: Path):
        super().__init__()
        self.project_root = project_root
        self.current_worker = None
        
    def generate_macro_async(self, user_request: str):
        """Асинхронная генерация макроса"""
        if self.current_worker and self.current_worker.isRunning():
            print("⚠️ AI уже работает, ждите завершения")
            return
        
        self.generation_started.emit()
        
        # Создаем рабочий поток
        self.current_worker = AIWorker(
            "generate_macro",
            user_request=user_request,
            project_root=self.project_root
        )
        
        # Подключаем сигналы
        self.current_worker.generation_finished.connect(self._on_generation_finished)
        self.current_worker.progress_updated.connect(self.progress_updated.emit)
        
        # Запускаем
        self.current_worker.start()
        
    def create_dsl_variable_async(self, description: str):
        """Асинхронное создание DSL переменной"""
        if self.current_worker and self.current_worker.isRunning():
            print("⚠️ AI уже работает, ждите завершения")
            return
        
        self.generation_started.emit()
        
        self.current_worker = AIWorker(
            "create_dsl_variable",
            description=description,
            project_root=self.project_root
        )
        
        self.current_worker.generation_finished.connect(self._on_generation_finished)
        self.current_worker.progress_updated.connect(self.progress_updated.emit)
        
        self.current_worker.start()
        
    def add_platform_async(self, platform_name: str, description: str):
        """Асинхронное добавление платформы"""
        if self.current_worker and self.current_worker.isRunning():
            print("⚠️ AI уже работает, ждите завершения")
            return
        
        self.generation_started.emit()
        
        self.current_worker = AIWorker(
            "add_platform",
            platform_name=platform_name,
            description=description,
            project_root=self.project_root
        )
        
        self.current_worker.generation_finished.connect(self._on_generation_finished)
        self.current_worker.progress_updated.connect(self.progress_updated.emit)
        
        self.current_worker.start()
    
    def _on_generation_finished(self, success: bool, result: str, metadata: dict):
        """Обработка завершения генерации"""
        self.generation_finished.emit(success, result, metadata)
        
        # Очищаем ссылку на worker
        if self.current_worker:
            self.current_worker.deleteLater()
            self.current_worker = None
    
    def is_busy(self) -> bool:
        """Проверка, занят ли сервис"""
        return self.current_worker is not None and self.current_worker.isRunning()
    
    def get_available_templates(self) -> Dict[str, list]:
        """Получение списка доступных шаблонов"""
        try:
            templates = {}
            templates_dir = self.project_root / "templates"
            
            if templates_dir.exists():
                for platform_dir in templates_dir.iterdir():
                    if platform_dir.is_dir() and platform_dir.name != "__pycache__":
                        png_files = list(platform_dir.rglob("*.png"))
                        if png_files:
                            templates[platform_dir.name] = [f.name for f in png_files]
            
            return templates
        except Exception as e:
            print(f"⚠️ Ошибка получения шаблонов: {e}")
            return {}
    
    def get_dsl_variables(self) -> Dict[str, str]:
        """Получение списка DSL переменных"""
        try:
            variables = {}
            dsl_file = self.project_root / "templates" / "DSL_VARIABLES.txt"
            
            if dsl_file.exists():
                with open(dsl_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Простой парсинг переменных
                import re
                pattern = r'\$\{([^}]+)\}'
                matches = re.findall(pattern, content)
                
                for var in matches:
                    variables[var] = f"DSL переменная: {var}"
            
            return variables
        except Exception as e:
            print(f"⚠️ Ошибка получения DSL переменных: {e}")
            return {}
