#!/usr/bin/env python3
"""
Подробные описания модулей для точного определения контекста AI
"""

from typing import Dict, List, Any

class ModuleDescriptions:
    """
    Детальные описания модулей с контекстными подсказками для AI
    """
    
    DETAILED_MODULES = {
        "sequence_generator": {
            "name": "Генератор Последовательностей Автоматизации",
            "description": "Создает макросы для автоматизации действий на macOS через веб-браузеры, системные приложения и Spotlight поиск",
            
            # Подкатегории для точного определения
            "subcategories": {
                "web_automation": {
                    "description": "Автоматизация действий в веб-браузерах",
                    "triggers": [
                        # Прямые упоминания сайтов
                        "youtube", "google", "twitter", "facebook", "instagram", "linkedin", 
                        "github", "amazon", "netflix", "ebay", "wikipedia", "reddit",
                        
                        # Веб-действия
                        "зайди на", "перейди на", "открой сайт", "найди на сайте",
                        "поищи в интернете", "браузер", "веб-страница", "сайт",
                        
                        # Поисковые фразы для веб-сайтов
                        "найди на YouTube", "поищи в Google", "найди на GitHub",
                        "зайди на Twitter", "открой Amazon", "найди в интернете"
                    ],
                    "examples": [
                        "найди на YouTube видео про Python",
                        "поищи в Google курсы программирования", 
                        "зайди на Twitter и найди новости",
                        "найди на Amazon ноутбуки",
                        "открой GitHub и найди проекты по AI"
                    ],
                    "generated_commands": ["selenium_init", "selenium_click", "selenium_type", "selenium_close"],
                    "intent_confidence": 0.9
                },
                
                "system_automation": {
                    "description": "Автоматизация системных приложений macOS",
                    "triggers": [
                        # Системные приложения
                        "калькулятор", "calculator", "finder", "safari", "настройки",
                        "system preferences", "activity monitor", "terminal", "textedit",
                        
                        # Системные действия
                        "открой приложение", "запусти программу", "закрой приложение",
                        "переключи на", "сверни окно", "разверни окно"
                    ],
                    "examples": [
                        "открой калькулятор",
                        "запусти Finder", 
                        "открой системные настройки",
                        "посчитай в калькуляторе 25 * 17"
                    ],
                    "generated_commands": ["@system open_app", "click", "type", "hotkey"],
                    "intent_confidence": 0.95
                },
                
                "spotlight_automation": {
                    "description": "Поиск файлов и приложений через Spotlight",
                    "triggers": [
                        # Spotlight специфичные фразы
                        "найди файл", "поищи документ", "найди приложение через spotlight",
                        "spotlight поиск", "найди на компьютере", "поиск файлов",
                        
                        # Типы файлов
                        "pdf", "doc", "txt", "jpg", "png", "mp3", "mp4", "zip",
                        "найди все", "файлы типа", "документы", "изображения", "музыка"
                    ],
                    "examples": [
                        "найди файлы PDF через Spotlight",
                        "поищи документы Word",
                        "найди все изображения на компьютере",
                        "найди приложения через Spotlight"
                    ],
                    "generated_commands": ["key cmd+space", "type", "press enter"],
                    "intent_confidence": 0.85
                },
                
                "calculator_automation": {
                    "description": "Автоматизация вычислений в калькуляторе macOS",
                    "triggers": [
                        # Математические операции
                        "посчитай", "вычисли", "сколько будет", "калькулятор",
                        "+", "-", "*", "/", "=", "плюс", "минус", "умножить", "разделить"
                    ],
                    "examples": [
                        "посчитай 25 * 17",
                        "вычисли 100 / 4 + 50",
                        "сколько будет 15% от 200"
                    ],
                    "generated_commands": ["@system open_app Calculator", "click button_", "wait"],
                    "intent_confidence": 0.98
                }
            },
            
            "priority_rules": [
                # Правила приоритета для разрешения конфликтов
                {
                    "rule": "Если упоминается конкретный сайт (YouTube, Google, etc.) - всегда web_automation",
                    "examples": ["найди в Google", "зайди на YouTube", "открой Amazon"]
                },
                {
                    "rule": "Если есть математические операции - всегда calculator_automation", 
                    "examples": ["посчитай 2+2", "вычисли 50*3"]
                },
                {
                    "rule": "Если упоминается 'файл', 'документ', 'на компьютере' - spotlight_automation",
                    "examples": ["найди файл PDF", "поищи документы"]
                },
                {
                    "rule": "Если упоминается системное приложение без веб-контекста - system_automation",
                    "examples": ["открой калькулятор", "запусти Finder"]
                }
            ]
        },
        
        "dom_analyzer": {
            "name": "Анализатор DOM Структуры",
            "description": "Извлекает селекторы и анализирует структуру веб-страниц",
            "triggers": [
                "селектор", "dom", "css selector", "xpath", "элемент страницы",
                "структура сайта", "веб-элемент", "html элемент",
                "найди селектор", "проанализируй страницу", "извлеки селекторы"
            ],
            "examples": [
                "найди селекторы на странице Amazon",
                "проанализируй структуру сайта YouTube",
                "извлеки CSS селекторы для кнопок"
            ],
            "intent_confidence": 0.9
        },
        
        "prompt_updater": {
            "name": "Обновлятор AI Промптов",
            "description": "Улучшает и обновляет промпты для AI генерации",
            "triggers": [
                "промпт", "шаблон", "обнови промпты", "улучши генерацию",
                "ai промпт", "обновить шаблоны", "улучшить ai"
            ],
            "examples": [
                "обнови промпты для веб-автоматизации",
                "улучши шаблоны генерации",
                "обновить AI промпты"
            ],
            "intent_confidence": 0.95
        }
    }
    
    @classmethod
    def analyze_user_intent(cls, user_request: str) -> Dict[str, Any]:
        """
        Детальный анализ намерений пользователя
        
        Args:
            user_request: Запрос пользователя
            
        Returns:
            Детальная информация о намерении
        """
        request_lower = user_request.lower()
        
        # Анализ для sequence_generator (основной модуль)
        if "sequence_generator" in cls.DETAILED_MODULES:
            seq_gen = cls.DETAILED_MODULES["sequence_generator"]
            
            # Проверяем подкатегории
            subcategory_scores = {}
            
            for subcat_name, subcat_info in seq_gen["subcategories"].items():
                score = 0
                matched_triggers = []
                
                # Подсчитываем совпадения триггеров
                for trigger in subcat_info["triggers"]:
                    if trigger.lower() in request_lower:
                        score += 1
                        matched_triggers.append(trigger)
                
                # Дополнительные очки за точные совпадения с примерами
                for example in subcat_info["examples"]:
                    if example.lower() in request_lower:
                        score += 3
                        matched_triggers.append(f"example: {example}")
                
                if score > 0:
                    subcategory_scores[subcat_name] = {
                        "score": score,
                        "confidence": min(score / 5.0, subcat_info["intent_confidence"]),
                        "matched_triggers": matched_triggers,
                        "info": subcat_info
                    }
            
            # Находим лучшую подкатегорию
            if subcategory_scores:
                best_subcategory = max(subcategory_scores, key=lambda x: subcategory_scores[x]["score"])
                best_info = subcategory_scores[best_subcategory]
                
                # Применяем правила приоритета
                final_subcategory = cls._apply_priority_rules(request_lower, best_subcategory, seq_gen["priority_rules"])
                
                return {
                    "module": "sequence_generator",
                    "subcategory": final_subcategory,
                    "confidence": best_info["confidence"],
                    "matched_triggers": best_info["matched_triggers"],
                    "expected_commands": best_info["info"]["generated_commands"],
                    "analysis_method": "detailed_intent_analysis",
                    "all_scores": subcategory_scores
                }
        
        # Проверяем другие модули
        for module_name, module_info in cls.DETAILED_MODULES.items():
            if module_name == "sequence_generator":
                continue
                
            score = 0
            matched_triggers = []
            
            for trigger in module_info["triggers"]:
                if trigger.lower() in request_lower:
                    score += 1
                    matched_triggers.append(trigger)
            
            if score > 0:
                return {
                    "module": module_name,
                    "subcategory": None,
                    "confidence": min(score / 3.0, module_info["intent_confidence"]),
                    "matched_triggers": matched_triggers,
                    "expected_commands": [],
                    "analysis_method": "detailed_intent_analysis"
                }
        
        # Fallback на sequence_generator с низкой уверенностью
        return {
            "module": "sequence_generator", 
            "subcategory": "system_automation",  # безопасный fallback
            "confidence": 0.3,
            "matched_triggers": [],
            "expected_commands": ["@system open_app"],
            "analysis_method": "fallback"
        }
    
    @classmethod
    def _apply_priority_rules(cls, request_lower: str, current_subcategory: str, priority_rules: List[Dict]) -> str:
        """
        Применяет правила приоритета для разрешения конфликтов
        """
        # Проверяем веб-сайты (высший приоритет)
        web_sites = ["youtube", "google", "twitter", "facebook", "instagram", "linkedin", 
                     "github", "amazon", "netflix", "ebay", "wikipedia", "reddit"]
        
        for site in web_sites:
            if site in request_lower:
                return "web_automation"
        
        # Проверяем математические операции
        math_indicators = ["+", "-", "*", "/", "=", "посчитай", "вычисли", "сколько будет"]
        if any(indicator in request_lower for indicator in math_indicators):
            return "calculator_automation"
        
        # Проверяем файловый поиск
        file_indicators = ["файл", "документ", "на компьютере", "pdf", "doc", "txt", "изображения"]
        if any(indicator in request_lower for indicator in file_indicators):
            return "spotlight_automation"
        
        # Возвращаем текущую подкатегорию если нет приоритетных правил
        return current_subcategory
    
    @classmethod
    def get_prompt_type_for_subcategory(cls, subcategory: str) -> str:
        """
        Возвращает тип промпта для подкатегории
        """
        mapping = {
            "web_automation": "web_automation",
            "system_automation": "system_automation", 
            "spotlight_automation": "spotlight_automation",
            "calculator_automation": "calculator_automation"
        }
        return mapping.get(subcategory, "mixed_automation")

def analyze_request(user_request: str) -> Dict[str, Any]:
    """
    Быстрая функция для анализа запроса
    """
    return ModuleDescriptions.analyze_user_intent(user_request)

if __name__ == "__main__":
    # Тестирование детального анализа
    test_requests = [
        "найди на YouTube видео про Python",
        "поищи в Google курсы программирования",
        "зайди на Twitter и найди новости",
        "открой калькулятор",
        "посчитай 25 * 17",
        "найди файлы PDF через Spotlight",
        "найди селекторы на странице",
        "обнови промпты"
    ]
    
    print("🧪 ТЕСТИРОВАНИЕ ДЕТАЛЬНОГО АНАЛИЗА НАМЕРЕНИЙ")
    print("=" * 70)
    
    for request in test_requests:
        print(f"\n📝 Запрос: '{request}'")
        result = analyze_request(request)
        
        print(f"   🎯 Модуль: {result['module']}")
        if result['subcategory']:
            print(f"   📂 Подкатегория: {result['subcategory']}")
        print(f"   🎲 Уверенность: {result['confidence']:.2f}")
        print(f"   🔍 Триггеры: {result['matched_triggers'][:3]}")  # Первые 3
        if result['expected_commands']:
            print(f"   ⚙️  Команды: {result['expected_commands'][:2]}")  # Первые 2
