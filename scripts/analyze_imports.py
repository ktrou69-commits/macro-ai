#!/usr/bin/env python3
"""
analyze_imports.py
Анализирует все импорты в проекте перед реструктуризацией

Находит:
- Все импорты из корневых модулей
- Все импорты из utils
- Все Path(__file__) использования
- Все sys.path.insert() использования
"""

import re
from pathlib import Path
from collections import defaultdict

# Корень проекта
PROJECT_ROOT = Path(__file__).parent.parent

# Модули которые будут перемещены
ROOT_MODULES = [
    'main',
    'macro_sequence',
    'atlas_dsl_parser',
    'sequence_builder',
    'parallel_runner',
    'selenium_helper',
]

def find_imports_in_file(file_path):
    """Находит все импорты в файле"""
    imports = {
        'root_modules': [],
        'utils_imports': [],
        'path_file': [],
        'sys_path': [],
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
            for i, line in enumerate(lines, 1):
                # Импорты корневых модулей
                for module in ROOT_MODULES:
                    if re.search(rf'\bimport {module}\b', line):
                        imports['root_modules'].append((i, line.strip()))
                    if re.search(rf'\bfrom {module} import\b', line):
                        imports['root_modules'].append((i, line.strip()))
                
                # Импорты из utils
                if re.search(r'\bfrom utils\b', line) or re.search(r'\bimport utils\b', line):
                    imports['utils_imports'].append((i, line.strip()))
                
                # Path(__file__)
                if 'Path(__file__)' in line:
                    imports['path_file'].append((i, line.strip()))
                
                # sys.path.insert
                if 'sys.path.insert' in line:
                    imports['sys_path'].append((i, line.strip()))
    
    except Exception as e:
        print(f"⚠️  Ошибка чтения {file_path}: {e}")
    
    return imports

def analyze_project():
    """Анализирует весь проект"""
    print("="*80)
    print("🔍 АНАЛИЗ ИМПОРТОВ ПРОЕКТА".center(80))
    print("="*80)
    print()
    
    # Собираем все .py файлы
    py_files = []
    for pattern in ['*.py', '**/*.py']:
        py_files.extend(PROJECT_ROOT.glob(pattern))
    
    # Исключаем venv, __pycache__, .git
    py_files = [
        f for f in py_files
        if 'venv' not in str(f)
        and '__pycache__' not in str(f)
        and '.git' not in str(f)
        and 'learning' not in str(f)
    ]
    
    print(f"📊 Найдено файлов: {len(py_files)}")
    print()
    
    # Анализируем каждый файл
    results = defaultdict(lambda: defaultdict(list))
    
    for file_path in py_files:
        imports = find_imports_in_file(file_path)
        rel_path = file_path.relative_to(PROJECT_ROOT)
        
        if imports['root_modules']:
            results['root_modules'][str(rel_path)] = imports['root_modules']
        if imports['utils_imports']:
            results['utils_imports'][str(rel_path)] = imports['utils_imports']
        if imports['path_file']:
            results['path_file'][str(rel_path)] = imports['path_file']
        if imports['sys_path']:
            results['sys_path'][str(rel_path)] = imports['sys_path']
    
    # Выводим результаты
    print("="*80)
    print("📦 ИМПОРТЫ КОРНЕВЫХ МОДУЛЕЙ".center(80))
    print("="*80)
    print()
    
    if results['root_modules']:
        for file_path, imports in sorted(results['root_modules'].items()):
            print(f"📄 {file_path}")
            for line_num, line in imports:
                print(f"   L{line_num}: {line}")
            print()
    else:
        print("✅ Не найдено")
        print()
    
    print("="*80)
    print("🔧 ИМПОРТЫ ИЗ UTILS".center(80))
    print("="*80)
    print()
    
    if results['utils_imports']:
        for file_path, imports in sorted(results['utils_imports'].items()):
            print(f"📄 {file_path}")
            for line_num, line in imports:
                print(f"   L{line_num}: {line}")
            print()
    else:
        print("✅ Не найдено")
        print()
    
    print("="*80)
    print("📁 ИСПОЛЬЗОВАНИЕ Path(__file__)".center(80))
    print("="*80)
    print()
    
    if results['path_file']:
        for file_path, usages in sorted(results['path_file'].items()):
            print(f"📄 {file_path}")
            for line_num, line in usages:
                print(f"   L{line_num}: {line}")
            print()
    else:
        print("✅ Не найдено")
        print()
    
    print("="*80)
    print("🛤️  ИСПОЛЬЗОВАНИЕ sys.path.insert".center(80))
    print("="*80)
    print()
    
    if results['sys_path']:
        for file_path, usages in sorted(results['sys_path'].items()):
            print(f"📄 {file_path}")
            for line_num, line in usages:
                print(f"   L{line_num}: {line}")
            print()
    else:
        print("✅ Не найдено")
        print()
    
    # Статистика
    print("="*80)
    print("📊 СТАТИСТИКА".center(80))
    print("="*80)
    print()
    print(f"Файлов с импортами корневых модулей: {len(results['root_modules'])}")
    print(f"Файлов с импортами из utils:         {len(results['utils_imports'])}")
    print(f"Файлов с Path(__file__):             {len(results['path_file'])}")
    print(f"Файлов с sys.path.insert:            {len(results['sys_path'])}")
    print()
    
    # Список файлов для обновления
    files_to_update = set()
    for category in results.values():
        files_to_update.update(category.keys())
    
    print("="*80)
    print("📝 ФАЙЛЫ ДЛЯ ОБНОВЛЕНИЯ".center(80))
    print("="*80)
    print()
    print(f"Всего файлов: {len(files_to_update)}")
    print()
    for file_path in sorted(files_to_update):
        print(f"  • {file_path}")
    print()
    
    # Сохраняем результаты
    output_file = PROJECT_ROOT / "IMPORT_ANALYSIS_REPORT.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*80 + "\n")
        f.write("АНАЛИЗ ИМПОРТОВ ПРОЕКТА\n")
        f.write("="*80 + "\n\n")
        
        f.write("ФАЙЛЫ ДЛЯ ОБНОВЛЕНИЯ:\n\n")
        for file_path in sorted(files_to_update):
            f.write(f"  • {file_path}\n")
        f.write("\n")
        
        f.write("="*80 + "\n")
        f.write("ИМПОРТЫ КОРНЕВЫХ МОДУЛЕЙ:\n")
        f.write("="*80 + "\n\n")
        for file_path, imports in sorted(results['root_modules'].items()):
            f.write(f"📄 {file_path}\n")
            for line_num, line in imports:
                f.write(f"   L{line_num}: {line}\n")
            f.write("\n")
        
        f.write("="*80 + "\n")
        f.write("ИМПОРТЫ ИЗ UTILS:\n")
        f.write("="*80 + "\n\n")
        for file_path, imports in sorted(results['utils_imports'].items()):
            f.write(f"📄 {file_path}\n")
            for line_num, line in imports:
                f.write(f"   L{line_num}: {line}\n")
            f.write("\n")
        
        f.write("="*80 + "\n")
        f.write("Path(__file__):\n")
        f.write("="*80 + "\n\n")
        for file_path, usages in sorted(results['path_file'].items()):
            f.write(f"📄 {file_path}\n")
            for line_num, line in usages:
                f.write(f"   L{line_num}: {line}\n")
            f.write("\n")
        
        f.write("="*80 + "\n")
        f.write("sys.path.insert:\n")
        f.write("="*80 + "\n\n")
        for file_path, usages in sorted(results['sys_path'].items()):
            f.write(f"📄 {file_path}\n")
            for line_num, line in usages:
                f.write(f"   L{line_num}: {line}\n")
            f.write("\n")
    
    print(f"💾 Результаты сохранены: {output_file}")
    print()
    print("="*80)
    print("✅ АНАЛИЗ ЗАВЕРШЁН".center(80))
    print("="*80)

if __name__ == "__main__":
    analyze_project()
