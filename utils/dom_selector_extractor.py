#!/usr/bin/env python3
"""
dom_selector_extractor.py
Автоматическое извлечение DOM селекторов через AI

Workflow:
1. Пользователь кликает на элемент (или делает screenshot области)
2. Система снимает DOM snapshot
3. AI анализирует HTML и находит лучший селектор
4. Сохраняет в dom_selectors/ структуру
5. Автоматически доступен в DSL
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re


class DOMSelectorExtractor:
    """
    Извлекает DOM селекторы автоматически через AI
    """
    
    def __init__(self, selectors_path: str = "dom_selectors"):
        self.selectors_path = Path(selectors_path)
        self.selectors_path.mkdir(exist_ok=True)
        self.selectors_cache = {}
        self._load_selectors()
    
    def _load_selectors(self):
        """Загружает все сохраненные селекторы"""
        for json_file in self.selectors_path.rglob("*.json"):
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.selectors_cache.update(data)
    
    def extract_selector_from_html(self, html_snippet: str, element_name: str) -> Dict:
        """
        Извлекает селектор из HTML фрагмента
        
        Args:
            html_snippet: HTML код элемента (из F12)
            element_name: Имя элемента (например, "TikTok-Like")
        
        Returns:
            Dict с селектором и метаданными
        """
        # Парсим HTML
        selectors = self._parse_html_to_selectors(html_snippet)
        
        # Выбираем лучший селектор
        best_selector = self._choose_best_selector(selectors)
        
        return {
            'name': element_name,
            'selector': best_selector,
            'all_selectors': selectors,
            'html': html_snippet,
            'type': self._detect_element_type(html_snippet)
        }
    
    def _parse_html_to_selectors(self, html: str) -> List[str]:
        """
        Парсит HTML и генерирует возможные селекторы
        
        Пример:
        <div class="p8Jhnd" jsname="wgPSWd">
          <div jsname="Q8Kwad" class="aj35ze">
            <svg>...</svg>
          </div>
        </div>
        
        Генерирует:
        - div.p8Jhnd
        - div[jsname="wgPSWd"]
        - div.p8Jhnd[jsname="wgPSWd"]
        - div.aj35ze
        - div[jsname="Q8Kwad"]
        """
        selectors = []
        
        # Извлекаем классы
        classes = re.findall(r'class="([^"]+)"', html)
        for class_list in classes:
            for cls in class_list.split():
                selectors.append(f'.{cls}')
        
        # Извлекаем data-атрибуты (самые надежные!)
        data_attrs = re.findall(r'(data-[a-z0-9-]+)="([^"]+)"', html)
        for attr, value in data_attrs:
            selectors.append(f'[{attr}="{value}"]')
        
        # Извлекаем aria-атрибуты
        aria_attrs = re.findall(r'(aria-[a-z0-9-]+)="([^"]+)"', html)
        for attr, value in aria_attrs:
            selectors.append(f'[{attr}="{value}"]')
        
        # Извлекаем jsname (Google специфичный)
        jsnames = re.findall(r'jsname="([^"]+)"', html)
        for jsname in jsnames:
            selectors.append(f'[jsname="{jsname}"]')
        
        # Извлекаем ID
        ids = re.findall(r'id="([^"]+)"', html)
        for id_val in ids:
            selectors.append(f'#{id_val}')
        
        # Извлекаем тег
        tag_match = re.match(r'<(\w+)', html)
        if tag_match:
            tag = tag_match.group(1)
            selectors.append(tag)
        
        return selectors
    
    def _choose_best_selector(self, selectors: List[str]) -> str:
        """
        Выбирает лучший селектор по приоритету
        
        Приоритет:
        1. data-e2e (TikTok, Facebook)
        2. data-testid (React apps)
        3. aria-label (accessibility)
        4. ID
        5. Уникальный класс
        6. Комбинация атрибутов
        """
        # Приоритет 1: data-e2e
        for sel in selectors:
            if 'data-e2e' in sel:
                return sel
        
        # Приоритет 2: data-testid
        for sel in selectors:
            if 'data-testid' in sel:
                return sel
        
        # Приоритет 3: aria-label
        for sel in selectors:
            if 'aria-label' in sel:
                return sel
        
        # Приоритет 4: ID
        for sel in selectors:
            if sel.startswith('#'):
                return sel
        
        # Приоритет 5: data-* атрибуты
        for sel in selectors:
            if sel.startswith('[data-'):
                return sel
        
        # Приоритет 6: Первый класс
        for sel in selectors:
            if sel.startswith('.'):
                return sel
        
        # Fallback: первый доступный
        return selectors[0] if selectors else 'div'
    
    def _detect_element_type(self, html: str) -> str:
        """
        Определяет тип элемента
        """
        html_lower = html.lower()
        
        if '<button' in html_lower or 'role="button"' in html_lower:
            return 'button'
        elif '<input' in html_lower:
            if 'type="text"' in html_lower or 'type="search"' in html_lower:
                return 'input_field'
            elif 'type="submit"' in html_lower:
                return 'submit_button'
            else:
                return 'input'
        elif '<a' in html_lower:
            return 'link'
        elif '<textarea' in html_lower:
            return 'textarea'
        elif 'aria-label' in html_lower and 'like' in html_lower:
            return 'like_button'
        elif 'aria-label' in html_lower and 'comment' in html_lower:
            return 'comment_button'
        else:
            return 'element'
    
    def save_selector(self, element_name: str, selector_data: Dict, website: str = "TikTok"):
        """
        Сохраняет селектор в структуру
        
        Args:
            element_name: Имя элемента (например, "Like")
            selector_data: Данные селектора
            website: Название сайта (TikTok, YouTube, etc.)
        """
        # Создаем структуру папок
        website_path = self.selectors_path / website
        website_path.mkdir(exist_ok=True)
        
        # Файл для сайта
        selectors_file = website_path / "selectors.json"
        
        # Загружаем существующие
        if selectors_file.exists():
            with open(selectors_file, 'r', encoding='utf-8') as f:
                selectors = json.load(f)
        else:
            selectors = {}
        
        # Добавляем новый
        full_name = f"Chrome-{website}-{element_name}"
        selectors[full_name] = selector_data
        
        # Сохраняем
        with open(selectors_file, 'w', encoding='utf-8') as f:
            json.dump(selectors, f, indent=2, ensure_ascii=False)
        
        # Обновляем кэш
        self.selectors_cache[full_name] = selector_data
        
        print(f"✅ Селектор сохранен: {full_name}")
        print(f"   Selector: {selector_data['selector']}")
        print(f"   Type: {selector_data['type']}")
    
    def get_selector(self, element_name: str) -> Optional[str]:
        """
        Получает селектор по имени элемента
        """
        if element_name in self.selectors_cache:
            return self.selectors_cache[element_name]['selector']
        return None
    
    def extract_from_ai_prompt(self, html_snippet: str, context: str = "") -> Dict:
        """
        Использует AI для извлечения селектора
        
        Args:
            html_snippet: HTML код
            context: Контекст (например, "кнопка лайка в TikTok")
        
        Returns:
            Dict с селектором и метаданными
        """
        # TODO: Интеграция с AI (Gemini/GPT)
        # Пока используем rule-based подход
        
        selectors = self._parse_html_to_selectors(html_snippet)
        best_selector = self._choose_best_selector(selectors)
        
        return {
            'selector': best_selector,
            'all_selectors': selectors,
            'html': html_snippet,
            'context': context,
            'confidence': self._calculate_confidence(best_selector)
        }
    
    def _calculate_confidence(self, selector: str) -> float:
        """
        Рассчитывает уверенность в селекторе
        """
        if 'data-e2e' in selector:
            return 0.95
        elif 'data-testid' in selector:
            return 0.90
        elif 'aria-label' in selector:
            return 0.85
        elif selector.startswith('#'):
            return 0.80
        elif selector.startswith('[data-'):
            return 0.75
        elif selector.startswith('.'):
            return 0.60
        else:
            return 0.50
    
    def generate_structure_file(self, website: str):
        """
        Генерирует structure.txt файл для сайта
        (аналог templates/Chrome/TikTok/structure.txt)
        """
        website_path = self.selectors_path / website
        selectors_file = website_path / "selectors.json"
        
        if not selectors_file.exists():
            print(f"❌ Нет селекторов для {website}")
            return
        
        with open(selectors_file, 'r', encoding='utf-8') as f:
            selectors = json.load(f)
        
        # Генерируем structure.txt
        structure_file = website_path / "structure.txt"
        
        with open(structure_file, 'w', encoding='utf-8') as f:
            f.write(f"# DOM Selectors for {website}\n")
            f.write(f"# Auto-generated by DOM Selector Extractor\n\n")
            
            for name, data in selectors.items():
                f.write(f"{name}\n")
                f.write(f"  Selector: {data['selector']}\n")
                f.write(f"  Type: {data['type']}\n")
                f.write(f"  Confidence: {self._calculate_confidence(data['selector']):.0%}\n")
                f.write("\n")
        
        print(f"✅ Structure file created: {structure_file}")


# Пример использования
if __name__ == "__main__":
    print("DOM Selector Extractor - Пример использования")
    print("="*80)
    
    extractor = DOMSelectorExtractor()
    
    # Пример 1: Кнопка из Google (твой пример)
    html_google = '''<div class="p8Jhnd" jsname="wgPSWd" style="transform: translate3d(0px, 0px, 0px);">
        <div jsname="Q8Kwad" class="aj35ze" style="transform-origin: center center;">
            <svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M16.59 8.59L12 13.17 7.41 8.59 6 10l6 6 6-6z"></path>
            </svg>
        </div>
    </div>'''
    
    result = extractor.extract_selector_from_html(html_google, "DropdownButton")
    print("\n📌 Пример 1: Google Dropdown")
    print(f"   Best selector: {result['selector']}")
    print(f"   All selectors: {result['all_selectors']}")
    print(f"   Type: {result['type']}")
    
    # Пример 2: TikTok Like button
    html_tiktok = '''<button data-e2e="like-button" class="css-1vwu9aw" aria-label="like">
        <svg>...</svg>
    </button>'''
    
    result2 = extractor.extract_selector_from_html(html_tiktok, "Like")
    print("\n📌 Пример 2: TikTok Like")
    print(f"   Best selector: {result2['selector']}")
    print(f"   Type: {result2['type']}")
    
    # Сохранение
    extractor.save_selector("Like", result2, website="TikTok")
    
    # Генерация structure.txt
    extractor.generate_structure_file("TikTok")
