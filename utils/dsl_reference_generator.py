#!/usr/bin/env python3
"""
dsl_reference_generator.py
Генератор справочника DSL команд и доступных шаблонов

Использование:
    python3 utils/dsl_reference_generator.py
    python3 utils/dsl_reference_generator.py --templates-path templates/Chrome/TikTok
    python3 utils/dsl_reference_generator.py --output my_reference.txt
"""

import argparse
from pathlib import Path
from typing import Dict, List, Set


class DSLReferenceGenerator:
    """Генератор справочника DSL"""
    
    def __init__(self, templates_path: str = "templates"):
        self.templates_path = Path(templates_path)
        self.template_names = set()
    
    def scan_templates(self) -> Dict[str, List[str]]:
        """
        Сканирует папку с шаблонами и извлекает все имена
        
        Returns:
            Dict с группировкой имен по файлам
        """
        if not self.templates_path.exists():
            print(f"❌ Папка не найдена: {self.templates_path}")
            return {}
        
        templates_map = {}
        
        # 1. Находим все .png файлы (Vision)
        png_files = list(self.templates_path.rglob("*.png"))
        
        if not png_files:
            print(f"⚠️  PNG файлы не найдены в: {self.templates_path}")
        else:
            print(f"📂 Сканирование: {self.templates_path}")
            print(f"📄 Найдено PNG файлов (Vision): {len(png_files)}")
        
        for png_file in sorted(png_files):
            # Полный путь относительно базовой папки
            try:
                relative_path = png_file.relative_to(Path.cwd())
            except ValueError:
                # Если не получается относительный путь, используем абсолютный
                relative_path = png_file
            
            # Извлекаем все возможные имена
            names = self._extract_names(png_file)
            
            # Сохраняем
            templates_map[str(relative_path)] = names
            self.template_names.update(names)
        
        # 2. Парсим DOM селекторы из structure.txt
        dom_selectors = self._scan_dom_selectors()
        if dom_selectors:
            print(f"📄 Найдено DOM селекторов: {len(dom_selectors)}\n")
            templates_map.update(dom_selectors)
        else:
            print()
        
        return templates_map
    
    def _extract_names(self, png_file: Path) -> List[str]:
        """
        Извлекает все возможные имена для файла
        (как в atlas_dsl_parser.py)
        """
        names = []
        
        # Короткое имя (без расширения)
        short_name = png_file.stem
        names.append(short_name)
        
        # Убираем префиксы
        clean_name = short_name
        for prefix in ["Chrome-TikTok-", "Chrome-YouTube-", "Chrome-", "Atlas-", "TikTok-"]:
            if clean_name.startswith(prefix):
                clean_name = clean_name[len(prefix):]
                names.append(clean_name)
                break
        
        # Убираем суффиксы
        if "-btn" in clean_name or "_btn" in clean_name:
            no_btn = clean_name.replace("-btn", "").replace("_btn", "")
            if no_btn not in names:
                names.append(no_btn)
        
        # С заменой дефисов на подчеркивания
        for name in list(names):
            if "-" in name:
                underscore_name = name.replace("-", "_")
                if underscore_name not in names:
                    names.append(underscore_name)
        
        return names
    
    def _scan_dom_selectors(self) -> Dict[str, List[str]]:
        """
        Парсит DOM селекторы из structure.txt файлов
        
        Returns:
            Dict с DOM селекторами и их метаданными
        """
        dom_map = {}
        
        # Находим все structure.txt файлы
        structure_files = list(self.templates_path.rglob("structure.txt"))
        
        for structure_file in structure_files:
            try:
                with open(structure_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Парсим DOM селекторы
                # Формат:
                # # Chrome-TikTok-Like-dom
                # #   Selector: [data-e2e="like-icon"]
                # #   Type: span
                # #   Confidence: 95%
                
                lines = content.split('\n')
                i = 0
                while i < len(lines):
                    line = lines[i].strip()
                    
                    # Ищем строку с именем DOM селектора
                    # Формат: " │    │    # Chrome-TikTok-Like-dom"
                    if '# Chrome-' in line and line.endswith('-dom'):
                        # Извлекаем имя (убираем все до "# Chrome-")
                        hash_index = line.find('# Chrome-')
                        if hash_index != -1:
                            dom_name = line[hash_index + 2:].strip()  # Убираем "# "
                        
                        # Собираем метаданные
                        metadata = {'name': dom_name}
                        i += 1
                        
                        # Читаем следующие строки с метаданными
                        while i < len(lines):
                            meta_line = lines[i]
                            
                            # Проверяем что это комментарий с метаданными
                            if '#   ' not in meta_line:
                                break
                            
                            # Парсим метаданные (ищем в строке, не в stripped версии)
                            if 'Selector:' in meta_line:
                                metadata['selector'] = meta_line.split('Selector:', 1)[1].strip()
                            elif 'Type:' in meta_line:
                                metadata['type'] = meta_line.split('Type:', 1)[1].strip()
                            elif 'Confidence:' in meta_line:
                                metadata['confidence'] = meta_line.split('Confidence:', 1)[1].strip()
                            elif 'Description:' in meta_line:
                                metadata['description'] = meta_line.split('Description:', 1)[1].strip()
                            elif 'Method:' in meta_line:
                                metadata['method'] = meta_line.split('Method:', 1)[1].strip()
                            elif 'Fallback:' in meta_line:
                                metadata['fallback'] = meta_line.split('Fallback:', 1)[1].strip()
                            
                            i += 1
                        
                        # Формируем ключ (путь к structure.txt + имя)
                        key = f"{structure_file.parent.name}/{dom_name}"
                        
                        # Извлекаем возможные имена
                        names = [dom_name]
                        
                        # Добавляем вариант без префикса Chrome-
                        if dom_name.startswith('Chrome-'):
                            short_name = dom_name[7:]  # Убираем "Chrome-"
                            names.append(short_name)
                        
                        # Сохраняем
                        dom_map[key] = {
                            'names': names,
                            'metadata': metadata
                        }
                        self.template_names.update(names)
                        
                        continue
                    
                    i += 1
                    
            except Exception as e:
                print(f"⚠️  Ошибка парсинга {structure_file}: {e}")
                continue
        
        return dom_map
    
    def get_dsl_commands(self) -> Dict[str, str]:
        """
        Возвращает все доступные DSL команды с описанием
        """
        return {
            # Клики и взаимодействие
            "open <template>": "Запуск приложения (клик по иконке)",
            "click <template>": "Клик по кнопке/элементу",
            "click (<x>, <y>)": "Клик по абсолютным координатам",
            "double_click <template>": "Двойной клик",
            "dclick <template>": "Двойной клик (короткая форма)",
            "right_click <template>": "Правый клик (контекстное меню)",
            "rclick <template>": "Правый клик (короткая форма)",
            
            # Ввод текста
            "type \"<text>\"": "Ввод текста",
            "paste \"<text>\"": "Вставка текста из буфера",
            
            # Клавиатура
            "press <key>": "Нажатие клавиши (enter, esc, tab, space, ...)",
            "hotkey <key1>+<key2>": "Комбинация клавиш (ctrl+c, cmd+v, ...)",
            
            # Прокрутка
            "scroll <direction>": "Прокрутка (up, down, left, right)",
            "scroll <direction> <amount>": "Прокрутка на N пикселей",
            
            # Ожидание
            "wait <duration>": "Ожидание (3s, 1.5s, 500ms)",
            "sleep <duration>": "Ожидание (альтернативная форма)",
            
            # Циклы
            "repeat <N>:": "Повторить N раз (следующие строки с отступом)",
            "end": "Конец блока repeat",
            
            # Комментарии
            "# <comment>": "Комментарий (игнорируется)",
        }
    
    def generate_reference(self, output_file: str = "dsl_references/DSL_REFERENCE.txt"):
        """
        Генерирует справочник и сохраняет в файл
        """
        # Создаем папку dsl_references если её нет
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        templates_map = self.scan_templates()
        
        if not templates_map:
            print("❌ Нет шаблонов для генерации справочника")
            return
        
        # Формируем содержимое
        content = []
        
        # Заголовок
        content.append("=" * 80)
        content.append("DSL СПРАВОЧНИК - Доступные команды и шаблоны")
        content.append("=" * 80)
        content.append("")
        content.append(f"📂 Папка с шаблонами: {self.templates_path}")
        content.append(f"📄 Всего файлов: {len(templates_map)}")
        content.append(f"🏷️  Всего уникальных имен: {len(self.template_names)}")
        content.append("")
        content.append("=" * 80)
        content.append("")
        
        # Раздел 1: DSL Команды
        content.append("📖 РАЗДЕЛ 1: DSL КОМАНДЫ")
        content.append("=" * 80)
        content.append("")
        
        commands = self.get_dsl_commands()
        
        # Группируем команды
        groups = {
            "Клики и взаимодействие": [
                "open <template>",
                "click <template>",
                "click (<x>, <y>)",
                "double_click <template>",
                "dclick <template>",
                "right_click <template>",
                "rclick <template>",
            ],
            "Ввод текста": [
                "type \"<text>\"",
                "paste \"<text>\"",
            ],
            "Клавиатура": [
                "press <key>",
                "hotkey <key1>+<key2>",
            ],
            "Прокрутка": [
                "scroll <direction>",
                "scroll <direction> <amount>",
            ],
            "Ожидание": [
                "wait <duration>",
                "sleep <duration>",
            ],
            "Циклы": [
                "repeat <N>:",
                "end",
            ],
            "Комментарии": [
                "# <comment>",
            ],
        }
        
        for group_name, group_commands in groups.items():
            content.append(f"\n{group_name}:")
            content.append("-" * 80)
            for cmd in group_commands:
                if cmd in commands:
                    content.append(f"  {cmd:<40} # {commands[cmd]}")
            content.append("")
        
        # Примеры
        content.append("\n📝 ПРИМЕРЫ:")
        content.append("-" * 80)
        content.append("")
        content.append("# Простой клик")
        content.append("click ChromeSearchField")
        content.append("")
        content.append("# Ввод текста")
        content.append("type \"Hello World\"")
        content.append("")
        content.append("# Комбинация клавиш")
        content.append("hotkey cmd+v")
        content.append("")
        content.append("# Цикл")
        content.append("repeat 5:")
        content.append("  click LikeButton")
        content.append("  wait 1s")
        content.append("")
        content.append("# Прокрутка")
        content.append("scroll down")
        content.append("scroll down 500")
        content.append("")
        
        # Раздел 2: Доступные шаблоны
        content.append("\n" + "=" * 80)
        content.append("📋 РАЗДЕЛ 2: ДОСТУПНЫЕ ШАБЛОНЫ И СЕЛЕКТОРЫ")
        content.append("=" * 80)
        content.append("")
        
        # Разделяем Vision и DOM
        vision_templates = {}
        dom_selectors = {}
        
        for file_path, data in sorted(templates_map.items()):
            if isinstance(data, list):
                # Vision template (список имен)
                vision_templates[file_path] = data
            elif isinstance(data, dict) and 'names' in data:
                # DOM selector (dict с метаданными)
                dom_selectors[file_path] = data
        
        # Выводим Vision шаблоны
        if vision_templates:
            content.append("\n🖼️  VISION TEMPLATES (Template Matching)")
            content.append("-" * 80)
            for file_path, names in sorted(vision_templates.items()):
                content.append(f"\n📄 {file_path}")
                content.append("   Доступные имена:")
                for name in names:
                    content.append(f"     • {name}")
        
        # Выводим DOM селекторы
        if dom_selectors:
            content.append("\n\n🔧 DOM SELECTORS (CSS Selectors)")
            content.append("-" * 80)
            for file_path, data in sorted(dom_selectors.items()):
                names = data['names']
                metadata = data['metadata']
                
                content.append(f"\n📄 {file_path}")
                content.append("   Доступные имена:")
                for name in names:
                    content.append(f"     • {name}")
                
                # Метаданные
                if 'selector' in metadata:
                    content.append(f"   Selector: {metadata['selector']}")
                if 'type' in metadata:
                    content.append(f"   Type: {metadata['type']}")
                if 'confidence' in metadata:
                    content.append(f"   Confidence: {metadata['confidence']}")
                if 'method' in metadata:
                    content.append(f"   Method: {metadata['method']}")
                if 'fallback' in metadata:
                    content.append(f"   Fallback: {metadata['fallback']}")
        
        content.append("")
        
        # Раздел 3: Все уникальные имена (алфавитный список)
        content.append("\n" + "=" * 80)
        content.append("🏷️  РАЗДЕЛ 3: ВСЕ ДОСТУПНЫЕ ИМЕНА (алфавитный порядок)")
        content.append("=" * 80)
        content.append("")
        
        for name in sorted(self.template_names):
            content.append(f"  • {name}")
        
        content.append("")
        content.append("=" * 80)
        content.append("✅ Справочник сгенерирован успешно!")
        content.append("=" * 80)
        
        # Сохраняем в файл
        output_path = Path(output_file)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(content))
        
        print(f"✅ Справочник сохранен: {output_path}")
        print(f"📊 Всего строк: {len(content)}")
        print(f"🏷️  Уникальных имен: {len(self.template_names)}")
        print(f"📄 Файлов шаблонов: {len(templates_map)}")
        
        return output_path


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description='Генератор справочника DSL команд и шаблонов',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры:
  # Сгенерировать справочник для всех шаблонов
  python3 utils/dsl_reference_generator.py
  
  # Справочник для конкретной папки
  python3 utils/dsl_reference_generator.py --templates-path templates/Chrome/TikTok
  
  # Сохранить в другой файл
  python3 utils/dsl_reference_generator.py --output my_reference.txt
  
  # Справочник для Atlas шаблонов
  python3 utils/dsl_reference_generator.py --templates-path templates/Atlas
        """
    )
    
    parser.add_argument(
        '--templates-path',
        type=str,
        default='templates',
        help='Путь к папке с шаблонами (по умолчанию: templates)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='dsl_references/DSL_REFERENCE.txt',
        help='Имя выходного файла (по умолчанию: dsl_references/DSL_REFERENCE.txt)'
    )
    
    args = parser.parse_args()
    
    # Генерируем справочник
    generator = DSLReferenceGenerator(args.templates_path)
    generator.generate_reference(args.output)


if __name__ == "__main__":
    main()
