# 💾 Система переменных DSL - Детальный анализ

## 📋 Содержание
1. [Обзор системы переменных](#обзор-системы-переменных)
2. [Формат файлов переменных](#формат-файлов-переменных)
3. [Парсинг и загрузка](#парсинг-и-загрузка)
4. [Развертывание переменных](#развертывание-переменных)
5. [Параметризация](#параметризация)
6. [Интеграция с AI генератором](#интеграция-с-ai-генератором)

## 🎯 Обзор системы переменных

Система переменных DSL позволяет:

- **🔄 Переиспользовать** блоки кода в разных макросах
- **📝 Параметризовать** команды для гибкости
- **🤖 Создавать** переменные через AI генератор
- **⚡ Оптимизировать** размер и читаемость DSL кода

```
┌─────────────────────────────────────────────────────────────────┐
│                    СИСТЕМА ПЕРЕМЕННЫХ DSL                       │
├─────────────────────────────────────────────────────────────────┤
│  📄 ФАЙЛЫ ПЕРЕМЕННЫХ                                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ DSL_VARIABLES   │  │ USER_VARIABLES  │  │ AI Generated    │  │
│  │ (системные)     │  │ (пользователь.) │  │ (автоматич.)    │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  🔧 ПАРСЕР ПЕРЕМЕННЫХ                                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ Загрузка файлов │→ │ Парсинг формата │→ │ Извлечение      │  │
│  │ переменных      │  │ ${VarName}      │  │ параметров      │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  🔄 РАЗВЕРТЫВАНИЕ                                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ ${VarName}      │→ │ Подстановка     │→ │ DSL команды     │  │
│  │ в DSL коде      │  │ параметров      │  │ для выполнения  │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## 📄 Формат файлов переменных

### **Расположение файлов**
```
templates/DSL_VARIABLES.txt          # Системные переменные
dsl_references/USER_VARIABLES.txt    # Пользовательские переменные
```

### **Структура файла переменных**
```
${VariableName}
--------------------
DSL код
DSL код
...

${VariableWithParams:param1,param2}
--------------------
DSL код с {param1}
DSL код с {param2}
...

ИСПОЛЬЗОВАНИЕ:
${VariableName} - Описание переменной
${VariableWithParams:param1,param2} - Описание с параметрами

================================================================================
```

### **Пример реального файла**
```
${ChromeOpen}
--------------------
open ChromeApp
wait 2s
click ChromeNewTab
wait 1s

${TikTokLike}
--------------------
click TikTok-like-btn
wait 1s

${YouTubeSearch:query}
--------------------
click YouTube-search
wait 1s
type "{query}"
press enter
wait 3s

${TikTokComment:text,user}
--------------------
click TikTok-comment-btn
wait 1s
type "{text}"
wait 0.5s
type "@{user}"
wait 0.5s
press enter

${ChromeGoToSite:url}
--------------------
click ChromeAddressBar
wait 0.5s
key_combination cmd+a
wait 0.2s
type "{url}"
press enter
wait 3s

ИСПОЛЬЗОВАНИЕ:
${ChromeOpen} - Открыть Chrome и новую вкладку
${TikTokLike} - Поставить лайк на TikTok
${YouTubeSearch:query} - Найти видео на YouTube по запросу
${TikTokComment:text,user} - Оставить комментарий с упоминанием пользователя
${ChromeGoToSite:url} - Перейти на указанный сайт в Chrome

================================================================================
```

## 🔧 Парсинг и загрузка

### **Метод `_load_dsl_variables()`**
```python
def _load_dsl_variables(self) -> Dict[str, Dict[str, str]]:
    """
    Загружает DSL переменные из файлов
    
    Returns:
        Dict в формате:
        {
            'ChromeOpen': {
                'code': 'open ChromeApp\nwait 2s\nclick ChromeNewTab\nwait 1s',
                'params': []
            },
            'YouTubeSearch': {
                'code': 'click YouTube-search\nwait 1s\ntype "{query}"\npress enter\nwait 3s',
                'params': ['query']
            }
        }
    """
    variables = {}
    
    # Файлы для загрузки
    var_files = [
        Path(self.templates_base_path) / 'DSL_VARIABLES.txt',
        Path('dsl_references') / 'USER_VARIABLES.txt'
    ]
    
    for var_file in var_files:
        if var_file.exists():
            variables.update(self._parse_variable_file(var_file))
    
    return variables
```

### **Парсинг файла переменных**
```python
def _parse_variable_file(self, var_file: Path) -> Dict[str, Dict]:
    """Парсит один файл переменных"""
    variables = {}
    
    with open(var_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Состояние парсера
    current_var = None
    current_code = []
    in_code_section = False
    
    for line in content.split('\n'):
        line_stripped = line.strip()
        
        # Начало новой переменной: ${...}
        if line_stripped.startswith('${') and line_stripped.endswith('}'):
            # Сохраняем предыдущую переменную
            if current_var and current_code:
                variables[current_var] = self._process_variable_code(current_code)
            
            # Парсим новую переменную
            var_declaration = line_stripped[2:-1]  # Убираем ${ и }
            current_var, params = self._parse_variable_declaration(var_declaration)
            current_code = []
            in_code_section = False
        
        # Разделитель кода (----)
        elif line_stripped.startswith('---'):
            in_code_section = True
        
        # Конец секции кода
        elif line_stripped.startswith('ИСПОЛЬЗОВАНИЕ:') or \
             line_stripped.startswith('================'):
            in_code_section = False
        
        # Код переменной
        elif in_code_section and current_var:
            # Пропускаем комментарии в начале
            if line_stripped and not line_stripped.startswith('#'):
                current_code.append(line)
            elif current_code:  # Добавляем пустые строки только если уже есть код
                current_code.append(line)
    
    # Сохраняем последнюю переменную
    if current_var and current_code:
        variables[current_var] = self._process_variable_code(current_code)
    
    return variables
```

### **Парсинг объявления переменной**
```python
def _parse_variable_declaration(self, declaration: str) -> Tuple[str, List[str]]:
    """
    Парсит объявление переменной
    
    Примеры:
    'ChromeOpen' → ('ChromeOpen', [])
    'YouTubeSearch:query' → ('YouTubeSearch', ['query'])
    'TikTokComment:text,user' → ('TikTokComment', ['text', 'user'])
    """
    if ':' in declaration:
        var_name, params_str = declaration.split(':', 1)
        params = [p.strip() for p in params_str.split(',')]
        return var_name.strip(), params
    else:
        return declaration.strip(), []
```

### **Обработка кода переменной**
```python
def _process_variable_code(self, code_lines: List[str]) -> Dict[str, Any]:
    """
    Обрабатывает код переменной и извлекает параметры
    
    Returns:
        {
            'code': 'clean_code_text',
            'params': ['extracted_params'],
            'line_count': number_of_lines
        }
    """
    # Очищаем код от лишних пустых строк
    clean_code = '\n'.join(code_lines).strip()
    
    # Извлекаем параметры из кода (например {query}, {text})
    import re
    params = re.findall(r'\{(\w+)\}', clean_code)
    unique_params = list(set(params))
    
    return {
        'code': clean_code,
        'params': unique_params,
        'line_count': len([line for line in code_lines if line.strip()])
    }
```

## 🔄 Развертывание переменных

### **Обнаружение переменных в DSL**
```python
def _parse_line(self, line: str) -> Dict[str, Any]:
    """
    Парсит строку DSL и обнаруживает переменные
    
    Примеры:
    '${ChromeOpen}' → expand_variable
    '${YouTubeSearch:query="Python"}' → expand_variable с параметрами
    'click like-btn' → обычная команда
    """
    line_stripped = line.strip()
    
    # Проверяем, является ли строка переменной
    if line_stripped.startswith('${') and '}' in line_stripped:
        return self._parse_variable_usage(line_stripped)
    
    # Обычная DSL команда
    return self._parse_regular_command(line_stripped)
```

### **Парсинг использования переменной**
```python
def _parse_variable_usage(self, line: str) -> Dict[str, Any]:
    """
    Парсит использование переменной в DSL
    
    Форматы:
    ${VarName}                           # Без параметров
    ${VarName:param="value"}             # Один параметр
    ${VarName:param1="val1",param2="val2"} # Несколько параметров
    """
    import re
    
    # Извлекаем имя переменной и параметры
    match = re.match(r'\$\{([^:}]+)(?::([^}]+))?\}', line)
    if not match:
        return {'action': 'error', 'message': f'Invalid variable syntax: {line}'}
    
    var_name = match.group(1)
    params_str = match.group(2) or ''
    
    # Парсим параметры
    params = self._parse_variable_params(params_str)
    
    return {
        'action': 'expand_variable',
        'variable': var_name,
        'params': params,
        'original_line': line
    }
```

### **Парсинг параметров переменной**
```python
def _parse_variable_params(self, params_str: str) -> Dict[str, str]:
    """
    Парсит параметры переменной
    
    Примеры:
    'query="Python tutorial"' → {'query': 'Python tutorial'}
    'text="Hello",user="john"' → {'text': 'Hello', 'user': 'john'}
    'url="https://google.com"' → {'url': 'https://google.com'}
    """
    params = {}
    
    if not params_str.strip():
        return params
    
    # Регулярное выражение для парсинга параметров
    import re
    param_pattern = r'(\w+)=(["\']?)([^"\'=,]+)\2'
    
    for match in re.finditer(param_pattern, params_str):
        param_name = match.group(1)
        param_value = match.group(3)
        params[param_name] = param_value
    
    return params
```

### **Развертывание переменной в DSL команды**
```python
def _expand_variable(self, var_name: str, var_params: Dict[str, str]) -> List[str]:
    """
    Разворачивает переменную в список DSL команд
    
    Процесс:
    1. Находит переменную в загруженных переменных
    2. Подставляет параметры в код
    3. Возвращает список строк DSL кода
    """
    if var_name not in self.variables:
        print(f"⚠️ Переменная ${{{var_name}}} не найдена")
        return []
    
    var_data = self.variables[var_name]
    code = var_data['code']
    expected_params = var_data['params']
    
    # Проверяем, что все необходимые параметры переданы
    missing_params = set(expected_params) - set(var_params.keys())
    if missing_params:
        print(f"⚠️ Отсутствуют параметры для ${{{var_name}}}: {missing_params}")
        return []
    
    # Подставляем параметры в код
    expanded_code = self._substitute_parameters(code, var_params)
    
    # Разбиваем на строки
    lines = expanded_code.split('\n')
    return [line for line in lines if line.strip()]
```

### **Подстановка параметров**
```python
def _substitute_parameters(self, code: str, params: Dict[str, str]) -> str:
    """
    Подставляет параметры в код переменной
    
    Пример:
    code = 'type "{query}"\nwait 1s'
    params = {'query': 'Python tutorial'}
    result = 'type "Python tutorial"\nwait 1s'
    """
    result = code
    
    for param_name, param_value in params.items():
        # Заменяем {param_name} на param_value
        placeholder = f'{{{param_name}}}'
        result = result.replace(placeholder, param_value)
    
    return result
```

## 📝 Параметризация

### **Типы параметров**

#### **1. Текстовые параметры**
```atlas
# Переменная:
${YouTubeSearch:query}
--------------------
click YouTube-search
wait 1s
type "{query}"
press enter
wait 3s

# Использование:
${YouTubeSearch:query="Python tutorial"}
${YouTubeSearch:query="Machine Learning"}
```

#### **2. URL параметры**
```atlas
# Переменная:
${ChromeGoToSite:url}
--------------------
click ChromeAddressBar
wait 0.5s
key_combination cmd+a
type "{url}"
press enter
wait 3s

# Использование:
${ChromeGoToSite:url="https://github.com"}
${ChromeGoToSite:url="https://stackoverflow.com"}
```

#### **3. Множественные параметры**
```atlas
# Переменная:
${TikTokComment:text,user}
--------------------
click TikTok-comment-btn
wait 1s
type "{text}"
wait 0.5s
type "@{user}"
press enter

# Использование:
${TikTokComment:text="Great video!",user="johndoe"}
${TikTokComment:text="Amazing content",user="creator123"}
```

### **Валидация параметров**
```python
def _validate_variable_params(self, var_name: str, provided_params: Dict[str, str]) -> bool:
    """
    Валидирует параметры переменной
    
    Проверки:
    1. Все обязательные параметры переданы
    2. Нет лишних параметров
    3. Параметры не пустые
    """
    if var_name not in self.variables:
        return False
    
    expected_params = set(self.variables[var_name]['params'])
    provided_params_set = set(provided_params.keys())
    
    # Проверяем отсутствующие параметры
    missing = expected_params - provided_params_set
    if missing:
        print(f"❌ Отсутствуют параметры: {missing}")
        return False
    
    # Проверяем лишние параметры
    extra = provided_params_set - expected_params
    if extra:
        print(f"⚠️ Лишние параметры: {extra}")
    
    # Проверяем пустые значения
    empty_params = [k for k, v in provided_params.items() if not v.strip()]
    if empty_params:
        print(f"❌ Пустые параметры: {empty_params}")
        return False
    
    return True
```

## 🤖 Интеграция с AI генератором

### **Создание переменных через AI**
```python
# В menu_ai_generator() после генерации DSL:
if save_as_var == 'y':
    from src.ai.variable_generator import AIVariableGenerator
    var_generator = AIVariableGenerator(self.project_root)
    
    # AI анализирует DSL код и создает переменную
    variable = var_generator.generate_variable(user_input, dsl_code)
    
    # Предлагает название
    print(f"💡 Предлагаемое название: ${{{variable['name']}}}")
    custom_name = input("Или введите свое: ").strip()
    
    if custom_name:
        variable['name'] = custom_name
    
    # Сохраняет в USER_VARIABLES.txt
    var_generator.save_variable(variable)
```

### **Формат AI-генерируемых переменных**
```python
# AIVariableGenerator создает переменные в формате:
{
    'name': 'YouTubeLikeVideo',
    'description': 'Открыть YouTube и поставить лайк на видео',
    'code': 'open ChromeApp\nwait 2s\nclick ChromeNewTab\n...',
    'params': ['video_query'],
    'usage_example': '${YouTubeLikeVideo:video_query="Python tutorial"}'
}
```

### **Автоматическое обнаружение параметров**
```python
def extract_parameters_from_code(self, dsl_code: str) -> List[str]:
    """
    AI анализирует DSL код и предлагает параметры
    
    Пример:
    DSL: 'type "Python tutorial"\nclick search'
    → Предлагает параметр 'query' для "Python tutorial"
    """
    import re
    
    # Находим строковые литералы
    string_literals = re.findall(r'"([^"]+)"', dsl_code)
    
    # AI анализирует и предлагает имена параметров
    suggested_params = []
    for literal in string_literals:
        if self._looks_like_parameter(literal):
            param_name = self._suggest_parameter_name(literal)
            suggested_params.append(param_name)
    
    return suggested_params

def _suggest_parameter_name(self, value: str) -> str:
    """AI предлагает имя параметра на основе значения"""
    # Простая эвристика (можно улучшить с помощью AI)
    if 'http' in value.lower():
        return 'url'
    elif len(value.split()) > 1:
        return 'query'
    elif '@' in value:
        return 'username'
    else:
        return 'text'
```

## 📊 Статистика и диагностика

### **Статистика загрузки переменных**
```python
# При инициализации:
if self.variables:
    print(f"✅ Загружено {len(self.variables)} DSL переменных")
    
    # Детальная статистика
    simple_vars = len([v for v in self.variables.values() if not v['params']])
    param_vars = len([v for v in self.variables.values() if v['params']])
    
    print(f"   📝 Простые переменные: {simple_vars}")
    print(f"   🔧 Параметризованные: {param_vars}")
```

### **Диагностика использования**
```python
def get_variable_usage_stats(self) -> Dict[str, int]:
    """Статистика использования переменных"""
    usage_stats = {}
    
    # Анализируем все .atlas файлы
    for atlas_file in Path('macros/production').glob('*.atlas'):
        with open(atlas_file, 'r') as f:
            content = f.read()
        
        # Ищем использования переменных
        import re
        variables_used = re.findall(r'\$\{([^}:]+)', content)
        
        for var_name in variables_used:
            usage_stats[var_name] = usage_stats.get(var_name, 0) + 1
    
    return usage_stats
```

---

**Следующий раздел:**
- [04-yaml-generation.md](04-yaml-generation.md) - Генерация выполнимого YAML из DSL
