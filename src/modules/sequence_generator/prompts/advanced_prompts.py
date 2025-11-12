"""
Продвинутые AI промпты для генерации сложных многошаговых макросов
"""

from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class AdvancedPrompts:
    """Коллекция продвинутых промптов для сложных макросов"""
    
    PROMPTS = {
        "complex_macro": """
Ты эксперт по созданию сложных многошаговых макросов автоматизации с условной логикой, циклами и переменными.

РАСШИРЕННЫЕ DSL КОМАНДЫ:

УСЛОВНАЯ ЛОГИКА:
- if element_exists "selector" ... else ... endif
- if page_contains "text" ... else ... endif  
- if element_visible "selector" ... else ... endif
- if $variable == "value" ... else ... endif

ЦИКЛЫ:
- repeat N times ... end_repeat
- while condition ... end_while
- for_each "selector" as variable ... end_for

ПЕРЕМЕННЫЕ:
- set variable_name = "value"
- param parameter_name = "default_value"
- Использование: $variable_name

УПРАВЛЕНИЕ ПОТОКОМ:
- break (выход из цикла)
- continue (следующая итерация)

ПРИМЕРЫ СЛОЖНЫХ МАКРОСОВ:

1. УСЛОВНАЯ ОБРАБОТКА ДАННЫХ:
```atlas
param search_term = "Python"
param max_results = 5

navigate "https://google.com"
wait 2s
type_in_field "//input[@name='q']" $search_term
press enter
wait 3s

set result_count = 0
for_each "//div[@class='g']" as result
    if element_exists result + "//h3"
        click result + "//h3//a"
        wait 2s
        
        if page_contains "404" or page_contains "Error"
            navigate_back
            continue
        endif
        
        set result_count = $result_count + 1
        
        if $result_count >= $max_results
            break
        endif
        
        navigate_back
        wait 1s
    endif
end_for
```

2. ЦИКЛИЧЕСКАЯ ОБРАБОТКА С ПРОВЕРКАМИ:
```atlas
param max_attempts = 3
set attempt = 0

while $attempt < $max_attempts
    set attempt = $attempt + 1
    
    click "//button[@id='load-more']"
    wait 3s
    
    if element_exists "//div[@class='error']"
        if $attempt < $max_attempts
            click "//button[@id='retry']"
            wait 5s
            continue
        else
            type "Max attempts reached, stopping"
            break
        endif
    endif
    
    if page_contains "No more items"
        type "All items loaded successfully"
        break
    endif
end_while
```

3. КОМПЛЕКСНАЯ АВТОМАТИЗАЦИЯ ФОРМЫ:
```atlas
param user_data = {
    "name": "John Doe",
    "email": "john@example.com", 
    "phone": "+1234567890"
}

# Заполнение формы с проверками
for_each "//form//input[@required]" as field
    set field_name = get_attribute(field, "name")
    
    if $field_name == "name"
        type_in_field field $user_data.name
    else if $field_name == "email"
        type_in_field field $user_data.email
    else if $field_name == "phone"
        type_in_field field $user_data.phone
    endif
    
    # Проверка валидации поля
    if element_exists field + "[aria-invalid='true']"
        type "Field validation failed for: " + $field_name
        continue
    endif
end_for

# Отправка формы
if element_exists "//button[@type='submit']:not([disabled])"
    click "//button[@type='submit']"
    wait 3s
    
    if page_contains "Success" or page_contains "Thank you"
        type "Form submitted successfully"
    else
        type "Form submission failed"
    endif
endif
```

КОНТЕКСТ: {context}
ПОЛЬЗОВАТЕЛЬСКИЙ ЗАПРОС: {user_request}

Создай СЛОЖНЫЙ многошаговый макрос, используя:
- Условную логику для обработки разных сценариев
- Циклы для повторяющихся действий
- Переменные для хранения данных
- Проверки ошибок и обработку исключений
- Логирование важных событий

ФОРМАТ ОТВЕТА:
НАЗВАНИЕ: [Краткое название макроса]

DSL КОД:
```atlas
# Подробные комментарии к логике
[Сложный DSL код с условиями, циклами и переменными]
```

ОПИСАНИЕ: [Подробное описание логики макроса и его возможностей]
""",

        "data_processing": """
Создай макрос для обработки данных с использованием циклов и условий.

СПЕЦИАЛИЗАЦИЯ: Обработка списков, таблиц, форм с множественными элементами.

ДОСТУПНЫЕ ПАТТЕРНЫ:
- Итерация по элементам списка
- Условная обработка каждого элемента
- Накопление результатов в переменных
- Обработка ошибок и пропуск проблемных элементов

ПРИМЕР ПАТТЕРНА:
```atlas
set processed_count = 0
set error_count = 0

for_each "//table//tr[position()>1]" as row
    if element_exists row + "//td[@class='data']"
        set data_value = get_text(row + "//td[@class='data']")
        
        if $data_value != ""
            # Обработка данных
            click row + "//button[@class='process']"
            wait 2s
            
            if element_exists "//div[@class='success']"
                set processed_count = $processed_count + 1
            else
                set error_count = $error_count + 1
            endif
        endif
    endif
end_for

type "Processed: " + $processed_count + ", Errors: " + $error_count
```

ЗАДАЧА: {user_request}
""",

        "workflow_automation": """
Создай макрос для автоматизации рабочего процесса с множественными шагами.

СПЕЦИАЛИЗАЦИЯ: Бизнес-процессы, последовательности действий с проверками.

ДОСТУПНЫЕ ПАТТЕРНЫ:
- Пошаговое выполнение с проверками
- Откат к предыдущему шагу при ошибке
- Условные ветвления в зависимости от результата
- Логирование прогресса

ПРИМЕР ПАТТЕРНА:
```atlas
param workflow_steps = ["login", "navigate", "process", "verify", "logout"]
set current_step = 0

for_each $workflow_steps as step
    set current_step = $current_step + 1
    type "Executing step " + $current_step + ": " + $step
    
    if $step == "login"
        # Логика входа
        if not element_exists "//div[@class='user-menu']"
            type "Login failed, retrying..."
            continue
        endif
    else if $step == "process"
        # Основная обработка
        repeat 3 times
            if element_exists "//button[@id='process']"
                click "//button[@id='process']"
                wait 5s
                
                if page_contains "Success"
                    break
                endif
            endif
        end_repeat
    endif
    
    type "Step " + $step + " completed"
end_for
```

ЗАДАЧА: {user_request}
""",

        "error_handling": """
Создай макрос с продвинутой обработкой ошибок и восстановлением.

СПЕЦИАЛИЗАЦИЯ: Надежные макросы с обработкой сбоев.

ДОСТУПНЫЕ ПАТТЕРНЫ:
- Try-catch эмуляция через условия
- Повторные попытки с экспоненциальной задержкой
- Graceful degradation при ошибках
- Детальное логирование ошибок

ПРИМЕР ПАТТЕРНА:
```atlas
param max_retries = 3
set retry_count = 0
set success = false

while $retry_count < $max_retries and not $success
    set retry_count = $retry_count + 1
    type "Attempt " + $retry_count + " of " + $max_retries
    
    # Основное действие
    click "//button[@id='action']"
    wait 2s
    
    if element_exists "//div[@class='error']"
        set error_message = get_text("//div[@class='error']")
        type "Error occurred: " + $error_message
        
        # Экспоненциальная задержка
        set delay = $retry_count * 2
        wait $delay + "s"
        
        # Попытка восстановления
        if element_exists "//button[@id='reset']"
            click "//button[@id='reset']"
            wait 1s
        endif
    else
        set success = true
        type "Action completed successfully"
    endif
end_while

if not $success
    type "Failed after " + $max_retries + " attempts"
endif
```

ЗАДАЧА: {user_request}
"""
    }
    
    EXAMPLES = {
        "e_commerce_automation": {
            "request": "автоматизируй процесс покупки товаров в интернет-магазине с проверкой наличия и сравнением цен",
            "response": """
НАЗВАНИЕ: Автоматизация покупки с проверкой цен

DSL КОД:
```atlas
# Параметры для автоматизации покупки
param product_list = ["iPhone 15", "MacBook Pro", "AirPods"]
param max_price = 1000
param preferred_stores = ["store1.com", "store2.com", "store3.com"]

set total_saved = 0
set purchased_items = 0

# Обработка каждого товара
for_each $product_list as product
    type "Searching for: " + $product
    set best_price = 99999
    set best_store = ""
    
    # Сравнение цен в разных магазинах
    for_each $preferred_stores as store
        navigate "https://" + $store + "/search"
        wait 2s
        
        type_in_field "//input[@name='search']" $product
        press enter
        wait 3s
        
        if element_exists "//div[@class='product-item'][1]"
            set current_price = get_text("//div[@class='product-item'][1]//span[@class='price']")
            
            if $current_price < $best_price and $current_price <= $max_price
                set best_price = $current_price
                set best_store = $store
            endif
        endif
    end_for
    
    # Покупка по лучшей цене
    if $best_store != ""
        navigate "https://" + $best_store + "/search"
        wait 2s
        
        type_in_field "//input[@name='search']" $product
        press enter
        wait 3s
        
        click "//div[@class='product-item'][1]//button[@class='add-to-cart']"
        wait 2s
        
        if element_exists "//div[@class='cart-success']"
            set purchased_items = $purchased_items + 1
            set saved_amount = $max_price - $best_price
            set total_saved = $total_saved + $saved_amount
            
            type "Purchased " + $product + " for $" + $best_price + " (saved $" + $saved_amount + ")"
        else
            type "Failed to add " + $product + " to cart"
        endif
    else
        type "No suitable offer found for " + $product + " within budget"
    endif
end_for

# Финальный отчет
type "Purchase complete: " + $purchased_items + " items bought"
type "Total saved: $" + $total_saved
```

ОПИСАНИЕ: Макрос автоматизирует процесс покупки товаров с умным сравнением цен. Для каждого товара из списка он проверяет цены в нескольких магазинах, выбирает лучшее предложение в рамках бюджета и автоматически добавляет товар в корзину. Включает обработку ошибок и подробную отчетность о сэкономленных средствах.
"""
        },
        
        "social_media_management": {
            "request": "создай макрос для автоматического постинга контента в социальные сети с проверкой лимитов и планированием",
            "response": """
НАЗВАНИЕ: Умное управление социальными сетями

DSL КОД:
```atlas
# Конфигурация для постинга
param social_networks = ["twitter", "facebook", "linkedin"]
param post_content = "Exciting news about our new product launch! #innovation #tech"
param max_posts_per_day = 3
param posting_interval = 2  # часы между постами

set posts_made = 0
set failed_posts = 0

# Проверка лимитов для каждой сети
for_each $social_networks as network
    type "Processing " + $network
    
    # Переход на платформу
    if $network == "twitter"
        navigate "https://twitter.com/compose/tweet"
    else if $network == "facebook"
        navigate "https://facebook.com"
        click "//div[@data-testid='status-attachment-mentions-input']"
    else if $network == "linkedin"
        navigate "https://linkedin.com/feed"
        click "//button[@aria-label='Start a post']"
    endif
    
    wait 3s
    
    # Проверка авторизации
    if element_exists "//input[@name='session[username_or_email]']" or element_exists "//input[@name='email']"
        type "Not logged in to " + $network + ", skipping..."
        continue
    endif
    
    # Проверка дневного лимита постов
    if element_exists "//div[contains(text(), 'daily limit')]"
        type "Daily posting limit reached for " + $network
        continue
    endif
    
    # Создание поста
    if element_exists "//textarea" or element_exists "//div[@contenteditable='true']"
        # Адаптация контента под платформу
        set adapted_content = $post_content
        
        if $network == "twitter"
            # Ограничение для Twitter
            if length($adapted_content) > 280
                set adapted_content = substring($adapted_content, 0, 277) + "..."
            endif
        else if $network == "linkedin"
            # Добавление профессионального тона
            set adapted_content = $adapted_content + " #professional #business"
        endif
        
        type_in_field "//textarea, //div[@contenteditable='true']" $adapted_content
        wait 2s
        
        # Публикация
        if element_exists "//button[contains(text(), 'Post')] | //button[contains(text(), 'Tweet')] | //button[contains(text(), 'Share')]"
            click "//button[contains(text(), 'Post')] | //button[contains(text(), 'Tweet')] | //button[contains(text(), 'Share')]"
            wait 3s
            
            # Проверка успешности
            if element_exists "//div[contains(text(), 'posted')] | //div[contains(text(), 'shared')]" or not element_exists "//div[@role='alert']"
                set posts_made = $posts_made + 1
                type "Successfully posted to " + $network
                
                # Пауза между постами
                if $posts_made < length($social_networks)
                    type "Waiting " + $posting_interval + " hours before next post..."
                    wait ($posting_interval * 3600) + "s"
                endif
            else
                set failed_posts = $failed_posts + 1
                type "Failed to post to " + $network
            endif
        else
            type "Post button not found on " + $network
            set failed_posts = $failed_posts + 1
        endif
    else
        type "Text input not found on " + $network
        set failed_posts = $failed_posts + 1
    endif
    
    # Проверка дневного лимита
    if $posts_made >= $max_posts_per_day
        type "Daily posting limit reached (" + $max_posts_per_day + " posts)"
        break
    endif
end_for

# Финальный отчет
type "Social media posting complete:"
type "- Successful posts: " + $posts_made
type "- Failed posts: " + $failed_posts
type "- Networks processed: " + length($social_networks)
```

ОПИСАНИЕ: Интеллектуальный макрос для управления социальными сетями, который автоматически адаптирует контент под каждую платформу, соблюдает лимиты постинга, проверяет авторизацию и обеспечивает равномерное распределение постов во времени. Включает обработку ошибок и детальную отчетность о результатах публикации.
"""
        }
    }
    
    @classmethod
    def get_advanced_prompt(cls, complexity_level: str, context: Dict[str, Any]) -> str:
        """
        Получение продвинутого промпта для сложных макросов
        
        Args:
            complexity_level: Уровень сложности (complex_macro, data_processing, workflow_automation, error_handling)
            context: Контекст для подстановки в промпт
            
        Returns:
            Сформированный промпт
        """
        if complexity_level not in cls.PROMPTS:
            complexity_level = "complex_macro"
        
        prompt_template = cls.PROMPTS[complexity_level]
        
        # Подставляем контекст
        try:
            formatted_prompt = prompt_template.format(**context)
            logger.info(f"Сформирован продвинутый промпт: {complexity_level}")
            return formatted_prompt
        except KeyError as e:
            logger.error(f"Отсутствует ключ в контексте: {e}")
            # Возвращаем базовый промпт
            return cls.PROMPTS["complex_macro"].format(
                context="Контекст недоступен",
                user_request=context.get("user_request", "Неизвестная задача")
            )
    
    @classmethod
    def get_examples_for_complexity(cls, complexity_level: str) -> List[Dict[str, str]]:
        """Получение примеров для определенного уровня сложности"""
        # Возвращаем все примеры, так как они все демонстрируют сложные макросы
        return [
            {
                "key": key,
                "request": example["request"],
                "response": example["response"]
            }
            for key, example in cls.EXAMPLES.items()
        ]
    
    @classmethod
    def analyze_complexity_requirements(cls, user_request: str) -> str:
        """
        Анализ требований к сложности макроса
        
        Args:
            user_request: Запрос пользователя
            
        Returns:
            Рекомендуемый тип промпта
        """
        user_lower = user_request.lower()
        
        # Ключевые слова для определения типа сложности
        if any(word in user_lower for word in ["обработка данных", "таблица", "список", "массив", "итерация"]):
            return "data_processing"
        
        elif any(word in user_lower for word in ["процесс", "workflow", "последовательность", "этапы", "шаги"]):
            return "workflow_automation"
        
        elif any(word in user_lower for word in ["ошибка", "сбой", "восстановление", "retry", "надежность"]):
            return "error_handling"
        
        else:
            return "complex_macro"
    
    @classmethod
    def enhance_prompt_with_examples(cls, base_prompt: str, user_request: str) -> str:
        """Улучшение промпта добавлением релевантных примеров"""
        # Определяем наиболее подходящий пример
        user_lower = user_request.lower()
        
        selected_example = None
        if any(word in user_lower for word in ["покупка", "магазин", "товар", "цена"]):
            selected_example = cls.EXAMPLES["e_commerce_automation"]
        elif any(word in user_lower for word in ["пост", "социальные сети", "публикация"]):
            selected_example = cls.EXAMPLES["social_media_management"]
        
        if selected_example:
            example_text = f"""
ДОПОЛНИТЕЛЬНЫЙ ПРИМЕР СЛОЖНОГО МАКРОСА:

Запрос: "{selected_example['request']}"
Решение: {selected_example['response']}

Используй этот пример как вдохновение для создания своего макроса.
"""
            return base_prompt + example_text
        
        return base_prompt


class ComplexityAnalyzer:
    """Анализатор сложности запросов для выбора подходящего промпта"""
    
    COMPLEXITY_INDICATORS = {
        "high": [
            "условие", "если", "иначе", "цикл", "повтор", "для каждого",
            "проверка", "ошибка", "обработка", "множественный", "массив",
            "список", "таблица", "данные", "процесс", "workflow"
        ],
        "medium": [
            "последовательность", "шаги", "этапы", "несколько", "разные",
            "варианты", "опции", "выбор", "сравнение"
        ],
        "low": [
            "простой", "базовый", "открой", "кликни", "введи", "один"
        ]
    }
    
    @classmethod
    def analyze_request_complexity(cls, user_request: str) -> Dict[str, Any]:
        """
        Анализ сложности пользовательского запроса
        
        Args:
            user_request: Запрос пользователя
            
        Returns:
            Словарь с информацией о сложности
        """
        user_lower = user_request.lower()
        
        # Подсчет индикаторов сложности
        complexity_scores = {
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for level, indicators in cls.COMPLEXITY_INDICATORS.items():
            for indicator in indicators:
                if indicator in user_lower:
                    complexity_scores[level] += 1
        
        # Определение общего уровня сложности
        total_indicators = sum(complexity_scores.values())
        if total_indicators == 0:
            complexity_level = "medium"  # По умолчанию
        else:
            complexity_level = max(complexity_scores.keys(), key=lambda k: complexity_scores[k])
        
        # Рекомендации по типу промпта
        prompt_recommendations = {
            "high": "complex_macro",
            "medium": "workflow_automation", 
            "low": "basic_macro"  # Fallback к базовому промпту
        }
        
        return {
            "complexity_level": complexity_level,
            "complexity_scores": complexity_scores,
            "total_indicators": total_indicators,
            "recommended_prompt": prompt_recommendations.get(complexity_level, "complex_macro"),
            "requires_advanced_features": complexity_scores["high"] > 0
        }
