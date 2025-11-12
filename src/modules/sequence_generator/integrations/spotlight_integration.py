"""
Интеграция со Spotlight поиском macOS
"""

import subprocess
import json
import logging
from typing import List, Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class SpotlightIntegration:
    """Интеграция со Spotlight поиском macOS"""
    
    def __init__(self):
        self.search_cache = {}
        self.common_searches = self._load_common_searches()
    
    def _load_common_searches(self) -> Dict[str, str]:
        """Загрузка часто используемых поисковых запросов"""
        return {
            # Приложения
            "калькулятор": "Calculator",
            "calculator": "Calculator",
            "finder": "Finder",
            "файлы": "Finder",
            "настройки": "System Preferences",
            "preferences": "System Preferences",
            "терминал": "Terminal",
            "terminal": "Terminal",
            "браузер": "Safari",
            "safari": "Safari",
            "chrome": "Google Chrome",
            "хром": "Google Chrome",
            
            # Системные функции
            "скриншот": "Screenshot",
            "снимок экрана": "Screenshot",
            "активность": "Activity Monitor",
            "мониторинг": "Activity Monitor",
            "диски": "Disk Utility",
            "дисковая утилита": "Disk Utility",
            
            # Документы и файлы
            "документы": "Documents",
            "загрузки": "Downloads",
            "рабочий стол": "Desktop",
            "изображения": "Pictures",
            "музыка": "Music",
            "видео": "Movies"
        }
    
    def search_spotlight(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Поиск через Spotlight"""
        try:
            # Используем mdfind для поиска
            cmd = ['mdfind', '-limit', str(limit), query]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                paths = result.stdout.strip().split('\n')
                results = []
                
                for path in paths:
                    if path:
                        item_info = self._get_item_info(path)
                        if item_info:
                            results.append(item_info)
                
                return results
            else:
                logger.warning(f"⚠️ Spotlight поиск неудачен: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Ошибка Spotlight поиска: {e}")
            return []
    
    def _get_item_info(self, path: str) -> Optional[Dict[str, Any]]:
        """Получение информации об элементе"""
        try:
            path_obj = Path(path)
            
            if not path_obj.exists():
                return None
            
            # Определение типа элемента
            item_type = "file"
            if path_obj.is_dir():
                if path.endswith('.app'):
                    item_type = "application"
                else:
                    item_type = "folder"
            
            return {
                "path": path,
                "name": path_obj.name,
                "type": item_type,
                "parent": str(path_obj.parent),
                "extension": path_obj.suffix if path_obj.is_file() else None
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Не удалось получить информацию о {path}: {e}")
            return None
    
    def find_applications(self, query: str) -> List[Dict[str, Any]]:
        """Поиск приложений через Spotlight"""
        try:
            # Поиск приложений по bundle identifier и имени
            cmd = ['mdfind', 'kMDItemContentType == "com.apple.application-bundle"']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                all_apps = result.stdout.strip().split('\n')
                matching_apps = []
                
                for app_path in all_apps:
                    if app_path and query.lower() in Path(app_path).name.lower():
                        app_info = self._get_app_info(app_path)
                        if app_info:
                            matching_apps.append(app_info)
                
                return matching_apps
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска приложений: {e}")
        
        return []
    
    def _get_app_info(self, app_path: str) -> Optional[Dict[str, Any]]:
        """Получение информации о приложении"""
        try:
            path_obj = Path(app_path)
            app_name = path_obj.stem
            
            # Попытка получить bundle ID
            bundle_id = None
            try:
                plist_path = path_obj / "Contents" / "Info.plist"
                if plist_path.exists():
                    cmd = ['plutil', '-extract', 'CFBundleIdentifier', 'raw', str(plist_path)]
                    result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        bundle_id = result.stdout.strip()
            except:
                pass
            
            return {
                "name": app_name,
                "path": app_path,
                "bundle_id": bundle_id,
                "type": "application"
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Не удалось получить информацию о приложении {app_path}: {e}")
            return None
    
    def generate_spotlight_search_dsl(self, query: str, action: str = "open") -> str:
        """Генерация DSL для Spotlight поиска"""
        # Проверяем, есть ли в кэше более точный запрос
        normalized_query = query.lower().strip()
        if normalized_query in self.common_searches:
            actual_query = self.common_searches[normalized_query]
        else:
            actual_query = query
        
        if action == "open":
            return f"""# Spotlight поиск и открытие: {query}
key cmd+space
wait 0.5s
type "{actual_query}"
wait 1s
press enter
wait 2s"""
        
        elif action == "search_only":
            return f"""# Spotlight поиск: {query}
key cmd+space
wait 0.5s
type "{actual_query}"
wait 1s"""
        
        else:
            return f"""# Spotlight поиск с действием {action}: {query}
key cmd+space
wait 0.5s
type "{actual_query}"
wait 1s
press enter
wait 2s"""
    
    def generate_app_launch_dsl(self, app_name: str) -> str:
        """Генерация DSL для запуска приложения через Spotlight"""
        return f"""# Запуск {app_name} через Spotlight
key cmd+space
wait 0.5s
type "{app_name}"
wait 1s
press enter
wait 2s"""
    
    def generate_file_search_dsl(self, filename: str, open_file: bool = True) -> str:
        """Генерация DSL для поиска файла"""
        action_comment = "и открытие" if open_file else ""
        
        dsl = f"""# Поиск файла {action_comment}: {filename}
key cmd+space
wait 0.5s
type "{filename}"
wait 1s"""
        
        if open_file:
            dsl += "\npress enter\nwait 2s"
        
        return dsl
    
    def generate_system_search_dsl(self, search_term: str) -> str:
        """Генерация DSL для системного поиска"""
        return f"""# Системный поиск: {search_term}
key cmd+space
wait 0.5s
type "{search_term}"
wait 1s
# Используем стрелки для навигации по результатам
key down
wait 0.3s
press enter
wait 2s"""
    
    def suggest_search_terms(self, partial_query: str) -> List[str]:
        """Предложение вариантов поиска"""
        suggestions = []
        partial_lower = partial_query.lower()
        
        # Поиск в общих запросах
        for key, value in self.common_searches.items():
            if partial_lower in key or partial_lower in value.lower():
                suggestions.append(key)
        
        # Ограничиваем количество предложений
        return suggestions[:10]
    
    def is_spotlight_available(self) -> bool:
        """Проверка доступности Spotlight"""
        try:
            result = subprocess.run(['mdfind', '--help'], 
                                  capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def get_spotlight_statistics(self) -> Dict[str, Any]:
        """Получение статистики Spotlight"""
        try:
            # Получение общего количества индексированных элементов
            result = subprocess.run(['mdfind', '-count', '*'], 
                                  capture_output=True, text=True, timeout=10)
            
            total_items = 0
            if result.returncode == 0:
                try:
                    total_items = int(result.stdout.strip())
                except:
                    pass
            
            return {
                "available": self.is_spotlight_available(),
                "total_indexed_items": total_items,
                "common_searches_count": len(self.common_searches),
                "cache_size": len(self.search_cache)
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статистики Spotlight: {e}")
            return {
                "available": False,
                "error": str(e)
            }
    
    def clear_cache(self):
        """Очистка кэша поиска"""
        self.search_cache.clear()
        logger.info("🗑️ Кэш Spotlight очищен")
    
    def add_common_search(self, query: str, target: str):
        """Добавление часто используемого поиска"""
        self.common_searches[query.lower()] = target
        logger.info(f"➕ Добавлен поиск: '{query}' -> '{target}'")
    
    def get_search_history(self) -> List[str]:
        """Получение истории поиска"""
        return list(self.search_cache.keys())
    
    def generate_advanced_search_dsl(self, query: str, filters: Dict[str, Any] = None) -> str:
        """Генерация расширенного поиска с фильтрами"""
        if not filters:
            return self.generate_spotlight_search_dsl(query)
        
        # Построение сложного запроса
        search_query = query
        
        if filters.get('file_type'):
            search_query += f" kind:{filters['file_type']}"
        
        if filters.get('date_range'):
            search_query += f" date:{filters['date_range']}"
        
        if filters.get('size'):
            search_query += f" size:{filters['size']}"
        
        return f"""# Расширенный Spotlight поиск: {query}
# Фильтры: {filters}
key cmd+space
wait 0.5s
type "{search_query}"
wait 2s
press enter
wait 2s"""
