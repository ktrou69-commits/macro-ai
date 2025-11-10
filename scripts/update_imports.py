#!/usr/bin/env python3
"""
update_imports.py
Автоматически обновляет все импорты после реструктуризации в src/
"""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent

# Маппинг старых путей на новые
IMPORT_MAPPINGS = {
    # Корневые модули → src/core/
    r'\bimport macro_sequence\b': 'from src.core from src.core import macro_sequence',
    r'\bfrom macro_sequence import\b': 'from src.core.macro_sequence import',
    r'\bimport atlas_dsl_parser\b': 'from src.core from src.core import atlas_dsl_parser',
    r'\bfrom atlas_dsl_parser import\b': 'from src.core.atlas_dsl_parser import',
    r'\bimport sequence_builder\b': 'from src.core from src.core import sequence_builder',
    r'\bfrom sequence_builder import\b': 'from src.core.sequence_builder import',
    
    # Движки → src/engines/
    r'\bimport parallel_runner\b': 'from src.engines from src.engines import parallel_runner',
    r'\bfrom parallel_runner import\b': 'from src.engines.parallel_runner import',
    r'\bimport selenium_helper\b': 'from src.engines from src.engines import selenium_helper',
    r'\bfrom selenium_helper import\b': 'from src.engines.selenium_helper import',
    
    # utils → src/utils/ или src/ai/
    r'\bfrom utils\.api_config import\b': 'from src.utils.api_config import',
    r'\bfrom utils\.smart_capture import\b': 'from src.utils.smart_capture import',
    r'\bfrom utils\.coordinate_finder import\b': 'from src.utils.coordinate_finder import',
    r'\bfrom utils\.advanced_coordinate_finder import\b': 'from src.utils.advanced_coordinate_finder import',
    r'\bfrom utils\.find_comment_region import\b': 'from src.utils.find_comment_region import',
    r'\bfrom utils\.simple_coordinate_finder import\b': 'from src.utils.simple_coordinate_finder import',
    r'\bfrom utils\.check_api_quota import\b': 'from src.utils.check_api_quota import',
    r'\bfrom utils\.dom_selector_tool import\b': 'from src.utils.dom_selector_tool import',
    
    # AI модули
    r'\bfrom utils\.ai_macro_generator import\b': 'from src.ai.macro_generator import',
    r'\bfrom utils\.ai_macro_generator_legacy import\b': 'from src.ai.macro_generator_legacy import',
    r'\bfrom utils\.prompt_updater import\b': 'from src.ai.prompt_updater import',
    r'\bfrom utils\.ai_dom_analyzer import\b': 'from src.ai.dom_analyzer import',
    r'\bfrom utils\.dom_selector_extractor import\b': 'from src.utils.dom_selector_extractor import',
}

# Path(__file__) обновления
PATH_FILE_MAPPINGS = {
    # Для файлов в src/ нужно добавить .parent
    'src/utils/api_config.py': {
        r'Path\(__file__\)\.parent\.parent': 'Path(__file__).parent.parent.parent',
    },
    'src/ai/macro_generator.py': {
        r'Path\(__file__\)\.parent\.parent': 'Path(__file__).parent.parent.parent',
    },
    'src/ai/macro_generator_legacy.py': {
        r'Path\(__file__\)\.parent\.parent': 'Path(__file__).parent.parent.parent',
    },
    'src/ai/prompt_updater.py': {
        r'Path\(__file__\)\.parent\.parent': 'Path(__file__).parent.parent.parent',
    },
    'src/ai/dom_analyzer.py': {
        r'Path\(__file__\)\.parent\.parent': 'Path(__file__).parent.parent.parent',
    },
    'src/utils/dom_selector_tool.py': {
        r'Path\(__file__\)\.parent\.parent': 'Path(__file__).parent.parent.parent',
    },
}

# sys.path.insert обновления
SYS_PATH_MAPPINGS = {
    'src/utils/api_config.py': {
        r'sys\.path\.insert\(0, str\(Path\(__file__\)\.parent\.parent\)\)': 
        'sys.path.insert(0, str(Path(__file__).parent.parent.parent))',
    },
    'src/ai/macro_generator.py': {
        r'sys\.path\.insert\(0, str\(Path\(__file__\)\.parent\.parent\)\)':
        'sys.path.insert(0, str(Path(__file__).parent.parent.parent))',
    },
    'src/ai/macro_generator_legacy.py': {
        r'sys\.path\.insert\(0, str\(Path\(__file__\)\.parent\.parent\)\)':
        'sys.path.insert(0, str(Path(__file__).parent.parent.parent))',
    },
    'src/ai/prompt_updater.py': {
        r'sys\.path\.insert\(0, str\(Path\(__file__\)\.parent\.parent\)\)':
        'sys.path.insert(0, str(Path(__file__).parent.parent.parent))',
    },
    'src/utils/check_api_quota.py': {
        r'sys\.path\.insert\(0, str\(Path\(__file__\)\.parent\.parent\)\)':
        'sys.path.insert(0, str(Path(__file__).parent.parent.parent))',
    },
    'src/utils/dom_selector_tool.py': {
        r'sys\.path\.insert\(0, str\(Path\(__file__\)\.parent\.parent\)\)':
        'sys.path.insert(0, str(Path(__file__).parent.parent.parent))',
    },
}

def update_file(file_path):
    """Обновляет импорты в файле"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        changes = []
        
        # Обновляем импорты
        for pattern, replacement in IMPORT_MAPPINGS.items():
            if re.search(pattern, content):
                content = re.sub(pattern, replacement, content)
                changes.append(f"  • {pattern} → {replacement}")
        
        # Обновляем Path(__file__) для конкретных файлов
        rel_path = str(file_path.relative_to(PROJECT_ROOT))
        if rel_path in PATH_FILE_MAPPINGS:
            for pattern, replacement in PATH_FILE_MAPPINGS[rel_path].items():
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    changes.append(f"  • Path(__file__) обновлён")
        
        # Обновляем sys.path.insert для конкретных файлов
        if rel_path in SYS_PATH_MAPPINGS:
            for pattern, replacement in SYS_PATH_MAPPINGS[rel_path].items():
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    changes.append(f"  • sys.path.insert обновлён")
        
        # Сохраняем если были изменения
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return changes
        
        return None
    
    except Exception as e:
        print(f"⚠️  Ошибка в {file_path}: {e}")
        return None

def main():
    print("="*80)
    print("🔄 ОБНОВЛЕНИЕ ИМПОРТОВ".center(80))
    print("="*80)
    print()
    
    # Файлы для обновления
    files_to_update = [
        # В src/
        *PROJECT_ROOT.glob('src/**/*.py'),
        # В tests/
        *PROJECT_ROOT.glob('tests/*.py'),
        # В scripts/
        *PROJECT_ROOT.glob('scripts/*.py'),
        # В simulator/
        *PROJECT_ROOT.glob('simulator/*.py'),
        # config.py
        PROJECT_ROOT / 'config.py',
    ]
    
    # Исключаем __init__.py и __pycache__
    files_to_update = [
        f for f in files_to_update
        if f.name != '__init__.py'
        and '__pycache__' not in str(f)
        and f.exists()
    ]
    
    print(f"📊 Найдено файлов: {len(files_to_update)}")
    print()
    
    updated_count = 0
    
    for file_path in sorted(files_to_update):
        changes = update_file(file_path)
        if changes:
            updated_count += 1
            rel_path = file_path.relative_to(PROJECT_ROOT)
            print(f"✅ {rel_path}")
            for change in changes:
                print(change)
            print()
    
    print("="*80)
    print(f"✅ Обновлено файлов: {updated_count}/{len(files_to_update)}")
    print("="*80)

if __name__ == "__main__":
    main()
