"""
Конфигурация модулей
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path


@dataclass
class AIConfig:
    """Конфигурация AI агента"""
    model: str = "gemini-2.5-flash"
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 30


@dataclass
class ExecutorConfig:
    """Конфигурация исполнителя"""
    type: str = "none"  # none, dsl_executor, custom
    timeout: int = 60
    retry_attempts: int = 2


@dataclass
class ResourcesConfig:
    """Конфигурация ресурсов модуля"""
    templates: bool = False
    variables: bool = False
    dom_selectors: bool = False
    system_commands: bool = False
    custom_data: bool = False


@dataclass
class ModuleConfig:
    """Конфигурация модуля"""
    name: str
    description: str
    version: str = "1.0.0"
    author: str = "Macro AI"
    
    # Пути
    prompt_path: str = ""
    config_path: str = ""
    
    # Ключевые слова для активации
    when_to_use: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    
    # Конфигурации
    ai_config: AIConfig = field(default_factory=AIConfig)
    executor_config: ExecutorConfig = field(default_factory=ExecutorConfig)
    resources_config: ResourcesConfig = field(default_factory=ResourcesConfig)
    
    # Приоритет и статус
    priority: int = 5  # 0 = высший, 10 = низший
    enabled: bool = True
    
    # Дополнительные настройки
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        # Объединяем when_to_use и keywords
        all_keywords = self.when_to_use + self.keywords
        self.keywords = list(set(all_keywords))  # Убираем дубликаты
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModuleConfig':
        """Создание конфигурации из словаря"""
        ai_config = AIConfig(**data.get('ai_config', {}))
        executor_config = ExecutorConfig(**data.get('executor_config', {}))
        resources_config = ResourcesConfig(**data.get('resources_config', {}))
        
        return cls(
            name=data['name'],
            description=data['description'],
            version=data.get('version', '1.0.0'),
            author=data.get('author', 'Macro AI'),
            prompt_path=data.get('prompt_path', ''),
            config_path=data.get('config_path', ''),
            when_to_use=data.get('when_to_use', []),
            keywords=data.get('keywords', []),
            ai_config=ai_config,
            executor_config=executor_config,
            resources_config=resources_config,
            priority=data.get('priority', 5),
            enabled=data.get('enabled', True),
            metadata=data.get('metadata', {})
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Сериализация конфигурации"""
        return {
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'author': self.author,
            'prompt_path': self.prompt_path,
            'config_path': self.config_path,
            'when_to_use': self.when_to_use,
            'keywords': self.keywords,
            'ai_config': {
                'model': self.ai_config.model,
                'max_tokens': self.ai_config.max_tokens,
                'temperature': self.ai_config.temperature,
                'timeout': self.ai_config.timeout
            },
            'executor_config': {
                'type': self.executor_config.type,
                'timeout': self.executor_config.timeout,
                'retry_attempts': self.executor_config.retry_attempts
            },
            'resources_config': {
                'templates': self.resources_config.templates,
                'variables': self.resources_config.variables,
                'dom_selectors': self.resources_config.dom_selectors,
                'system_commands': self.resources_config.system_commands,
                'custom_data': self.resources_config.custom_data
            },
            'priority': self.priority,
            'enabled': self.enabled,
            'metadata': self.metadata
        }
