"""
Примеры для AI (Few-Shot Learning)
Улучшает качество генерации через обучение на примерах
"""

from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class AIExamples:
    """Коллекция примеров для обучения AI"""
    
    EXAMPLES = {
        # Веб-автоматизация
        "youtube_automation": {
            "request": "открой YouTube и найди видео про Python",
            "intent_type": "web_automation",
            "response": """
НАЗВАНИЕ: Поиск видео на YouTube

DSL КОД:
```atlas
# Открытие YouTube и поиск видео про Python
navigate "https://youtube.com"
wait 3s
click_element "//input[@id='search']"
wait 1s
type "Python tutorial"
press enter
wait 2s
click_element "//div[@id='contents']//a[@id='video-title'][1]"
wait 3s
```

ОПИСАНИЕ: Автоматически открывает YouTube, выполняет поиск "Python tutorial" и кликает на первое видео в результатах
"""
        },
        
        "google_search": {
            "request": "найди в Google информацию про искусственный интеллект",
            "intent_type": "web_automation",
            "response": """
НАЗВАНИЕ: Поиск в Google про ИИ

DSL КОД:
```atlas
# Поиск информации про искусственный интеллект в Google
navigate "https://google.com"
wait 2s
click_element "//input[@name='q']"
wait 1s
type "искусственный интеллект"
press enter
wait 3s
click_element "//div[@id='search']//div[@class='g'][1]//a"
wait 2s
```

ОПИСАНИЕ: Открывает Google, выполняет поиск по запросу "искусственный интеллект" и переходит на первый результат
"""
        },
        
        "github_search": {
            "request": "найди на GitHub проект по машинному обучению",
            "intent_type": "web_automation",
            "response": """
НАЗВАНИЕ: Поиск ML проекта на GitHub

DSL КОД:
```atlas
# Поиск проекта по машинному обучению на GitHub
navigate "https://github.com"
wait 2s
click_element "//input[@placeholder='Search GitHub']"
wait 1s
type "machine learning python"
press enter
wait 3s
click_element "//div[@data-testid='results-list']//a[1]"
wait 2s
```

ОПИСАНИЕ: Открывает GitHub, ищет проекты по машинному обучению на Python и переходит к первому результату
"""
        },
        
        # Системная автоматизация
        "calculator_automation": {
            "request": "открой калькулятор и посчитай 25 + 17",
            "intent_type": "system_automation",
            "response": """
НАЗВАНИЕ: Вычисление в Калькуляторе

DSL КОД:
```atlas
# Открытие калькулятора и вычисление 25 + 17
system_command "open -a Calculator"
wait 2s
click "button_2"
click "button_5"
click "button_plus"
click "button_1"
click "button_7"
click "button_equals"
wait 1s
```

ОПИСАНИЕ: Открывает калькулятор macOS и выполняет вычисление 25 + 17, результат: 42
"""
        },
        
        "finder_search": {
            "request": "найди в finder файлы python",
            "intent_type": "system_automation",
            "response": """
НАЗВАНИЕ: Поиск Python файлов в Finder

DSL КОД:
```atlas
# Поиск файлов Python через Finder
system_command "open -a Finder"
wait 2s
click "search_field"
wait 1s
type "*.py"
press enter
wait 3s
```

ОПИСАНИЕ: Открывает Finder и выполняет поиск всех файлов с расширением .py в системе
"""
        },
        
        "system_preferences": {
            "request": "открой настройки звука",
            "intent_type": "system_automation",
            "response": """
НАЗВАНИЕ: Открытие настроек звука

DSL КОД:
```atlas
# Открытие настроек звука в System Preferences
system_command "open -a 'System Preferences'"
wait 3s
click "sound_pref"
wait 2s
```

ОПИСАНИЕ: Открывает Системные настройки macOS и переходит к разделу настроек звука
"""
        },
        
        # Spotlight автоматизация
        "spotlight_app_search": {
            "request": "найди через spotlight терминал",
            "intent_type": "spotlight_automation",
            "response": """
НАЗВАНИЕ: Поиск Терминала через Spotlight

DSL КОД:
```atlas
# Поиск и запуск Терминала через Spotlight
key "cmd+space"
wait 0.5s
type "Terminal"
wait 1s
press enter
wait 2s
```

ОПИСАНИЕ: Открывает Spotlight поиск, ищет приложение Terminal и запускает его
"""
        },
        
        "spotlight_file_search": {
            "request": "найди документы через spotlight",
            "intent_type": "spotlight_automation",
            "response": """
НАЗВАНИЕ: Поиск документов через Spotlight

DSL КОД:
```atlas
# Поиск документов через Spotlight
key "cmd+space"
wait 0.5s
type "Documents"
wait 1s
press enter
wait 2s
```

ОПИСАНИЕ: Использует Spotlight для поиска и открытия папки Documents
"""
        },
        
        # Смешанная автоматизация
        "complex_workflow": {
            "request": "открой Chrome, зайди на YouTube и найди видео про программирование",
            "intent_type": "mixed_automation",
            "response": """
НАЗВАНИЕ: Комплексный поиск видео

DSL КОД:
```atlas
# Комплексный workflow: Chrome -> YouTube -> поиск видео
system_command "open -a 'Google Chrome'"
wait 3s
navigate "https://youtube.com"
wait 3s
click_element "//input[@id='search']"
wait 1s
type "программирование для начинающих"
press enter
wait 3s
click_element "//div[@id='contents']//a[@id='video-title'][1]"
wait 2s
```

ОПИСАНИЕ: Открывает Google Chrome, переходит на YouTube, ищет видео про программирование и запускает первое найденное видео
"""
        },
        
        "productivity_workflow": {
            "request": "открой калькулятор, посчитай 15*8, потом найди результат в Google",
            "intent_type": "mixed_automation",
            "response": """
НАЗВАНИЕ: Вычисление и поиск результата

DSL КОД:
```atlas
# Вычисление в калькуляторе и поиск результата в Google
system_command "open -a Calculator"
wait 2s
click "button_1"
click "button_5"
click "button_multiply"
click "button_8"
click "button_equals"
wait 2s
system_command "open -a 'Google Chrome'"
wait 3s
navigate "https://google.com"
wait 2s
click_element "//input[@name='q']"
type "что означает число 120"
press enter
wait 3s
```

ОПИСАНИЕ: Вычисляет 15×8 в калькуляторе (результат: 120), затем ищет информацию об этом числе в Google
"""
        }
    }
    
    @classmethod
    def get_examples_for_intent(cls, intent_type: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Получение примеров для конкретного типа намерения
        
        Args:
            intent_type: Тип намерения
            limit: Максимальное количество примеров
            
        Returns:
            Список примеров
        """
        examples = []
        count = 0
        
        for example_key, example_data in cls.EXAMPLES.items():
            if count >= limit:
                break
                
            if example_data.get("intent_type") == intent_type:
                examples.append({
                    "key": example_key,
                    "request": example_data["request"],
                    "response": example_data["response"]
                })
                count += 1
        
        logger.info(f"Найдено {len(examples)} примеров для типа: {intent_type}")
        return examples
    
    @classmethod
    def get_all_examples(cls) -> Dict[str, Any]:
        """Получение всех примеров"""
        return cls.EXAMPLES.copy()
    
    @classmethod
    def add_example(cls, key: str, request: str, intent_type: str, response: str):
        """Добавление нового примера"""
        cls.EXAMPLES[key] = {
            "request": request,
            "intent_type": intent_type,
            "response": response
        }
        logger.info(f"Добавлен новый пример: {key}")
    
    @classmethod
    def format_examples_for_prompt(cls, intent_type: str, limit: int = 2) -> str:
        """
        Форматирование примеров для включения в промпт
        
        Args:
            intent_type: Тип намерения
            limit: Максимальное количество примеров
            
        Returns:
            Отформатированная строка с примерами
        """
        examples = cls.get_examples_for_intent(intent_type, limit)
        
        if not examples:
            return "Примеры недоступны"
        
        formatted_examples = []
        for i, example in enumerate(examples, 1):
            formatted_examples.append(f"""
ПРИМЕР {i}:
Запрос: "{example['request']}"
Ответ: {example['response']}
""")
        
        return "\n".join(formatted_examples)
    
    @classmethod
    def get_similar_examples(cls, user_request: str, limit: int = 2) -> List[Dict[str, Any]]:
        """
        Поиск похожих примеров по ключевым словам
        
        Args:
            user_request: Запрос пользователя
            limit: Максимальное количество примеров
            
        Returns:
            Список похожих примеров
        """
        user_words = set(user_request.lower().split())
        scored_examples = []
        
        for example_key, example_data in cls.EXAMPLES.items():
            example_words = set(example_data["request"].lower().split())
            # Простая оценка схожести по пересечению слов
            similarity = len(user_words.intersection(example_words)) / len(user_words.union(example_words))
            
            if similarity > 0.1:  # Минимальный порог схожести
                scored_examples.append({
                    "key": example_key,
                    "request": example_data["request"],
                    "response": example_data["response"],
                    "intent_type": example_data["intent_type"],
                    "similarity": similarity
                })
        
        # Сортируем по схожести и возвращаем топ результаты
        scored_examples.sort(key=lambda x: x["similarity"], reverse=True)
        return scored_examples[:limit]
    
    @classmethod
    def get_statistics(cls) -> Dict[str, Any]:
        """Получение статистики примеров"""
        intent_counts = {}
        
        for example_data in cls.EXAMPLES.values():
            intent_type = example_data.get("intent_type", "unknown")
            intent_counts[intent_type] = intent_counts.get(intent_type, 0) + 1
        
        return {
            "total_examples": len(cls.EXAMPLES),
            "intent_distribution": intent_counts,
            "available_intents": list(intent_counts.keys())
        }


class ExampleSelector:
    """Селектор примеров для улучшения AI генерации"""
    
    def __init__(self):
        self.examples = AIExamples()
    
    def select_best_examples(self, user_request: str, intent_type: str, limit: int = 2) -> str:
        """
        Выбор лучших примеров для конкретного запроса
        
        Args:
            user_request: Запрос пользователя
            intent_type: Определенный тип намерения
            limit: Количество примеров
            
        Returns:
            Отформатированные примеры для промпта
        """
        # Сначала ищем примеры по типу намерения
        intent_examples = self.examples.get_examples_for_intent(intent_type, limit)
        
        # Если примеров мало, дополняем похожими
        if len(intent_examples) < limit:
            similar_examples = self.examples.get_similar_examples(user_request, limit - len(intent_examples))
            
            # Добавляем похожие примеры, избегая дубликатов
            existing_keys = {ex.get("key") for ex in intent_examples}
            for similar in similar_examples:
                if similar["key"] not in existing_keys:
                    intent_examples.append(similar)
        
        # Форматируем для промпта
        if not intent_examples:
            return "Подходящие примеры не найдены"
        
        formatted = ["ПРИМЕРЫ ХОРОШИХ МАКРОСОВ:"]
        for i, example in enumerate(intent_examples[:limit], 1):
            formatted.append(f"""
ПРИМЕР {i}:
Запрос пользователя: "{example['request']}"
Правильный ответ: {example['response']}
""")
        
        formatted.append("Создай макрос в таком же стиле и формате.")
        return "\n".join(formatted)
    
    def get_context_examples(self, context: Dict[str, Any]) -> str:
        """Получение примеров на основе контекста"""
        intent_type = context.get("intent_type", "mixed_automation")
        user_request = context.get("user_request", "")
        
        return self.select_best_examples(user_request, intent_type, 2)
