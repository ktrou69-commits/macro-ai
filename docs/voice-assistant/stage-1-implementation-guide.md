# 🛠️ Этап 1: Подробное руководство по реализации

**Детальная инструкция с примерами кода для каждого шага**

## 📋 Пошаговая реализация

### Шаг 1: Создание структуры папок

```bash
# Переходим в корень проекта
cd /Users/kostya/Desktop/local-macros

# Создаем новые папки
mkdir -p src/voice
mkdir -p src/system
mkdir -p src/memory

# Создаем __init__.py файлы
touch src/voice/__init__.py
touch src/system/__init__.py
touch src/memory/__init__.py
```

### Шаг 2: Реализация state_manager.py

**Создать файл:** `src/memory/state_manager.py`

```python
#!/usr/bin/env python3
"""
state_manager.py
Система управления состоянием выполнения макросов
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading


@dataclass
class MacroState:
    """Состояние выполнения одного макроса"""
    session_id: str
    atlas_file: str
    voice_command: Optional[str] = None
    current_step: int = 0
    total_steps: int = 0
    completed_steps: List[int] = None
    pending_steps: List[int] = None
    variables: Dict[str, Any] = None
    last_error: Optional[str] = None
    execution_strategy: List[str] = None
    start_time: str = None
    status: str = "running"  # running, paused, completed, error
    
    def __post_init__(self):
        if self.completed_steps is None:
            self.completed_steps = []
        if self.pending_steps is None:
            self.pending_steps = []
        if self.variables is None:
            self.variables = {}
        if self.execution_strategy is None:
            self.execution_strategy = ["DOM", "System", "CV"]
        if self.start_time is None:
            self.start_time = datetime.now().isoformat()
    
    def save_step_result(self, step_num: int, result: Dict[str, Any]):
        """Сохранить результат выполнения шага"""
        self.current_step = step_num
        if step_num not in self.completed_steps:
            self.completed_steps.append(step_num)
        
        # Удаляем из pending если есть
        if step_num in self.pending_steps:
            self.pending_steps.remove(step_num)
            
        # Сохраняем переменные из результата
        if 'variables' in result:
            self.variables.update(result['variables'])
            
        # Сохраняем ошибку если есть
        if 'error' in result:
            self.last_error = result['error']
            self.status = "error"
        else:
            self.last_error = None
            
    def get_context_for_ai(self) -> Dict[str, Any]:
        """Получить контекст для ИИ"""
        return {
            "session_id": self.session_id,
            "atlas_file": self.atlas_file,
            "voice_command": self.voice_command,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "progress": f"{len(self.completed_steps)}/{self.total_steps}",
            "variables": self.variables,
            "last_error": self.last_error,
            "status": self.status,
            "can_resume": self.can_resume()
        }
    
    def can_resume(self) -> bool:
        """Можно ли продолжить выполнение"""
        return (
            self.status in ["running", "paused"] and 
            len(self.pending_steps) > 0
        )
    
    def mark_completed(self):
        """Отметить макрос как завершенный"""
        self.status = "completed"
        self.pending_steps = []
    
    def mark_paused(self):
        """Приостановить выполнение"""
        self.status = "paused"


class StateManager:
    """Менеджер состояний всех макросов"""
    
    def __init__(self, storage_dir: str = "macro_states"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.active_states: Dict[str, MacroState] = {}
        self._lock = threading.Lock()
        
    def create_session(self, atlas_file: str, voice_command: str = None) -> str:
        """Создать новую сессию выполнения макроса"""
        session_id = str(uuid.uuid4())
        
        state = MacroState(
            session_id=session_id,
            atlas_file=atlas_file,
            voice_command=voice_command
        )
        
        with self._lock:
            self.active_states[session_id] = state
            
        self._save_state(state)
        return session_id
    
    def get_state(self, session_id: str) -> Optional[MacroState]:
        """Получить состояние по ID сессии"""
        with self._lock:
            if session_id in self.active_states:
                return self.active_states[session_id]
                
        # Попробовать загрузить с диска
        return self._load_state(session_id)
    
    def update_state(self, session_id: str, **kwargs):
        """Обновить состояние"""
        with self._lock:
            if session_id in self.active_states:
                state = self.active_states[session_id]
                for key, value in kwargs.items():
                    if hasattr(state, key):
                        setattr(state, key, value)
                self._save_state(state)
    
    def save_step_result(self, session_id: str, step_num: int, result: Dict[str, Any]):
        """Сохранить результат выполнения шага"""
        with self._lock:
            if session_id in self.active_states:
                state = self.active_states[session_id]
                state.save_step_result(step_num, result)
                self._save_state(state)
    
    def get_resumable_sessions(self) -> List[MacroState]:
        """Получить список сессий, которые можно продолжить"""
        resumable = []
        
        # Проверяем активные состояния
        with self._lock:
            for state in self.active_states.values():
                if state.can_resume():
                    resumable.append(state)
        
        # Проверяем сохраненные состояния
        for state_file in self.storage_dir.glob("*.json"):
            try:
                state = self._load_state_from_file(state_file)
                if state and state.can_resume():
                    resumable.append(state)
            except Exception:
                continue
                
        return resumable
    
    def _save_state(self, state: MacroState):
        """Сохранить состояние на диск"""
        state_file = self.storage_dir / f"{state.session_id}.json"
        try:
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(state), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️ Ошибка сохранения состояния {state.session_id}: {e}")
    
    def _load_state(self, session_id: str) -> Optional[MacroState]:
        """Загрузить состояние с диска"""
        state_file = self.storage_dir / f"{session_id}.json"
        return self._load_state_from_file(state_file)
    
    def _load_state_from_file(self, state_file: Path) -> Optional[MacroState]:
        """Загрузить состояние из файла"""
        try:
            if not state_file.exists():
                return None
                
            with open(state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            state = MacroState(**data)
            
            # Добавляем в активные состояния
            with self._lock:
                self.active_states[state.session_id] = state
                
            return state
        except Exception as e:
            print(f"⚠️ Ошибка загрузки состояния из {state_file}: {e}")
            return None
    
    def cleanup_old_states(self, days: int = 7):
        """Очистить старые состояния"""
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        
        for state_file in self.storage_dir.glob("*.json"):
            if state_file.stat().st_mtime < cutoff_time:
                try:
                    state_file.unlink()
                    print(f"🗑️ Удалено старое состояние: {state_file.name}")
                except Exception as e:
                    print(f"⚠️ Ошибка удаления {state_file}: {e}")


# Глобальный экземпляр менеджера состояний
state_manager = StateManager()
```

### Шаг 3: Интеграция с macro_sequence.py

**Найти файл:** `src/core/macro_sequence.py`

**Добавить импорты в начало файла:**
```python
# Добавить после существующих импортов
from src.memory.state_manager import state_manager, MacroState
```

**Найти класс MacroSequence и добавить методы:**
```python
class MacroSequence:
    def __init__(self, config_file=None):
        # Существующий код...
        
        # НОВОЕ: Поддержка состояний
        self.session_id = None
        self.state_manager = state_manager
        
    def start_session(self, atlas_file: str, voice_command: str = None) -> str:
        """Начать новую сессию выполнения"""
        self.session_id = self.state_manager.create_session(
            atlas_file=atlas_file,
            voice_command=voice_command
        )
        return self.session_id
    
    def resume_session(self, session_id: str) -> bool:
        """Продолжить существующую сессию"""
        state = self.state_manager.get_state(session_id)
        if not state or not state.can_resume():
            return False
            
        self.session_id = session_id
        # Восстановить контекст выполнения
        self._restore_context_from_state(state)
        return True
    
    def _restore_context_from_state(self, state: MacroState):
        """Восстановить контекст выполнения из состояния"""
        # Восстановить переменные
        if hasattr(self, 'variables'):
            self.variables.update(state.variables)
        else:
            self.variables = state.variables.copy()
            
        # Установить текущий шаг
        self.current_step_index = state.current_step
        
        print(f"🔄 Восстановлена сессия {state.session_id}")
        print(f"📍 Текущий шаг: {state.current_step}/{state.total_steps}")
        print(f"📝 Переменные: {len(state.variables)}")
    
    def save_step_result(self, step_num: int, result: Dict[str, Any]):
        """Сохранить результат выполнения шага"""
        if self.session_id:
            self.state_manager.save_step_result(
                session_id=self.session_id,
                step_num=step_num,
                result=result
            )
    
    def get_ai_context(self) -> Dict[str, Any]:
        """Получить контекст для ИИ"""
        if self.session_id:
            state = self.state_manager.get_state(self.session_id)
            if state:
                return state.get_context_for_ai()
        return {}
```

### Шаг 4: Расширение atlas_dsl_parser.py

**Найти файл:** `src/core/atlas_dsl_parser.py`

**Добавить в класс AtlasDSLParser новые методы:**
```python
class AtlasDSLParser:
    def __init__(self, templates_base_path: str = "templates", dom_selectors_path: str = "dom_selectors"):
        # Существующий код...
        
        # НОВОЕ: Поддержка системных команд
        self.system_commands_whitelist = {
            'open_app', 'close_app', 'focus_window', 
            'take_screenshot', 'copy_to_clipboard',
            'list_processes', 'switch_desktop'
        }
    
    def parse_line(self, line: str, line_num: int) -> Dict[str, Any]:
        """Парсинг одной строки DSL (расширенная версия)"""
        line = line.strip()
        
        # Пропускаем пустые строки и комментарии
        if not line or line.startswith('#'):
            return None
            
        # НОВОЕ: Обработка @system команд
        if line.startswith('@system'):
            return self.parse_system_command(line, line_num)
            
        # Существующий код парсинга обычных команд...
        return self.parse_regular_command(line, line_num)
    
    def parse_system_command(self, line: str, line_num: int) -> Dict[str, Any]:
        """Парсинг @system команд"""
        # Убираем префикс '@system '
        command_part = line[8:].strip()
        
        # Парсим команду и аргументы
        parts = command_part.split(' ', 1)
        command = parts[0]
        args = parts[1] if len(parts) > 1 else ""
        
        # Проверяем whitelist
        if command not in self.system_commands_whitelist:
            raise ValueError(f"Системная команда '{command}' не разрешена (строка {line_num})")
        
        return {
            'action': 'system_command',
            'command': command,
            'args': args,
            'hidden': True,  # Не показывать в UI
            'line_num': line_num,
            'original_line': line
        }
    
    def parse_regular_command(self, line: str, line_num: int) -> Dict[str, Any]:
        """Парсинг обычных команд (существующий код)"""
        # Здесь остается существующая логика парсинга
        # click, type, wait, etc.
        pass
    
    def is_system_command(self, parsed_step: Dict[str, Any]) -> bool:
        """Проверка, является ли команда системной"""
        return parsed_step.get('action') == 'system_command'
```

### Шаг 5: Создание базового system_orchestrator.py

**Создать файл:** `src/system/system_orchestrator.py`

```python
#!/usr/bin/env python3
"""
system_orchestrator.py
Оркестратор выбора стратегии выполнения команд
"""

from typing import Dict, Any, Optional, List
from enum import Enum


class ExecutionStrategy(Enum):
    """Стратегии выполнения команд"""
    DOM = "dom"
    SYSTEM = "system"
    CV = "cv"


class SystemOrchestrator:
    """Оркестратор системных команд и выбора стратегии"""
    
    def __init__(self):
        self.system_commands = {
            'open_app', 'close_app', 'focus_window',
            'take_screenshot', 'copy_to_clipboard',
            'list_processes', 'switch_desktop'
        }
        
        self.web_contexts = {
            'chrome', 'safari', 'firefox', 'browser'
        }
    
    def choose_execution_strategy(self, command: Dict[str, Any], context: Dict[str, Any] = None) -> ExecutionStrategy:
        """
        Выбор стратегии выполнения команды
        
        Приоритет:
        1. DOM (если веб-контекст)
        2. System API (если системная команда)
        3. CV (универсальный fallback)
        """
        if context is None:
            context = {}
            
        # 1. Проверяем системные команды
        if self.is_system_command(command):
            return ExecutionStrategy.SYSTEM
            
        # 2. Проверяем веб-контекст
        if self.is_web_context(context):
            return ExecutionStrategy.DOM
            
        # 3. Fallback на CV
        return ExecutionStrategy.CV
    
    def is_system_command(self, command: Dict[str, Any]) -> bool:
        """Проверка, является ли команда системной"""
        if command.get('action') == 'system_command':
            return True
            
        # Проверяем по названию команды
        cmd_name = command.get('command', '')
        return cmd_name in self.system_commands
    
    def is_web_context(self, context: Dict[str, Any]) -> bool:
        """Проверка веб-контекста"""
        app_name = context.get('current_app', '').lower()
        return any(web_app in app_name for web_app in self.web_contexts)
    
    def execute_system_command(self, command: str, args: str = "") -> Dict[str, Any]:
        """
        Выполнение системной команды
        Пока заглушка - реализация в Этапе 2
        """
        print(f"🔧 Выполнение системной команды: {command} {args}")
        
        # Заглушка для тестирования
        return {
            'success': True,
            'command': command,
            'args': args,
            'result': f"Команда {command} выполнена успешно"
        }
    
    def get_available_strategies(self) -> List[str]:
        """Получить список доступных стратегий"""
        return [strategy.value for strategy in ExecutionStrategy]


# Глобальный экземпляр оркестратора
system_orchestrator = SystemOrchestrator()
```

### Шаг 6: Создание тестов

**Создать файл:** `tests/test_stage1_basic.py`

```python
#!/usr/bin/env python3
"""
Тесты для Этапа 1: Базовая архитектура
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.memory.state_manager import StateManager, MacroState
from src.system.system_orchestrator import SystemOrchestrator, ExecutionStrategy
from src.core.atlas_dsl_parser import AtlasDSLParser


class TestStateManager:
    """Тесты менеджера состояний"""
    
    def setup_method(self):
        """Настройка для каждого теста"""
        self.temp_dir = tempfile.mkdtemp()
        self.state_manager = StateManager(storage_dir=self.temp_dir)
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        shutil.rmtree(self.temp_dir)
    
    def test_create_session(self):
        """Тест создания сессии"""
        session_id = self.state_manager.create_session(
            atlas_file="test.atlas",
            voice_command="открой хром"
        )
        
        assert session_id is not None
        assert len(session_id) == 36  # UUID длина
        
        state = self.state_manager.get_state(session_id)
        assert state is not None
        assert state.atlas_file == "test.atlas"
        assert state.voice_command == "открой хром"
    
    def test_save_step_result(self):
        """Тест сохранения результата шага"""
        session_id = self.state_manager.create_session("test.atlas")
        
        result = {
            'success': True,
            'variables': {'screenshot_path': '/tmp/test.png'}
        }
        
        self.state_manager.save_step_result(session_id, 1, result)
        
        state = self.state_manager.get_state(session_id)
        assert state.current_step == 1
        assert 1 in state.completed_steps
        assert state.variables['screenshot_path'] == '/tmp/test.png'
    
    def test_resumable_sessions(self):
        """Тест получения возобновляемых сессий"""
        # Создаем сессию с pending шагами
        session_id = self.state_manager.create_session("test.atlas")
        self.state_manager.update_state(
            session_id, 
            pending_steps=[2, 3, 4],
            status="paused"
        )
        
        resumable = self.state_manager.get_resumable_sessions()
        assert len(resumable) == 1
        assert resumable[0].session_id == session_id


class TestSystemOrchestrator:
    """Тесты системного оркестратора"""
    
    def setup_method(self):
        self.orchestrator = SystemOrchestrator()
    
    def test_system_command_detection(self):
        """Тест определения системных команд"""
        system_cmd = {
            'action': 'system_command',
            'command': 'open_app'
        }
        
        regular_cmd = {
            'action': 'click',
            'template': 'button.png'
        }
        
        assert self.orchestrator.is_system_command(system_cmd) == True
        assert self.orchestrator.is_system_command(regular_cmd) == False
    
    def test_web_context_detection(self):
        """Тест определения веб-контекста"""
        web_context = {'current_app': 'Google Chrome'}
        desktop_context = {'current_app': 'Finder'}
        
        assert self.orchestrator.is_web_context(web_context) == True
        assert self.orchestrator.is_web_context(desktop_context) == False
    
    def test_strategy_selection(self):
        """Тест выбора стратегии выполнения"""
        # Системная команда
        system_cmd = {'action': 'system_command', 'command': 'open_app'}
        strategy = self.orchestrator.choose_execution_strategy(system_cmd)
        assert strategy == ExecutionStrategy.SYSTEM
        
        # Веб-контекст
        web_cmd = {'action': 'click', 'template': 'button.png'}
        web_context = {'current_app': 'Chrome'}
        strategy = self.orchestrator.choose_execution_strategy(web_cmd, web_context)
        assert strategy == ExecutionStrategy.DOM
        
        # Fallback на CV
        desktop_cmd = {'action': 'click', 'template': 'button.png'}
        desktop_context = {'current_app': 'Finder'}
        strategy = self.orchestrator.choose_execution_strategy(desktop_cmd, desktop_context)
        assert strategy == ExecutionStrategy.CV


class TestAtlasDSLParser:
    """Тесты парсера DSL с поддержкой @system команд"""
    
    def setup_method(self):
        self.parser = AtlasDSLParser()
    
    def test_system_command_parsing(self):
        """Тест парсинга @system команд"""
        line = '@system open_app "Chrome"'
        result = self.parser.parse_system_command(line, 1)
        
        assert result['action'] == 'system_command'
        assert result['command'] == 'open_app'
        assert result['args'] == '"Chrome"'
        assert result['hidden'] == True
    
    def test_system_command_whitelist(self):
        """Тест whitelist системных команд"""
        # Разрешенная команда
        allowed_line = '@system open_app "Chrome"'
        result = self.parser.parse_system_command(allowed_line, 1)
        assert result is not None
        
        # Запрещенная команда
        forbidden_line = '@system rm -rf /'
        with pytest.raises(ValueError):
            self.parser.parse_system_command(forbidden_line, 1)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```

## 🚀 Запуск и тестирование

### Команды для тестирования:

```bash
# Запуск тестов
cd /Users/kostya/Desktop/local-macros
python -m pytest tests/test_stage1_basic.py -v

# Проверка импортов
python -c "from src.memory.state_manager import state_manager; print('✅ StateManager работает')"
python -c "from src.system.system_orchestrator import system_orchestrator; print('✅ SystemOrchestrator работает')"

# Тест интеграции с существующим кодом
python src/main.py  # Должен работать без ошибок
```

## ✅ Критерии готовности Этапа 1

- [ ] Все новые папки созданы
- [ ] StateManager сохраняет и загружает состояния
- [ ] MacroSequence интегрирован с StateManager
- [ ] AtlasDSLParser поддерживает @system команды
- [ ] SystemOrchestrator выбирает стратегии
- [ ] Все тесты проходят
- [ ] Существующий функционал не сломан
- [ ] Документация обновлена

**После завершения этого этапа у вас будет готовая базовая архитектура для интеграции голосового ассистента!**
