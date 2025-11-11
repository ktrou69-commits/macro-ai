"""
Architecture Service - Сервис для работы с архитектурой шаблонов
Интеграция с существующим функционалом из src/main.py (automation_template_architecture)
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import sys
import os

class ArchitectureService:
    """Сервис для работы с архитектурой шаблонов"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.templates_dir = project_root / "templates"
        self.structure_file = self.templates_dir / "TEMPLATES_STRUCTURE.txt"
        
        # Добавляем путь к src для импорта
        sys.path.insert(0, str(project_root))
        
        # Проверяем доступность AI
        try:
            from src.utils.api_config import api_config
            self.gemini_key = api_config.gemini_key
            self.ai_available = bool(self.gemini_key)
        except ImportError as e:
            print(f"⚠️ AI недоступен: {e}")
            self.ai_available = False
    
    def is_ai_available(self) -> bool:
        """Проверка доступности AI"""
        return self.ai_available
    
    def get_current_structure(self) -> Dict[str, Any]:
        """
        Получение текущей структуры шаблонов
        
        Returns:
            Dict с информацией о структуре
        """
        try:
            # Сканируем папку templates/
            structure = {}
            total_files = 0
            
            if not self.templates_dir.exists():
                return {
                    'success': False,
                    'error': 'Папка templates/ не найдена',
                    'structure': {},
                    'total_files': 0,
                    'total_folders': 0
                }
            
            for png_file in sorted(self.templates_dir.rglob("*.png")):
                rel_path = png_file.relative_to(self.templates_dir)
                folder = str(rel_path.parent)
                
                if folder not in structure:
                    structure[folder] = {
                        'files': [],
                        'count': 0,
                        'path': folder
                    }
                
                structure[folder]['files'].append({
                    'name': png_file.name,
                    'short_name': png_file.name.replace('-btn.png', '').replace('.png', ''),
                    'full_path': str(png_file),
                    'size': png_file.stat().st_size if png_file.exists() else 0
                })
                structure[folder]['count'] += 1
                total_files += 1
            
            return {
                'success': True,
                'structure': structure,
                'total_files': total_files,
                'total_folders': len(structure),
                'structure_file_exists': self.structure_file.exists(),
                'structure_file_path': str(self.structure_file)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'structure': {},
                'total_files': 0,
                'total_folders': 0
            }
    
    def get_structure_file_content(self) -> str:
        """Получение содержимого файла TEMPLATES_STRUCTURE.txt"""
        
        if not self.structure_file.exists():
            return "Файл TEMPLATES_STRUCTURE.txt не найден"
        
        try:
            with open(self.structure_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Ошибка чтения файла: {e}"
    
    def generate_architecture_async(self, description: str, callback=None) -> Dict[str, Any]:
        """
        Асинхронная генерация архитектуры шаблонов через AI
        
        Args:
            description: Описание действий пользователя
            callback: Функция для обновления прогресса
            
        Returns:
            Dict с результатом операции
        """
        if not self.ai_available:
            return {
                'success': False,
                'error': 'AI недоступен',
                'message': 'Установите необходимые библиотеки и настройте GEMINI_API_KEY'
            }
        
        try:
            if callback:
                callback("🔄 Чтение текущей структуры...")
            
            # Читаем текущую структуру
            current_structure = ""
            if self.structure_file.exists():
                with open(self.structure_file, 'r', encoding='utf-8') as f:
                    current_structure = f.read()
            
            if callback:
                callback("🤖 Генерация новой архитектуры через AI...")
            
            # Создаем промпт для AI
            system_prompt = f"""Ты — эксперт по созданию архитектуры UI-шаблонов для автоматизации.

У нас есть текущая структура шаблонов:

{current_structure}

Твоя задача — создать НОВУЮ ВЕТКУ в этой структуре на основе описания пользователя.

ПРАВИЛА:
1. Используй формат как в примере выше (с отступами и комментариями)
2. Названия файлов: AppName-ElementName-btn.png
3. Комментарии должны быть понятными и описывать назначение элемента
4. Если это новое приложение — создай новую папку
5. Если это вкладка внутри приложения (например Chrome) — добавь подпапку
6. Используй пробелы для отступов (не символы дерева)

ФОРМАТ ОТВЕТА:
Выведи ТОЛЬКО новую ветку структуры, без объяснений.

Пример:
  Settings/                            # Настройки системы
    Settings-WiFi-btn.png              # Кнопка Wi-Fi
    Settings-Network-btn.png           # Кнопка "Сеть"
    Settings-NetworkName-btn.png       # Название сети

INPUT: {description}
"""
            
            # Генерируем через Gemini
            from google import genai
            from src.utils.api_config import api_config
            
            client = genai.Client(api_key=self.gemini_key)
            
            response = client.models.generate_content(
                model=api_config.gemini_model,
                contents=system_prompt
            )
            
            result = response.text.strip()
            
            return {
                'success': True,
                'architecture': result,
                'message': 'Новая архитектура успешно сгенерирована!',
                'description': description
            }
            
        except ImportError:
            return {
                'success': False,
                'error': 'Библиотека google-genai не установлена',
                'message': 'Установите: pip install google-genai'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Ошибка генерации: {e}'
            }
    
    def save_architecture_to_file(self, architecture: str) -> Dict[str, Any]:
        """
        Сохранение архитектуры в файл TEMPLATES_STRUCTURE.txt
        
        Args:
            architecture: Сгенерированная архитектура
            
        Returns:
            Dict с результатом операции
        """
        try:
            # Создаем папку если не существует
            self.structure_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Добавляем в файл
            with open(self.structure_file, 'a', encoding='utf-8') as f:
                f.write("\n")
                f.write(architecture)
                f.write("\n")
            
            return {
                'success': True,
                'message': 'Архитектура добавлена в файл!',
                'file_path': str(self.structure_file)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Ошибка сохранения: {e}'
            }
    
    def update_full_structure(self, callback=None) -> Dict[str, Any]:
        """
        Обновление полной структуры шаблонов через AI
        
        Args:
            callback: Функция для обновления прогресса
            
        Returns:
            Dict с результатом операции
        """
        if not self.ai_available:
            return {
                'success': False,
                'error': 'AI недоступен'
            }
        
        try:
            if callback:
                callback("🔄 Сканирование папки templates/...")
            
            # Сканируем текущие файлы
            structure_info = self.get_current_structure()
            
            if not structure_info['success']:
                return structure_info
            
            # Генерируем описание структуры
            structure_description = self._generate_structure_description(structure_info['structure'])
            
            if callback:
                callback("🤖 AI обновляет полную структуру...")
            
            # Просим AI обновить структуру
            updated_structure = self._ask_ai_to_update_structure(structure_description)
            
            if not updated_structure:
                return {
                    'success': False,
                    'error': 'AI не смог обновить структуру'
                }
            
            # Сохраняем новую структуру
            with open(self.structure_file, 'w', encoding='utf-8') as f:
                f.write(updated_structure)
            
            return {
                'success': True,
                'message': 'Структура шаблонов полностью обновлена!',
                'file_path': str(self.structure_file),
                'structure': updated_structure
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _generate_structure_description(self, structure: Dict[str, Any]) -> str:
        """Генерирует описание структуры для AI"""
        
        lines = []
        lines.append("📂 ТЕКУЩАЯ СТРУКТУРА ШАБЛОНОВ:")
        lines.append("")
        
        for folder, info in sorted(structure.items()):
            lines.append(f"📁 {folder}/ ({info['count']} файлов)")
            for file_info in sorted(info['files'], key=lambda x: x['name']):
                lines.append(f"   • {file_info['short_name']} ({file_info['name']})")
            lines.append("")
        
        return "\n".join(lines)
    
    def _ask_ai_to_update_structure(self, current_structure: str) -> Optional[str]:
        """Просит AI обновить TEMPLATES_STRUCTURE.txt"""
        
        try:
            from google import genai
            from src.utils.api_config import api_config
            
            client = genai.Client(api_key=self.gemini_key)
            
            prompt = f"""Ты — эксперт по документированию структуры шаблонов для автоматизации.

Твоя задача: создать красивый и понятный файл TEMPLATES_STRUCTURE.txt на основе текущих файлов.

{current_structure}

ТРЕБОВАНИЯ:

1. Формат файла:
================================================================================
ПОЛНАЯ СТРУКТУРА ШАБЛОНОВ - Описание всех кнопок и элементов
================================================================================

📂 templates/
│
├── Chrome/                              # Браузер Google Chrome
│   │
│   ├── ChromeBasicGuiButtons/           # Базовые кнопки Chrome
│   │   ├── ChromeApp-btn.png            # Иконка запуска Chrome
│   │   ├── ChromeNewTab-btn.png         # Кнопка "плюс" — открыть новую вкладку
│   │   └── ...
│   │
│   ├── TikTok/                          # Вкладка TikTok
│   │   ├── Chrome-TikTok-Like-btn.png   # Кнопка лайка видео
│   │   └── ...
│   │
│   └── YouTube/                         # Вкладка YouTube
│       └── ...

2. Краткие имена для DSL:
================================================================================
КРАТКИЕ ИМЕНА ШАБЛОНОВ (для использования в DSL)
================================================================================

Chrome - Базовые:
  • ChromeApp                - Запуск Chrome
  • ChromeNewTab             - Новая вкладка
  ...

3. Типичные сценарии:
================================================================================
ТИПИЧНЫЕ СЦЕНАРИИ ИСПОЛЬЗОВАНИЯ
================================================================================

1. Открыть Chrome и перейти на сайт:
   open ChromeApp
   wait 2s
   click ChromeSearchField
   ...

ВАЖНО:
- Добавь понятные комментарии для каждого файла
- Группируй по платформам (Chrome, TikTok, YouTube, ...)
- Используй эмодзи для красоты
- Добавь примеры использования

Верни ТОЛЬКО содержимое файла, без дополнительных объяснений!
"""
            
            response = client.models.generate_content(
                model=api_config.gemini_model,
                contents=prompt
            )
            
            return response.text
            
        except Exception as e:
            print(f"❌ Ошибка AI: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получение статистики по шаблонам"""
        
        structure_info = self.get_current_structure()
        
        if not structure_info['success']:
            return {
                'total_files': 0,
                'total_folders': 0,
                'platforms': [],
                'structure_file_exists': False
            }
        
        # Определяем платформы
        platforms = []
        for folder in structure_info['structure'].keys():
            if 'Chrome' in folder:
                platforms.append('Chrome')
            if 'TikTok' in folder:
                platforms.append('TikTok')
            if 'YouTube' in folder:
                platforms.append('YouTube')
            if 'Instagram' in folder:
                platforms.append('Instagram')
        
        platforms = list(set(platforms))  # Убираем дубликаты
        
        return {
            'total_files': structure_info['total_files'],
            'total_folders': structure_info['total_folders'],
            'platforms': platforms,
            'structure_file_exists': structure_info['structure_file_exists'],
            'structure_file_path': structure_info.get('structure_file_path', '')
        }
