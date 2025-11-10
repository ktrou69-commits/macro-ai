#!/usr/bin/env python3
"""
dom_selector_extractor.py
Утилита для сохранения и загрузки DOM селекторов
"""

import json
from pathlib import Path
from typing import Dict, Optional, List


class DOMSelectorExtractor:
    """Класс для работы с DOM селекторами"""
    
    def __init__(self, base_dir: Optional[Path] = None):
        """
        Инициализация
        
        Args:
            base_dir: Базовая директория для селекторов (по умолчанию dom_selectors/)
        """
        if base_dir is None:
            # Определяем корень проекта
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent
            base_dir = project_root / 'dom_selectors'
        
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    def save_selector(
        self, 
        element_name: str, 
        selector_data: Dict, 
        website: str = 'default'
    ) -> Path:
        """
        Сохраняет селектор в JSON файл
        
        Args:
            element_name: Название элемента
            selector_data: Данные селектора (dict)
            website: Название сайта
            
        Returns:
            Путь к сохраненному файлу
        """
        # Создаем директорию для сайта
        website_dir = self.base_dir / website.lower()
        website_dir.mkdir(parents=True, exist_ok=True)
        
        # Путь к файлу селекторов
        selectors_file = website_dir / 'selectors.json'
        
        # Загружаем существующие селекторы
        if selectors_file.exists():
            with open(selectors_file, 'r', encoding='utf-8') as f:
                selectors = json.load(f)
        else:
            selectors = {}
        
        # Добавляем новый селектор
        selectors[element_name] = selector_data
        
        # Сохраняем
        with open(selectors_file, 'w', encoding='utf-8') as f:
            json.dump(selectors, f, indent=2, ensure_ascii=False)
        
        return selectors_file
    
    def load_selectors(self, website: str) -> Dict:
        """
        Загружает все селекторы для сайта
        
        Args:
            website: Название сайта
            
        Returns:
            Словарь селекторов
        """
        website_dir = self.base_dir / website.lower()
        selectors_file = website_dir / 'selectors.json'
        
        if not selectors_file.exists():
            return {}
        
        with open(selectors_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_selector(self, element_name: str, website: str) -> Optional[Dict]:
        """
        Получает конкретный селектор
        
        Args:
            element_name: Название элемента
            website: Название сайта
            
        Returns:
            Данные селектора или None
        """
        selectors = self.load_selectors(website)
        return selectors.get(element_name)
    
    def list_websites(self) -> List[str]:
        """
        Возвращает список всех сайтов с селекторами
        
        Returns:
            Список названий сайтов
        """
        if not self.base_dir.exists():
            return []
        
        websites = []
        for item in self.base_dir.iterdir():
            if item.is_dir():
                websites.append(item.name)
        
        return sorted(websites)
    
    def list_selectors(self, website: str) -> List[str]:
        """
        Возвращает список всех селекторов для сайта
        
        Args:
            website: Название сайта
            
        Returns:
            Список названий селекторов
        """
        selectors = self.load_selectors(website)
        return list(selectors.keys())
