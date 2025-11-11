"""
Config Service - Сервис для работы с конфигурацией
Обертка над src/utils/api_config.py
"""

from typing import Dict, Any, Optional
from pathlib import Path

class ConfigService:
    """Сервис для работы с конфигурацией API и проекта"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
    def get_api_status(self) -> Dict[str, Any]:
        """Получить статус API ключей"""
        try:
            from src.utils.api_config import api_config
            
            return {
                'gemini': {
                    'available': api_config.has_gemini(),
                    'model': api_config.gemini_model if api_config.has_gemini() else None,
                    'key_present': bool(api_config.gemini_key)
                },
                'openai': {
                    'available': api_config.has_openai(),
                    'key_present': bool(api_config.openai_key)
                },
                'anthropic': {
                    'available': api_config.has_anthropic(),
                    'key_present': bool(api_config.anthropic_key)
                }
            }
        except Exception as e:
            print(f"⚠️ Ошибка получения статуса API: {e}")
            return {
                'gemini': {'available': False, 'model': None, 'key_present': False},
                'openai': {'available': False, 'key_present': False},
                'anthropic': {'available': False, 'key_present': False}
            }
    
    def get_project_stats(self) -> Dict[str, int]:
        """Получить статистику проекта"""
        try:
            stats = {
                'templates_count': 0,
                'dsl_variables_count': 0,
                'platforms_count': 0
            }
            
            # Подсчет шаблонов (PNG файлов)
            templates_dir = self.project_root / "templates"
            if templates_dir.exists():
                png_files = list(templates_dir.rglob("*.png"))
                stats['templates_count'] = len(png_files)
                
                # Подсчет платформ (папок в Chrome/)
                chrome_dir = templates_dir / "Chrome"
                if chrome_dir.exists():
                    platforms = [d for d in chrome_dir.iterdir() if d.is_dir()]
                    stats['platforms_count'] = len(platforms)
            
            # Подсчет DSL переменных
            dsl_file = self.project_root / "templates" / "DSL_VARIABLES.txt"
            if dsl_file.exists():
                with open(dsl_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Подсчет уникальных переменных ${...}
                    import re
                    variables = re.findall(r'\$\{([^}]+)\}', content)
                    stats['dsl_variables_count'] = len(set(variables))
            
            return stats
            
        except Exception as e:
            print(f"⚠️ Ошибка получения статистики: {e}")
            return {'templates_count': 0, 'dsl_variables_count': 0, 'platforms_count': 0}
    
    def get_gemini_model(self) -> Optional[str]:
        """Получить текущую модель Gemini"""
        try:
            from src.utils.api_config import api_config
            return api_config.gemini_model if api_config.has_gemini() else None
        except Exception:
            return None
    
    def is_api_configured(self) -> bool:
        """Проверить, настроен ли хотя бы один API"""
        status = self.get_api_status()
        return any(api['available'] for api in status.values())
    
    def get_env_file_path(self) -> Path:
        """Получить путь к .env файлу"""
        return self.project_root / ".env"
    
    def get_project_info(self) -> Dict[str, Any]:
        """Получить общую информацию о проекте"""
        return {
            'name': self.project_root.name,
            'path': str(self.project_root),
            'env_exists': self.get_env_file_path().exists(),
            'api_configured': self.is_api_configured(),
            'stats': self.get_project_stats()
        }
