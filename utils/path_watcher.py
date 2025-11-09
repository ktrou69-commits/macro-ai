#!/usr/bin/env python3
"""
path_watcher.py
Автоматическое отслеживание перемещения файлов и обновление путей в коде

Использование:
    python3 utils/path_watcher.py

Что делает:
    - Отслеживает папку templates/
    - При перемещении файла автоматически обновляет все пути в коде
    - Работает в реальном времени
"""

import os
import re
import time
from pathlib import Path
from typing import List, Dict, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileMovedEvent


class PathUpdater:
    """Обновление путей в файлах"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.file_extensions = ['.yaml', '.yml', '.atlas', '.py', '.md', '.txt']
    
    def find_code_files(self) -> List[Path]:
        """Найти все файлы с кодом"""
        files = []
        
        for ext in self.file_extensions:
            files.extend(self.project_root.rglob(f"*{ext}"))
        
        # Исключаем служебные папки
        exclude_dirs = {'.git', '__pycache__', 'venv', 'node_modules', '.venv', 'coordinates'}
        files = [f for f in files if not any(ex in f.parts for ex in exclude_dirs)]
        
        return files
    
    def update_path_in_file(self, filepath: Path, old_path: str, new_path: str) -> int:
        """Обновить путь в файле"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Ищем все варианты старого пути
            old_variants = [
                old_path,  # Относительный
                str(self.project_root / old_path),  # Абсолютный
            ]
            
            updated_content = content
            total_replacements = 0
            
            for old_variant in old_variants:
                if old_variant in updated_content:
                    # Заменяем на относительный путь
                    updated_content = updated_content.replace(old_variant, new_path)
                    total_replacements += content.count(old_variant)
            
            if total_replacements > 0:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
            
            return total_replacements
        
        except Exception as e:
            print(f"⚠️  Ошибка при обработке {filepath}: {e}")
            return 0
    
    def update_all_files(self, old_path: str, new_path: str):
        """Обновить пути во всех файлах"""
        files = self.find_code_files()
        total_changes = 0
        changed_files = []
        
        for filepath in files:
            count = self.update_path_in_file(filepath, old_path, new_path)
            if count > 0:
                total_changes += count
                changed_files.append((filepath, count))
        
        return total_changes, changed_files


class TemplateWatcher(FileSystemEventHandler):
    """Отслеживание перемещения файлов в templates/"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.updater = PathUpdater(project_root)
        self.templates_dir = project_root / "templates"
        
        print("\n" + "="*70)
        print("👁️  PATH WATCHER - Автоматическое обновление путей")
        print("="*70)
        print(f"\n📂 Отслеживаемая папка: {self.templates_dir}")
        print("💡 Переместите любой файл - пути обновятся автоматически!")
        print("🛑 Нажмите CTRL+C для остановки")
        print("="*70 + "\n")
    
    def on_moved(self, event):
        """Обработка перемещения файла"""
        if isinstance(event, FileMovedEvent):
            # Игнорируем папки
            if event.is_directory:
                return
            
            # Игнорируем не-PNG файлы (можно расширить)
            if not event.dest_path.endswith('.png'):
                return
            
            # Получаем относительные пути
            old_path = Path(event.src_path).relative_to(self.project_root)
            new_path = Path(event.dest_path).relative_to(self.project_root)
            
            print(f"\n{'='*70}")
            print(f"🔄 ОБНАРУЖЕНО ПЕРЕМЕЩЕНИЕ")
            print(f"{'='*70}")
            print(f"📤 Старый путь: {old_path}")
            print(f"📥 Новый путь:  {new_path}")
            print(f"{'='*70}\n")
            
            print("🔍 Сканирование файлов...")
            
            # Обновляем пути
            total_changes, changed_files = self.updater.update_all_files(
                str(old_path),
                str(new_path)
            )
            
            if total_changes > 0:
                print(f"\n✅ Обновлено файлов: {len(changed_files)}")
                print(f"✅ Всего замен: {total_changes}\n")
                
                for filepath, count in changed_files:
                    rel_path = filepath.relative_to(self.project_root)
                    print(f"   📝 {rel_path}: {count} замен")
                
                print(f"\n{'='*70}")
                print("🎉 ПУТИ ОБНОВЛЕНЫ АВТОМАТИЧЕСКИ!")
                print(f"{'='*70}\n")
            else:
                print(f"\n⚠️  Ссылки на этот файл не найдены")
                print(f"{'='*70}\n")


def main():
    """Главная функция"""
    project_root = Path.cwd()
    
    # Проверяем что мы в корне проекта
    if not (project_root / "templates").exists():
        print("❌ Ошибка: Запускай из корня проекта (где находится папка templates/)")
        return
    
    # Создаем наблюдатель
    event_handler = TemplateWatcher(project_root)
    observer = Observer()
    observer.schedule(event_handler, str(project_root / "templates"), recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("🛑 PATH WATCHER ОСТАНОВЛЕН")
        print("="*70 + "\n")
        observer.stop()
    
    observer.join()


if __name__ == "__main__":
    main()
