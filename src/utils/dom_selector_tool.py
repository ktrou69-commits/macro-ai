#!/usr/bin/env python3
"""
dom_selector_tool.py
Интерактивный инструмент для извлечения DOM селекторов

Workflow:
1. Пользователь копирует HTML из F12
2. Вставляет в инструмент
3. AI анализирует и находит селектор
4. Сохраняет в dom_selectors/
5. Автоматически доступен в DSL
"""

import os
import sys
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Загрузка .env файла
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Загружен .env файл: {env_path}")
except ImportError:
    print("⚠️  python-dotenv не установлен. Установите: pip install python-dotenv")

from src.utils.dom_selector_extractor import DOMSelectorExtractor
from src.ai.dom_analyzer import AIDOMAnalyzer, GEMINI_AVAILABLE


class DOMSelectorTool:
    """
    Интерактивный инструмент для работы с DOM селекторами
    """
    
    def __init__(self):
        self.extractor = DOMSelectorExtractor()
        self.ai_analyzer = None
        
        # Проверяем доступность AI
        api_key = os.getenv('GEMINI_API_KEY')
        
        if GEMINI_AVAILABLE and api_key:
            try:
                self.ai_analyzer = AIDOMAnalyzer()
                print("✅ AI анализатор доступен (ключ из .env)")
            except Exception as e:
                print(f"⚠️  AI анализатор недоступен: {e}")
        elif not GEMINI_AVAILABLE:
            print("⚠️  AI анализатор недоступен: google-genai не установлен")
            print("   Установите: pip install google-genai")
        elif not api_key:
            print("⚠️  AI анализатор недоступен: GEMINI_API_KEY не найден")
            print("   Добавьте ключ в .env файл или установите переменную окружения")
    
    def run(self):
        """
        Запускает интерактивное меню
        """
        while True:
            print("\n" + "="*80)
            print("DOM SELECTOR TOOL - Автоматическое извлечение селекторов")
            print("="*80)
            print("\n1. Извлечь селектор из HTML (AI)")
            print("2. Извлечь селектор из HTML (Rule-based)")
            print("3. Просмотреть сохраненные селекторы")
            print("4. Генерировать structure.txt для сайта")
            print("5. Массовое извлечение (несколько элементов)")
            print("0. Выход")
            
            choice = input("\nВыбор: ").strip()
            
            if choice == '1':
                self.extract_with_ai()
            elif choice == '2':
                self.extract_rule_based()
            elif choice == '3':
                self.view_selectors()
            elif choice == '4':
                self.generate_structure()
            elif choice == '5':
                self.batch_extract()
            elif choice == '0':
                print("👋 До свидания!")
                break
            else:
                print("❌ Неверный выбор")
    
    def extract_with_ai(self):
        """
        Извлечение селектора с помощью AI
        """
        if not self.ai_analyzer:
            print("❌ AI анализатор недоступен")
            print("   Установите GEMINI_API_KEY и google-genai")
            return
        
        print("\n" + "-"*80)
        print("ИЗВЛЕЧЕНИЕ СЕЛЕКТОРА С AI")
        print("-"*80)
        
        # Ввод данных
        website = input("\nНазвание сайта (TikTok, YouTube, etc.): ").strip()
        element_name = input("Название элемента (Like, Comment, SearchField): ").strip()
        
        # Выбор способа ввода
        print("\nСпособ ввода HTML:")
        print("  1. Вставить в терминал (для коротких HTML)")
        print("  2. Загрузить из файла (для длинных HTML)")
        input_method = input("Выбор (1/2): ").strip()
        
        html = ""
        
        if input_method == "2":
            # Загрузка из файла
            print("\nСохраните HTML в файл (например: /tmp/element.html)")
            file_path = input("Путь к файлу: ").strip()
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    html = f.read().strip()
                print(f"✅ Загружено {len(html)} символов")
            except FileNotFoundError:
                print(f"❌ Файл не найден: {file_path}")
                return
            except Exception as e:
                print(f"❌ Ошибка чтения файла: {e}")
                return
        else:
            # Ввод в терминал
            print("\nВставьте HTML код элемента (из F12):")
            print("(Для завершения ввода нажмите Enter дважды)")
            print("⚠️  ВНИМАНИЕ: Если HTML длинный (>1000 символов), используйте опцию 2")
            
            html_lines = []
            empty_count = 0
            
            while True:
                try:
                    line = input()
                except EOFError:
                    break
                
                if line == "":
                    empty_count += 1
                    if empty_count >= 2:
                        # Две пустые строки подряд - завершаем ввод
                        break
                else:
                    empty_count = 0
                
                html_lines.append(line)
            
            # Убираем последние пустые строки
            while html_lines and html_lines[-1] == "":
                html_lines.pop()
            
            html = "\n".join(html_lines).strip()
            
            if len(html) > 1000:
                print(f"⚠️  HTML длинный ({len(html)} символов)")
                print("   Если текст обрезан, используйте опцию 2 (файл)")
        
        if not html:
            print("❌ HTML не введен")
            return
        
        # Анализ
        print("\n🔍 Анализ HTML с помощью AI...")
        context = f"{element_name} в {website}"
        result = self.ai_analyzer.analyze_html(html, context=context)
        
        # Результат
        print("\n" + "="*80)
        print("РЕЗУЛЬТАТ АНАЛИЗА")
        print("="*80)
        print(f"\n✅ Лучший селектор: {result['selector']}")
        print(f"   Тип элемента: {result['element_type']}")
        print(f"   Описание: {result['description']}")
        print(f"   Уверенность: {result['confidence']:.0%}")
        print(f"\n💡 Обоснование: {result.get('reasoning', 'N/A')}")
        
        if result.get('alternative_selectors'):
            print(f"\n📋 Альтернативные селекторы:")
            for alt in result['alternative_selectors']:
                print(f"   • {alt}")
        
        # Сохранение
        save = input("\n💾 Сохранить селектор? (y/n): ").strip().lower()
        if save == 'y':
            selector_data = {
                'selector': result['selector'],
                'type': result['element_type'],
                'description': result['description'],
                'confidence': result['confidence'],
                'alternatives': result.get('alternative_selectors', []),
                'html': html
            }
            
            # Сохраняем с суффиксом -dom
            element_name_dom = f"{element_name}-dom"
            self.extractor.save_selector(element_name_dom, selector_data, website=website)
            
            # Обновляем structure.txt
            self._update_structure_txt(website, element_name, result)
            
            print(f"\n✅ Селектор сохранен: Chrome-{website}-{element_name_dom}")
            print(f"   Файл: dom_selectors/{website}/selectors.json")
            print(f"   Structure: templates/Chrome/{website.title()}/structure.txt")
    
    def extract_rule_based(self):
        """
        Извлечение селектора без AI (rule-based)
        """
        print("\n" + "-"*80)
        print("ИЗВЛЕЧЕНИЕ СЕЛЕКТОРА (RULE-BASED)")
        print("-"*80)
        
        website = input("\nНазвание сайта: ").strip()
        element_name = input("Название элемента: ").strip()
        
        print("\nВставьте HTML код:")
        print("(Для завершения ввода нажмите Enter дважды)")
        
        html_lines = []
        empty_count = 0
        
        while True:
            line = input()
            
            if line == "":
                empty_count += 1
                if empty_count >= 2:
                    break
            else:
                empty_count = 0
            
            html_lines.append(line)
        
        # Убираем последние пустые строки
        while html_lines and html_lines[-1] == "":
            html_lines.pop()
        
        html = "\n".join(html_lines).strip()
        
        if not html:
            print("❌ HTML не введен")
            return
        
        # Анализ
        print("\n🔍 Анализ HTML...")
        result = self.extractor.extract_selector_from_html(html, element_name)
        
        # Результат
        print("\n" + "="*80)
        print("РЕЗУЛЬТАТ")
        print("="*80)
        print(f"\n✅ Лучший селектор: {result['selector']}")
        print(f"   Тип элемента: {result['type']}")
        print(f"\n📋 Все найденные селекторы:")
        for sel in result['all_selectors']:
            print(f"   • {sel}")
        
        # Сохранение
        save = input("\n💾 Сохранить? (y/n): ").strip().lower()
        if save == 'y':
            self.extractor.save_selector(element_name, result, website=website)
    
    def view_selectors(self):
        """
        Просмотр сохраненных селекторов
        """
        print("\n" + "-"*80)
        print("СОХРАНЕННЫЕ СЕЛЕКТОРЫ")
        print("-"*80)
        
        if not self.extractor.selectors_cache:
            print("\n❌ Нет сохраненных селекторов")
            return
        
        for name, data in self.extractor.selectors_cache.items():
            print(f"\n📌 {name}")
            print(f"   Selector: {data['selector']}")
            print(f"   Type: {data['type']}")
            if 'description' in data:
                print(f"   Description: {data['description']}")
    
    def generate_structure(self):
        """
        Генерирует structure.txt для сайта
        """
        print("\n" + "-"*80)
        print("ГЕНЕРАЦИЯ STRUCTURE.TXT")
        print("-"*80)
        
        website = input("\nНазвание сайта: ").strip()
        self.extractor.generate_structure_file(website)
    
    def batch_extract(self):
        """
        Массовое извлечение селекторов
        """
        if not self.ai_analyzer:
            print("❌ Для массового извлечения нужен AI анализатор")
            return
        
        print("\n" + "-"*80)
        print("МАССОВОЕ ИЗВЛЕЧЕНИЕ")
        print("-"*80)
        
        website = input("\nНазвание сайта: ").strip()
        
        elements = {}
        
        print("\nВводите элементы (пустое имя для завершения):")
        while True:
            element_name = input("\nНазвание элемента: ").strip()
            if not element_name:
                break
            
            print("HTML код (Enter дважды для завершения):")
            html_lines = []
            empty_count = 0
            
            while True:
                line = input()
                
                if line == "":
                    empty_count += 1
                    if empty_count >= 2:
                        break
                else:
                    empty_count = 0
                
                html_lines.append(line)
            
            # Убираем последние пустые строки
            while html_lines and html_lines[-1] == "":
                html_lines.pop()
            
            html = "\n".join(html_lines).strip()
            if html:
                elements[element_name] = html
        
        if not elements:
            print("❌ Нет элементов для анализа")
            return
        
        # Анализ
        print(f"\n🔍 Анализ {len(elements)} элементов...")
        mapping = self.ai_analyzer.generate_selector_mapping(website, elements)
        
        # Результат
        print("\n" + "="*80)
        print("РЕЗУЛЬТАТЫ")
        print("="*80)
        
        for name, data in mapping.items():
            print(f"\n📌 {name}")
            print(f"   Selector: {data['selector']}")
            print(f"   Type: {data['type']}")
            print(f"   Confidence: {data['confidence']:.0%}")
        
        # Сохранение
        save = input("\n💾 Сохранить все? (y/n): ").strip().lower()
        if save == 'y':
            for element_name, html in elements.items():
                result = mapping[f"Chrome-{website}-{element_name}"]
                self.extractor.save_selector(element_name, result, website=website)
            
            print(f"\n✅ Сохранено {len(elements)} селекторов")
    
    def _update_structure_txt(self, website: str, element_name: str, result: dict):
        """
        Обновляет structure.txt в templates/Chrome/{Website}/
        """
        from pathlib import Path
        
        # Путь к structure.txt
        structure_path = Path(f"templates/Chrome/{website.title()}/structure.txt")
        
        if not structure_path.exists():
            print(f"⚠️  Structure файл не найден: {structure_path}")
            return
        
        # Читаем существующий файл
        with open(structure_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Формируем запись для DOM селектора
        dom_entry = f"""
 │    │    # Chrome-{website.title()}-{element_name.title()}-dom
 │    │    #   Selector: {result['selector']}
 │    │    #   Type: {result['element_type']}
 │    │    #   Confidence: {result['confidence']:.0%}
 │    │    #   Description: {result['description']}
 │    │    #   Method: DOM (быстро, надежно)
 │    │    #   Fallback: Chrome-{website.title()}-{element_name.title()}-btn.png (Vision)
"""
        
        # Проверяем есть ли уже секция DOM SELECTORS
        if "# DOM SELECTORS" in content:
            # Добавляем в конец секции DOM
            content = content.rstrip() + dom_entry
        else:
            # Создаем секцию DOM SELECTORS
            dom_section = """
 │    │
 │    │    # ========================================
 │    │    # DOM SELECTORS (CSS Selectors)
 │    │    # ========================================""" + dom_entry
            content = content.rstrip() + dom_section
        
        # Сохраняем
        with open(structure_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   ✅ Обновлен structure.txt")


def main():
    """
    Точка входа
    """
    tool = DOMSelectorTool()
    tool.run()


if __name__ == "__main__":
    main()
