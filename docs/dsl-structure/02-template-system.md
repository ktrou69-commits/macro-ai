# 🖼️ Система шаблонов - Детальный анализ

## 📋 Содержание
1. [Обзор системы шаблонов](#обзор-системы-шаблонов)
2. [Структура и организация](#структура-и-организация)
3. [Алгоритм построения карты](#алгоритм-построения-карты)
4. [Именование и сокращения](#именование-и-сокращения)
5. [Интеграция с DSL](#интеграция-с-dsl)

## 🎯 Обзор системы шаблонов

Система шаблонов в Macro AI - это основа для визуального распознавания элементов интерфейса. Она позволяет:

- **🔍 Находить элементы** по изображениям на экране
- **📝 Использовать короткие имена** в DSL коде
- **🔄 Автоматически сопоставлять** различные варианты названий
- **⚡ Оптимизировать поиск** через кэширование

## 📁 Структура и организация

### **Иерархия папок templates/**
```
templates/
├── Chrome-TikTok-like-btn.png          # Кнопка лайка TikTok
├── Chrome-TikTok-comment-btn.png       # Кнопка комментария TikTok
├── Chrome-TikTok-share-btn.png         # Кнопка поделиться TikTok
├── Chrome-YouTube-like-btn.png         # Кнопка лайка YouTube
├── Chrome-YouTube-search.png           # Поиск YouTube
├── Chrome-YouTube-video.png            # Видео на YouTube
├── Atlas-ChromeNewTab.png              # Новая вкладка Chrome
├── Atlas-ChromeAddressBar.png          # Адресная строка Chrome
└── ...
```

### **Соглашения об именовании**
```
Формат: [Префикс]-[Платформа]-[Элемент]-[Тип].png

Примеры:
Chrome-TikTok-like-btn.png    → Браузер Chrome, платформа TikTok, кнопка лайка
Chrome-YouTube-search.png     → Браузер Chrome, платформа YouTube, поиск
Atlas-ChromeNewTab.png        → Системный (Atlas), новая вкладка Chrome
```

### **Типы префиксов**
```python
PREFIXES = {
    "Chrome-": "Элементы в браузере Chrome",
    "Atlas-": "Системные элементы macOS/Chrome",
    "Safari-": "Элементы в браузере Safari",
    "System-": "Системные элементы macOS"
}
```

## 🔧 Алгоритм построения карты

### **Метод `_build_template_map()`**
```python
def _build_template_map(self) -> Dict[str, str]:
    """
    Строит карту коротких имен → полные пути к шаблонам
    
    Процесс:
    1. Сканирует templates/ рекурсивно
    2. Находит все .png файлы  
    3. Создает множественные варианты имен
    4. Сохраняет в карту для быстрого доступа
    """
    template_map = {}
    
    # Сканируем все .png файлы
    templates_dir = Path(self.templates_base_path)
    for png_file in templates_dir.rglob("*.png"):
        full_path = str(png_file)
        short_name = png_file.stem  # Имя без расширения
        
        # Создаем варианты имен
        variants = self._generate_name_variants(short_name)
        
        # Сохраняем все варианты
        for variant in variants:
            template_map[variant] = full_path
    
    return template_map
```

### **Генерация вариантов имен**
```python
def _generate_name_variants(self, original_name: str) -> List[str]:
    """
    Генерирует все возможные варианты имени для шаблона
    
    Пример для "Chrome-TikTok-like-btn.png":
    - Chrome-TikTok-like-btn    (оригинал)
    - TikTok-like-btn          (без Chrome-)
    - like-btn                 (без Chrome-TikTok-)
    - like                     (без -btn)
    - like_btn                 (дефисы → подчеркивания)
    - TikTokLike               (CamelCase)
    """
    variants = [original_name]  # Оригинальное имя
    clean_name = original_name
    
    # Убираем префиксы
    prefixes_to_remove = [
        "Chrome-TikTok-", "Chrome-YouTube-", "Chrome-Instagram-",
        "Chrome-", "Atlas-", "Safari-", "System-"
    ]
    
    for prefix in prefixes_to_remove:
        if clean_name.startswith(prefix):
            clean_name = clean_name[len(prefix):]
            variants.append(clean_name)
            break
    
    # Убираем суффиксы
    suffixes_to_remove = ["-btn", "_btn", "-button", "_button"]
    for suffix in suffixes_to_remove:
        if clean_name.endswith(suffix):
            short_name = clean_name[:-len(suffix)]
            variants.append(short_name)
    
    # Варианты с заменой символов
    for variant in variants.copy():
        # Дефисы → подчеркивания
        if "-" in variant:
            variants.append(variant.replace("-", "_"))
        
        # CamelCase версия
        camel_case = "".join(word.capitalize() for word in variant.split("-"))
        if camel_case != variant:
            variants.append(camel_case)
    
    return list(set(variants))  # Убираем дубликаты
```

## 📝 Именование и сокращения

### **Примеры преобразований имен**

#### **TikTok элементы:**
```python
# Оригинал: Chrome-TikTok-like-btn.png
template_map = {
    "Chrome-TikTok-like-btn": "templates/Chrome-TikTok-like-btn.png",
    "TikTok-like-btn": "templates/Chrome-TikTok-like-btn.png",
    "like-btn": "templates/Chrome-TikTok-like-btn.png",
    "like": "templates/Chrome-TikTok-like-btn.png",
    "like_btn": "templates/Chrome-TikTok-like-btn.png",
    "TikTokLike": "templates/Chrome-TikTok-like-btn.png"
}
```

#### **YouTube элементы:**
```python
# Оригинал: Chrome-YouTube-search.png
template_map = {
    "Chrome-YouTube-search": "templates/Chrome-YouTube-search.png",
    "YouTube-search": "templates/Chrome-YouTube-search.png", 
    "search": "templates/Chrome-YouTube-search.png",
    "youtube_search": "templates/Chrome-YouTube-search.png",
    "YouTubeSearch": "templates/Chrome-YouTube-search.png"
}
```

#### **Системные элементы:**
```python
# Оригинал: Atlas-ChromeNewTab.png
template_map = {
    "Atlas-ChromeNewTab": "templates/Atlas-ChromeNewTab.png",
    "ChromeNewTab": "templates/Atlas-ChromeNewTab.png",
    "NewTab": "templates/Atlas-ChromeNewTab.png",
    "chrome_new_tab": "templates/Atlas-ChromeNewTab.png"
}
```

### **Приоритет разрешения имен**
```python
# При конфликте имен используется приоритет:
PRIORITY_ORDER = [
    "точное_совпадение",      # Полное имя файла
    "без_префикса",           # Имя без Chrome-/Atlas-
    "без_суффикса",           # Имя без -btn/-button
    "camel_case",             # CamelCase версия
    "underscore_version"      # С подчеркиваниями
]
```

## 🔗 Интеграция с DSL

### **Использование шаблонов в DSL коде**
```atlas
# Все эти варианты ссылаются на один файл:
click Chrome-TikTok-like-btn    # Полное имя
click TikTok-like-btn          # Без префикса Chrome-
click like-btn                 # Короткое имя
click like                     # Самое короткое
click TikTokLike              # CamelCase
```

### **Парсинг команды `click` в YAML**
```python
def _parse_click_command(self, line: str) -> Dict[str, Any]:
    """
    Парсит команду click и находит соответствующий шаблон
    
    Процесс:
    1. Извлекает имя элемента из команды
    2. Ищет в template_map
    3. Если найден → создает click_template команду
    4. Если не найден → ошибка или fallback
    """
    # Извлекаем имя элемента
    match = re.match(r'click\s+(.+)', line.strip())
    if not match:
        return None
    
    element_name = match.group(1).strip()
    
    # Ищем в карте шаблонов
    template_path = self.template_map.get(element_name)
    
    if template_path:
        return {
            'action': 'click_template',
            'template': template_path,
            'confidence': 0.8,
            'timeout': 10,
            'original_name': element_name
        }
    else:
        # Шаблон не найден
        print(f"⚠️ Шаблон '{element_name}' не найден")
        return {
            'action': 'error',
            'message': f"Template '{element_name}' not found",
            'available_templates': list(self.template_map.keys())[:10]
        }
```

### **Генерируемый YAML для шаблонов**
```yaml
# DSL команда: click like-btn
# Генерируется:
- action: click_template
  template: "templates/Chrome-TikTok-like-btn.png"
  confidence: 0.8          # Минимальная уверенность распознавания
  timeout: 10              # Таймаут поиска в секундах
  original_name: "like-btn" # Исходное имя из DSL
  method: "opencv"         # Метод поиска (opencv/yolo)
  
# При ошибке:
- action: error
  message: "Template 'unknown-btn' not found"
  available_templates: ["like-btn", "comment-btn", "share-btn", ...]
```

## 📊 Статистика и оптимизация

### **Кэширование шаблонов**
```python
class AtlasDSLParser:
    def __init__(self):
        # Кэш для оптимизации
        self._templates_cache = {}
        
    def get_template_info(self, template_name: str) -> Dict:
        """Получение информации о шаблоне с кэшированием"""
        if template_name in self._templates_cache:
            return self._templates_cache[template_name]
        
        # Загружаем и кэшируем
        template_info = self._load_template_info(template_name)
        self._templates_cache[template_name] = template_info
        return template_info
```

### **Статистика использования**
```python
# При инициализации выводится статистика:
print(f"✅ Загружено {len(template_map)} шаблонов")
print(f"📁 Найдено {png_count} .png файлов")
print(f"🔗 Создано {variants_count} вариантов имен")

# Примеры вывода:
# ✅ Загружено 156 шаблонов
# 📁 Найдено 52 .png файлов  
# 🔗 Создано 312 вариантов имен
```

### **Диагностика конфликтов имен**
```python
def _check_name_conflicts(self, template_map: Dict[str, str]):
    """Проверка конфликтов в именах шаблонов"""
    conflicts = {}
    
    for name, path in template_map.items():
        if name in conflicts:
            print(f"⚠️ Конфликт имени '{name}':")
            print(f"   {conflicts[name]}")
            print(f"   {path}")
        else:
            conflicts[name] = path
```

## 🎯 Лучшие практики

### **✅ Рекомендации по именованию файлов**
```
1. Используйте описательные имена:
   ✅ Chrome-TikTok-like-btn.png
   ❌ btn1.png

2. Следуйте соглашениям:
   ✅ [Браузер]-[Платформа]-[Элемент]-[Тип].png
   ❌ random_naming.png

3. Избегайте специальных символов:
   ✅ Chrome-YouTube-search.png  
   ❌ Chrome@YouTube#search$.png
```

### **🔧 Оптимизация производительности**
```python
# Предзагрузка часто используемых шаблонов
FREQUENTLY_USED = [
    "like-btn", "comment-btn", "share-btn",
    "search", "video", "ChromeNewTab"
]

def preload_templates(self):
    """Предзагрузка популярных шаблонов"""
    for template_name in FREQUENTLY_USED:
        if template_name in self.template_map:
            self._templates_cache[template_name] = self._load_template_info(template_name)
```

### **🛡️ Обработка ошибок**
```python
def safe_template_lookup(self, name: str) -> Optional[str]:
    """Безопасный поиск шаблона с предложениями"""
    # Точное совпадение
    if name in self.template_map:
        return self.template_map[name]
    
    # Поиск похожих имен
    similar = self._find_similar_names(name)
    if similar:
        print(f"💡 Возможно вы имели в виду: {', '.join(similar[:3])}")
    
    return None

def _find_similar_names(self, name: str) -> List[str]:
    """Поиск похожих имен шаблонов"""
    import difflib
    return difflib.get_close_matches(name, self.template_map.keys(), n=5, cutoff=0.6)
```

---

**Следующие разделы:**
- [03-variable-system.md](03-variable-system.md) - Система переменных DSL
- [04-yaml-generation.md](04-yaml-generation.md) - Генерация выполнимого YAML
