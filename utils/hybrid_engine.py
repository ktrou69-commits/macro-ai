#!/usr/bin/env python3
"""
hybrid_engine.py
DOM-Vision Hybrid Engine - Лучшее из двух миров

Стратегия:
1. Пытается DOM (быстро, надежно)
2. Fallback на Vision (если DOM не работает)
3. Автоматический выбор метода
"""

from typing import Optional, Tuple, Dict, Any
import time


class HybridEngine:
    """
    Гибридный движок для клика по элементам
    Комбинирует DOM (Selenium) и Vision (Template Matching)
    """
    
    def __init__(self, vision_engine, dom_engine=None):
        """
        Args:
            vision_engine: MacroSequenceRunner (template matching)
            dom_engine: Selenium driver (опционально)
        """
        self.vision = vision_engine
        self.dom = dom_engine
        self.stats = {
            'dom_success': 0,
            'dom_fail': 0,
            'vision_success': 0,
            'vision_fail': 0
        }
    
    def click(self, target: str, method: str = 'auto') -> bool:
        """
        Умный клик с автоматическим выбором метода
        
        Args:
            target: Имя элемента (например, "ChromeSearchField")
            method: 'auto', 'dom', 'vision', 'hybrid'
        
        Returns:
            True если успешно, False если нет
        """
        if method == 'auto':
            return self._auto_click(target)
        elif method == 'dom':
            return self._dom_click(target)
        elif method == 'vision':
            return self._vision_click(target)
        elif method == 'hybrid':
            return self._hybrid_click(target)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _auto_click(self, target: str) -> bool:
        """
        Автоматический выбор метода на основе контекста
        """
        # Если DOM доступен и элемент имеет DOM селектор
        if self.dom and self._has_dom_selector(target):
            print(f"🔄 Auto: Trying DOM first for {target}")
            if self._dom_click(target):
                return True
            
            print(f"⚠️  DOM failed, falling back to Vision")
            return self._vision_click(target)
        
        # Иначе используем Vision
        print(f"🔄 Auto: Using Vision for {target}")
        return self._vision_click(target)
    
    def _hybrid_click(self, target: str) -> bool:
        """
        Гибридный подход: DOM + Vision одновременно
        """
        print(f"🔄 Hybrid: Trying both DOM and Vision for {target}")
        
        # Пытаемся DOM
        dom_success = False
        if self.dom and self._has_dom_selector(target):
            dom_success = self._dom_click(target)
            if dom_success:
                return True
        
        # Fallback на Vision
        print(f"⚠️  DOM failed or unavailable, using Vision")
        return self._vision_click(target)
    
    def _dom_click(self, target: str) -> bool:
        """
        Клик через DOM (Selenium)
        """
        if not self.dom:
            return False
        
        try:
            selector = self._get_dom_selector(target)
            if not selector:
                return False
            
            print(f"🌐 DOM: Clicking {target} with selector: {selector}")
            
            # Selenium click
            element = self.dom.find_element_by_css_selector(selector)
            element.click()
            
            self.stats['dom_success'] += 1
            print(f"✅ DOM click successful")
            return True
            
        except Exception as e:
            self.stats['dom_fail'] += 1
            print(f"❌ DOM click failed: {e}")
            return False
    
    def _vision_click(self, target: str) -> bool:
        """
        Клик через Vision (Template Matching)
        """
        try:
            print(f"👁️  Vision: Searching for {target}")
            
            # Используем существующий vision engine
            step = {
                'action': 'click',
                'template': target,
                'clicks': 1
            }
            
            success = self.vision._execute_step(step)
            
            if success:
                self.stats['vision_success'] += 1
                print(f"✅ Vision click successful")
            else:
                self.stats['vision_fail'] += 1
                print(f"❌ Vision click failed")
            
            return success
            
        except Exception as e:
            self.stats['vision_fail'] += 1
            print(f"❌ Vision click failed: {e}")
            return False
    
    def _has_dom_selector(self, target: str) -> bool:
        """
        Проверяет есть ли DOM селектор для элемента
        """
        selector = self._get_dom_selector(target)
        return selector is not None
    
    def _get_dom_selector(self, target: str) -> Optional[str]:
        """
        Возвращает DOM селектор для элемента
        
        Маппинг имен шаблонов → CSS селекторы
        """
        # Маппинг для TikTok
        selectors = {
            # Chrome базовые
            'ChromeSearchField': 'input[type="text"][name="q"]',
            'ChromeNewTab': 'button[aria-label="New Tab"]',
            
            # TikTok
            'Chrome-TikTok-Like': 'button[data-e2e="like-button"]',
            'Like': 'button[data-e2e="like-button"]',
            'Chrome-TikTok-Comment': 'button[data-e2e="comment-button"]',
            'Chrome-TikTok-Search': 'button[data-e2e="search-button"]',
            'Chrome-TikTok-SearchField': 'input[data-e2e="search-input"]',
            
            # YouTube
            'Chrome-YouTube-Like': 'button[aria-label*="like"]',
            'Chrome-YouTube-SearchField': 'input#search',
            'Chrome-YouTube-Subscribe': 'button[aria-label*="Subscribe"]',
        }
        
        return selectors.get(target)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Возвращает статистику использования
        """
        total_dom = self.stats['dom_success'] + self.stats['dom_fail']
        total_vision = self.stats['vision_success'] + self.stats['vision_fail']
        
        return {
            'dom': {
                'success': self.stats['dom_success'],
                'fail': self.stats['dom_fail'],
                'total': total_dom,
                'success_rate': self.stats['dom_success'] / total_dom if total_dom > 0 else 0
            },
            'vision': {
                'success': self.stats['vision_success'],
                'fail': self.stats['vision_fail'],
                'total': total_vision,
                'success_rate': self.stats['vision_success'] / total_vision if total_vision > 0 else 0
            }
        }
    
    def print_stats(self):
        """
        Выводит статистику
        """
        stats = self.get_stats()
        
        print("\n" + "="*80)
        print("HYBRID ENGINE STATISTICS")
        print("="*80)
        
        print(f"\n🌐 DOM:")
        print(f"  Success: {stats['dom']['success']}")
        print(f"  Fail:    {stats['dom']['fail']}")
        print(f"  Total:   {stats['dom']['total']}")
        print(f"  Rate:    {stats['dom']['success_rate']:.1%}")
        
        print(f"\n👁️  Vision:")
        print(f"  Success: {stats['vision']['success']}")
        print(f"  Fail:    {stats['vision']['fail']}")
        print(f"  Total:   {stats['vision']['total']}")
        print(f"  Rate:    {stats['vision']['success_rate']:.1%}")
        
        print("\n" + "="*80)


# Пример использования
if __name__ == "__main__":
    print("Hybrid Engine - пример использования")
    print("="*80)
    
    # Псевдокод
    print("""
    # Инициализация
    vision_engine = MacroSequenceRunner()
    dom_engine = selenium.webdriver.Chrome()
    hybrid = HybridEngine(vision_engine, dom_engine)
    
    # Автоматический выбор метода
    hybrid.click("Chrome-TikTok-Like", method='auto')
    
    # Принудительно DOM
    hybrid.click("Chrome-TikTok-Like", method='dom')
    
    # Принудительно Vision
    hybrid.click("Chrome-TikTok-Like", method='vision')
    
    # Гибридный (пробует оба)
    hybrid.click("Chrome-TikTok-Like", method='hybrid')
    
    # Статистика
    hybrid.print_stats()
    """)
