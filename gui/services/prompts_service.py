"""
Prompts Service - Сервис для работы с AI промптами
Интеграция с существующим функционалом из src/main.py
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
import sys

class PromptsService:
    """Сервис для работы с AI промптами - интеграция с консольным функционалом"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_dir = project_root / "src"
        
        # Добавляем путь для импорта
        sys.path.insert(0, str(project_root))
        
    def get_available_actions(self) -> List[Dict[str, Any]]:
        """
        Получение доступных действий с промптами (из консольного меню)
        
        Returns:
            List с действиями
        """
        return [
            {
                'id': 'update_all',
                'title': '🔄 Обновить все промпты',
                'description': 'Сканирует templates/ и обновляет все промпты через AI',
                'details': [
                    'Сканирует templates/ и находит все PNG файлы',
                    'AI обновляет TEMPLATES_STRUCTURE.txt',
                    'AI обновляет BEST_PRACTICES.txt', 
                    'Регенерирует DSL_REFERENCE.txt'
                ],
                'warning': 'Это займёт 10-20 секунд',
                'action': 'update_prompts'
            },
            {
                'id': 'add_platform',
                'title': '➕ Добавить новую платформу',
                'description': 'AI создаст структуру шаблонов для новой платформы',
                'details': [
                    'Запрашивает название платформы',
                    'AI создает структуру папок',
                    'Генерирует STRUCTURE.txt файл',
                    'Обновляет общую документацию'
                ],
                'action': 'add_platform'
            },
            {
                'id': 'show_structure',
                'title': '📊 Показать структуру шаблонов',
                'description': 'Отображает текущую структуру templates/',
                'details': [
                    'Сканирует папку templates/',
                    'Показывает все платформы',
                    'Количество шаблонов по категориям',
                    'Статистика файлов'
                ],
                'action': 'show_structure'
            },
            {
                'id': 'open_docs',
                'title': '📚 Открыть документацию',
                'description': 'Открывает документацию по промптам',
                'details': [
                    'AI_PROMPTS_FULL.md - все промпты',
                    'PROMPT_UPDATER_GUIDE.md - руководство',
                    'AI_OPTIMIZATION_SUMMARY.md - оптимизация'
                ],
                'action': 'open_docs'
            }
        ]
    
    def update_all_prompts_async(self, callback=None) -> Dict[str, Any]:
        """
        Асинхронное обновление всех промптов через существующий скрипт
        
        Args:
            callback: Функция обратного вызова для прогресса
            
        Returns:
            Dict с результатом операции
        """
        try:
            if callback:
                callback("🔄 Запуск обновления промптов...")
            
            # Используем существующий prompt_updater.py
            script_path = self.project_root / "src" / "ai" / "prompt_updater.py"
            
            if not script_path.exists():
                return {
                    'success': False,
                    'error': 'prompt_updater.py не найден',
                    'message': 'Скрипт обновления промптов отсутствует'
                }
            
            if callback:
                callback("🤖 AI обновляет промпты...")
            
            # Запускаем обновление
            if callback:
                callback("🔄 Запуск: python3 prompt_updater.py --update")
                callback("=" * 80)
            
            result = subprocess.run([
                'python3', str(script_path), '--update'
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                # Ищем созданные файлы в выводе
                files_created = []
                if result.stdout:
                    # Ищем строки с путями к файлам
                    import re
                    file_patterns = [
                        r'templates/[^/]+_STRUCTURE\.txt',
                        r'dsl_references/[^/]+\.txt',
                        r'docs/[^/]+\.md'
                    ]
                    for pattern in file_patterns:
                        matches = re.findall(pattern, result.stdout)
                        files_created.extend(matches)
                
                return {
                    'success': True,
                    'output': result.stdout,
                    'files_created': files_created,
                    'message': f'Промпты успешно обновлены! Создано файлов: {len(files_created)}'
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'output': result.stdout,
                    'message': f'Ошибка обновления: {result.stderr}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Ошибка выполнения: {e}'
            }
    
    def add_new_platform_async(self, platform_name: str, description: str, callback=None) -> Dict[str, Any]:
        """
        Асинхронное добавление новой платформы
        
        Args:
            platform_name: Название платформы
            description: Описание действий
            callback: Функция обратного вызова
            
        Returns:
            Dict с результатом операции
        """
        try:
            if callback:
                callback(f"🤖 Создаю структуру для {platform_name}...")
            
            # Используем существующий prompt_updater.py
            script_path = self.project_root / "src" / "ai" / "prompt_updater.py"
            
            if not script_path.exists():
                return {
                    'success': False,
                    'error': 'prompt_updater.py не найден'
                }
            
            # Запускаем добавление платформы
            result = subprocess.run([
                'python3', str(script_path), 
                '--add-platform', platform_name,
                '--description', description
            ], capture_output=True, text=True, cwd=self.project_root)
            
            if result.returncode == 0:
                # Ищем созданные файлы
                files_created = []
                if result.stdout:
                    import re
                    # Ищем файл структуры платформы
                    structure_match = re.search(rf'templates/{re.escape(platform_name)}_STRUCTURE\.txt', result.stdout)
                    if structure_match:
                        files_created.append(structure_match.group())
                
                return {
                    'success': True,
                    'output': result.stdout,
                    'files_created': files_created,
                    'message': f'Платформа {platform_name} успешно добавлена! Создан файл: templates/{platform_name}_STRUCTURE.txt'
                }
            else:
                return {
                    'success': False,
                    'error': result.stderr,
                    'message': f'Ошибка добавления платформы: {result.stderr}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Ошибка: {e}'
            }
    
    def get_templates_structure(self) -> Dict[str, Any]:
        """Получение структуры шаблонов"""
        
        try:
            templates_dir = self.project_root / "templates"
            
            if not templates_dir.exists():
                return {
                    'success': False,
                    'message': 'Папка templates/ не найдена'
                }
            
            structure = {}
            total_files = 0
            
            # Сканируем структуру
            for platform_dir in templates_dir.iterdir():
                if platform_dir.is_dir() and not platform_dir.name.startswith('.'):
                    png_files = list(platform_dir.rglob("*.png"))
                    structure[platform_dir.name] = {
                        'path': str(platform_dir.relative_to(self.project_root)),
                        'files_count': len(png_files),
                        'files': [f.name for f in png_files[:10]]  # Показываем первые 10
                    }
                    total_files += len(png_files)
            
            return {
                'success': True,
                'structure': structure,
                'total_platforms': len(structure),
                'total_files': total_files,
                'message': f'Найдено {len(structure)} платформ, {total_files} файлов'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Ошибка сканирования: {e}'
            }
    
    def open_documentation(self) -> List[Dict[str, str]]:
        """Получение списка документации по промптам"""
        
        docs = []
        docs_dir = self.project_root / "docs"
        
        # Основные файлы документации
        doc_files = [
            {
                'name': 'AI_PROMPTS_FULL.md',
                'path': 'docs/project-overview/AI_PROMPTS_FULL.md',
                'title': '📋 Все AI промпты системы',
                'description': 'Полная коллекция промптов на 2-3k символов'
            },
            {
                'name': 'PROMPT_UPDATER_GUIDE.md', 
                'path': 'docs/PROMPT_UPDATER_GUIDE.md',
                'title': '📖 Руководство по обновлению промптов',
                'description': 'Подробное руководство по работе с промптами'
            },
            {
                'name': 'AI_OPTIMIZATION_SUMMARY.md',
                'path': 'docs/AI_OPTIMIZATION_SUMMARY.md', 
                'title': '⚡ Оптимизация AI',
                'description': 'Методы оптимизации AI генерации'
            },
            {
                'name': 'AI_PROMPT_OPTIMIZATION.md',
                'path': 'docs/AI_PROMPT_OPTIMIZATION.md',
                'title': '🎯 Детальная оптимизация промптов',
                'description': 'Глубокое объяснение оптимизации'
            }
        ]
        
        # Проверяем существование файлов
        for doc in doc_files:
            file_path = self.project_root / doc['path']
            doc['exists'] = file_path.exists()
            doc['full_path'] = str(file_path)
            docs.append(doc)
        
        return docs
    
    def open_file_in_system(self, file_path: str) -> bool:
        """Открытие файла в системном редакторе"""
        
        try:
            subprocess.run(['open', file_path])
            return True
        except Exception as e:
            print(f"⚠️ Ошибка открытия файла: {e}")
            return False
    
    def copy_to_clipboard(self, text: str) -> bool:
        """Копирование текста в буфер обмена"""
        
        try:
            process = subprocess.run(['pbcopy'], input=text, text=True)
            return process.returncode == 0
        except Exception as e:
            print(f"⚠️ Ошибка копирования: {e}")
            return False
