#!/usr/bin/env python3
"""
ai_dom_analyzer.py
AI-powered анализ DOM для автоматического извлечения селекторов

Использует Gemini AI для:
1. Анализа HTML структуры
2. Поиска лучших селекторов
3. Определения типа элемента
4. Генерации описаний
"""

import os
import json
from typing import Dict, Optional
from pathlib import Path

# Загрузка .env файла
try:
    from dotenv import load_dotenv
    # Загружаем .env из корня проекта
    env_path = Path(__file__).parent.parent / '.env'
    load_dotenv(env_path)
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  google-genai не установлен. Используйте: pip install google-genai")


class AIDOMAnalyzer:
    """
    AI-powered анализатор DOM элементов
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Args:
            api_key: Gemini API ключ (или из .env / переменной окружения)
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("google-genai не установлен")
        
        # API ключ: приоритет - параметр > .env > переменная окружения
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY не найден!\n"
                "Добавьте ключ в .env файл:\n"
                "GEMINI_API_KEY=your-key-here\n"
                "Или установите переменную окружения:\n"
                "export GEMINI_API_KEY='your-key'"
            )
        
        # Инициализация Gemini (новый SDK)
        self.client = genai.Client(api_key=self.api_key)
        from utils.api_config import api_config
        self.model_name = api_config.gemini_model
    
    def analyze_html(self, html_snippet: str, context: str = "") -> Dict:
        """
        Анализирует HTML и возвращает лучший селектор
        
        Args:
            html_snippet: HTML код элемента
            context: Контекст (например, "кнопка лайка в TikTok")
        
        Returns:
            Dict с селектором, типом, описанием
        """
        prompt = self._build_prompt(html_snippet, context)
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            result = self._parse_response(response.text)
            return result
        except Exception as e:
            print(f"❌ Ошибка AI анализа: {e}")
            return self._fallback_analysis(html_snippet)
    
    def _build_prompt(self, html: str, context: str) -> str:
        """
        Строит промпт для AI
        """
        return f"""
Ты эксперт по веб-автоматизации. Проанализируй HTML элемент и найди ЛУЧШИЙ CSS селектор.

HTML:
```html
{html}
```

Контекст: {context if context else "не указан"}

ЗАДАЧА:
1. Найди САМЫЙ НАДЕЖНЫЙ CSS селектор для этого элемента
2. Определи тип элемента (button, input, link, etc.)
3. Дай краткое описание

ПРИОРИТЕТ СЕЛЕКТОРОВ (от лучшего к худшему):
1. data-e2e="..." (TikTok, Facebook)
2. data-testid="..." (React apps)
3. aria-label="..." (accessibility)
4. id="..." (уникальный ID)
5. data-*="..." (любые data атрибуты)
6. class="..." (уникальный класс)
7. Комбинация атрибутов

ВАЖНО:
- Селектор должен быть УНИКАЛЬНЫМ
- Селектор должен быть СТАБИЛЬНЫМ (не меняться при обновлении страницы)
- Предпочитай data-* атрибуты классам

ОТВЕТ В JSON:
{{
  "selector": "лучший CSS селектор",
  "alternative_selectors": ["альтернатива 1", "альтернатива 2"],
  "element_type": "button|input|link|div|...",
  "description": "краткое описание элемента",
  "confidence": 0.95,
  "reasoning": "почему выбран этот селектор"
}}

ТОЛЬКО JSON, БЕЗ ДОПОЛНИТЕЛЬНОГО ТЕКСТА!
"""
    
    def _parse_response(self, response_text: str) -> Dict:
        """
        Парсит ответ AI
        """
        # Убираем markdown форматирование
        text = response_text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()
        
        # Парсим JSON
        try:
            result = json.loads(text)
            return result
        except json.JSONDecodeError as e:
            print(f"⚠️  Ошибка парсинга JSON: {e}")
            print(f"Response: {text}")
            return self._fallback_analysis("")
    
    def _fallback_analysis(self, html: str) -> Dict:
        """
        Fallback анализ без AI
        """
        return {
            "selector": "div",
            "alternative_selectors": [],
            "element_type": "element",
            "description": "Не удалось проанализировать",
            "confidence": 0.5,
            "reasoning": "Fallback analysis"
        }
    
    def analyze_multiple_elements(self, html_snippets: Dict[str, str]) -> Dict[str, Dict]:
        """
        Анализирует несколько элементов за раз
        
        Args:
            html_snippets: Dict {element_name: html_code}
        
        Returns:
            Dict {element_name: analysis_result}
        """
        results = {}
        
        for name, html in html_snippets.items():
            print(f"🔍 Анализ: {name}")
            result = self.analyze_html(html, context=name)
            results[name] = result
            print(f"   ✅ Селектор: {result['selector']}")
        
        return results
    
    def generate_selector_mapping(self, website: str, elements: Dict[str, str]) -> Dict:
        """
        Генерирует полный маппинг селекторов для сайта
        
        Args:
            website: Название сайта (TikTok, YouTube)
            elements: Dict {element_name: html_code}
        
        Returns:
            Dict с маппингом для использования в коде
        """
        results = self.analyze_multiple_elements(elements)
        
        # Формируем маппинг
        mapping = {}
        for name, analysis in results.items():
            full_name = f"Chrome-{website}-{name}"
            mapping[full_name] = {
                'selector': analysis['selector'],
                'type': analysis['element_type'],
                'description': analysis['description'],
                'confidence': analysis['confidence'],
                'alternatives': analysis.get('alternative_selectors', [])
            }
        
        return mapping


# Пример использования
if __name__ == "__main__":
    print("AI DOM Analyzer - Пример использования")
    print("="*80)
    
    # Проверка API ключа
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        print("❌ GEMINI_API_KEY не найден в переменных окружения")
        print("   Установите: export GEMINI_API_KEY='your-key'")
        exit(1)
    
    if not GEMINI_AVAILABLE:
        print("❌ google-generativeai не установлен")
        print("   Установите: pip install google-generativeai")
        exit(1)
    
    # Инициализация
    analyzer = AIDOMAnalyzer(api_key)
    
    # Пример 1: TikTok Like button
    html_like = '''<button data-e2e="like-button" class="css-1vwu9aw" aria-label="like">
        <svg width="24" height="24" viewBox="0 0 24 24">
            <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
        </svg>
    </button>'''
    
    print("\n📌 Анализ TikTok Like button:")
    result = analyzer.analyze_html(html_like, context="кнопка лайка в TikTok")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # Пример 2: Множественный анализ
    print("\n📌 Анализ нескольких элементов:")
    
    elements = {
        "Like": html_like,
        "Comment": '''<button data-e2e="comment-button" class="css-abc123">
            <svg>...</svg>
        </button>''',
        "SearchField": '''<input type="text" data-e2e="search-input" placeholder="Search">'''
    }
    
    mapping = analyzer.generate_selector_mapping("TikTok", elements)
    print(json.dumps(mapping, indent=2, ensure_ascii=False))
