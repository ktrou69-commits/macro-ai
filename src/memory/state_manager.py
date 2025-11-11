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
        seen_session_ids = set()
        
        # Проверяем активные состояния
        with self._lock:
            for state in self.active_states.values():
                if state.can_resume() and state.session_id not in seen_session_ids:
                    resumable.append(state)
                    seen_session_ids.add(state.session_id)
        
        # Проверяем сохраненные состояния (только те, которых нет в активных)
        for state_file in self.storage_dir.glob("*.json"):
            try:
                session_id = state_file.stem
                if session_id not in seen_session_ids:
                    state = self._load_state_from_file(state_file)
                    if state and state.can_resume():
                        resumable.append(state)
                        seen_session_ids.add(state.session_id)
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
