# 🎯 Как работает --config и --run

## 📖 Команда

```bash
python3 macro_sequence.py --config examples/tiktok_auto_like.atlas --run tiktok_auto_like
```

---

## 🔍 Разбор по частям

### 1. `--config examples/tiktok_auto_like.atlas`

**Что это:**  
Путь к файлу с конфигурацией (последовательностью действий)

**Что происходит:**
```python
# macro_sequence.py строка 102-115
if self.config_path.endswith('.atlas'):
    # DSL формат - конвертируем в YAML
    from atlas_dsl_parser import AtlasDSLParser
    parser = AtlasDSLParser()
    parsed = parser.parse_file(self.config_path)
    
    # Создаем структуру конфига
    sequence_name = Path(self.config_path).stem  # ← ЗДЕСЬ!
    self.config = {
        'sequences': {sequence_name: parsed},
        'settings': {}
    }
```

**Что такое `Path(self.config_path).stem`?**

```python
Path("examples/tiktok_auto_like.atlas").stem
# → "tiktok_auto_like"

# .stem берет имя файла БЕЗ расширения
# examples/tiktok_auto_like.atlas → tiktok_auto_like
```

**Результат:**
```python
self.config = {
    'sequences': {
        'tiktok_auto_like': {  # ← Имя из файла!
            'name': 'TikTok Auto Like',
            'steps': [
                {'action': 'open', 'app': 'ChromeApp'},
                {'action': 'wait', 'duration': 2.5},
                # ... и т.д.
            ]
        }
    },
    'settings': {}
}
```

---

### 2. `--run tiktok_auto_like`

**Что это:**  
Имя последовательности, которую нужно запустить

**Откуда берется имя:**  
Из имени файла! `tiktok_auto_like.atlas` → `tiktok_auto_like`

**Что происходит:**
```python
# macro_sequence.py строка 1226
runner.run_sequence(args.run, args.delay)
# runner.run_sequence("tiktok_auto_like", 3)
```

**Внутри run_sequence:**
```python
def run_sequence(self, sequence_name, delay=3):
    # Ищет последовательность по имени
    sequences = self.config.get('sequences', {})
    
    if sequence_name not in sequences:
        print(f"❌ Последовательность '{sequence_name}' не найдена")
        return
    
    sequence = sequences[sequence_name]  # ← Берет из config
    steps = sequence.get('steps', [])
    
    # Выполняет шаги
    for step in steps:
        self.execute_step(step)
```

---

## 🎯 Полный цикл

### Шаг 1: Запуск команды

```bash
python3 macro_sequence.py --config examples/tiktok_auto_like.atlas --run tiktok_auto_like
```

### Шаг 2: Загрузка конфига

```python
# macro_sequence.py
runner = MacroRunner("examples/tiktok_auto_like.atlas")

# Внутри __init__:
self._load_config()
```

### Шаг 3: Парсинг DSL

```python
# _load_config()
if self.config_path.endswith('.atlas'):
    # 1. Парсим DSL файл
    parser = AtlasDSLParser()
    parsed = parser.parse_file("examples/tiktok_auto_like.atlas")
    
    # 2. Берем имя из файла
    sequence_name = Path("examples/tiktok_auto_like.atlas").stem
    # sequence_name = "tiktok_auto_like"
    
    # 3. Создаем структуру
    self.config = {
        'sequences': {
            'tiktok_auto_like': parsed  # ← Ключ = имя файла
        }
    }
```

### Шаг 4: Запуск последовательности

```python
# main()
runner.run_sequence("tiktok_auto_like", 3)

# run_sequence()
sequence = self.config['sequences']['tiktok_auto_like']  # ← Находит по имени
steps = sequence['steps']

# Выполняет каждый шаг
for step in steps:
    self.execute_step(step)
```

---

## 💡 Почему имя совпадает с файлом?

### Для DSL файлов (.atlas):

**Имя последовательности = Имя файла (без расширения)**

```
examples/tiktok_auto_like.atlas
         ^^^^^^^^^^^^^^^^
         Это имя последовательности!
```

**Код:**
```python
sequence_name = Path(self.config_path).stem
# "examples/tiktok_auto_like.atlas" → "tiktok_auto_like"
```

**Поэтому:**
```bash
--config examples/tiktok_auto_like.atlas --run tiktok_auto_like
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^      ^^^^^^^^^^^^^^^^
         Файл                                  Имя из файла
```

---

### Для YAML файлов (.yaml):

**Имя последовательности = Ключ в YAML**

```yaml
# my_sequences.yaml
sequences:
  my_custom_name:  # ← Это имя последовательности!
    name: My Sequence
    steps:
      - action: click
```

**Запуск:**
```bash
--config my_sequences.yaml --run my_custom_name
         ^^^^^^^^^^^^^^^^^      ^^^^^^^^^^^^^^^
         Файл                   Ключ в YAML
```

---

## 📊 Сравнение DSL vs YAML

| Аспект | DSL (.atlas) | YAML (.yaml) |
|--------|--------------|--------------|
| **Имя последовательности** | Имя файла | Ключ в sequences |
| **Пример файла** | `tiktok_auto_like.atlas` | `my_sequences.yaml` |
| **Имя для --run** | `tiktok_auto_like` | Любое (из YAML) |
| **Количество последовательностей** | 1 на файл | Много в одном файле |

---

## 🎯 Примеры

### Пример 1: DSL файл

**Файл:** `examples/tiktok_auto_like.atlas`

```atlas
# TikTok Auto Like
open ChromeApp
wait 2s
click Chrome-TikTok-Like
```

**Запуск:**
```bash
python3 macro_sequence.py --config examples/tiktok_auto_like.atlas --run tiktok_auto_like
#                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^      ^^^^^^^^^^^^^^^^
#                                   Путь к файлу                          Имя файла без .atlas
```

**Что происходит:**
```python
# 1. Парсит tiktok_auto_like.atlas
# 2. Создает: config['sequences']['tiktok_auto_like'] = {...}
# 3. Запускает: run_sequence('tiktok_auto_like')
```

---

### Пример 2: YAML файл с одной последовательностью

**Файл:** `my_sequences.yaml`

```yaml
sequences:
  auto_like:  # ← Имя последовательности
    name: Auto Like
    steps:
      - action: click
        template: templates/like.png
```

**Запуск:**
```bash
python3 macro_sequence.py --config my_sequences.yaml --run auto_like
#                                   ^^^^^^^^^^^^^^^^      ^^^^^^^^^
#                                   Путь к файлу          Ключ из sequences
```

---

### Пример 3: YAML файл с несколькими последовательностями

**Файл:** `my_sequences.yaml`

```yaml
sequences:
  auto_like:  # ← Первая последовательность
    steps:
      - action: click
        template: templates/like.png
  
  auto_comment:  # ← Вторая последовательность
    steps:
      - action: click
        template: templates/comment.png
  
  auto_share:  # ← Третья последовательность
    steps:
      - action: click
        template: templates/share.png
```

**Запуск любой:**
```bash
# Запустить auto_like
python3 macro_sequence.py --config my_sequences.yaml --run auto_like

# Запустить auto_comment
python3 macro_sequence.py --config my_sequences.yaml --run auto_comment

# Запустить auto_share
python3 macro_sequence.py --config my_sequences.yaml --run auto_share
```

---

## 🤔 Что если имя не совпадает?

### DSL файл:

```bash
# Файл: examples/tiktok_auto_like.atlas
python3 macro_sequence.py --config examples/tiktok_auto_like.atlas --run wrong_name
#                                                                         ^^^^^^^^^^
#                                                                         ❌ Ошибка!
```

**Результат:**
```
❌ Последовательность 'wrong_name' не найдена
Доступные последовательности: tiktok_auto_like
```

**Почему:**
```python
# Имя последовательности = имя файла
sequence_name = "tiktok_auto_like"  # Из файла

# Ищем 'wrong_name'
if 'wrong_name' not in sequences:  # ← Не найдено!
    print("❌ Последовательность 'wrong_name' не найдена")
```

---

### YAML файл:

```bash
# Файл: my_sequences.yaml
# sequences:
#   auto_like: ...

python3 macro_sequence.py --config my_sequences.yaml --run wrong_name
#                                                           ^^^^^^^^^^
#                                                           ❌ Ошибка!
```

**Результат:**
```
❌ Последовательность 'wrong_name' не найдена
Доступные последовательности: auto_like
```

---

## 🎯 Как создать свою последовательность?

### Вариант 1: DSL файл (один файл = одна последовательность)

**1. Создай файл:**
```bash
nano examples/my_workflow.atlas
```

**2. Напиши DSL:**
```atlas
# My Workflow
open ChromeApp
wait 2s
click MyButton
```

**3. Запусти:**
```bash
python3 macro_sequence.py --config examples/my_workflow.atlas --run my_workflow
#                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^      ^^^^^^^^^^^
#                                   Путь к файлу                     Имя файла
```

**Имя последовательности = `my_workflow` (из имени файла)**

---

### Вариант 2: YAML файл (один файл = много последовательностей)

**1. Создай/открой файл:**
```bash
nano my_sequences.yaml
```

**2. Добавь последовательность:**
```yaml
sequences:
  my_custom_workflow:  # ← Любое имя!
    name: My Custom Workflow
    steps:
      - action: click
        template: templates/button.png
      - action: wait
        duration: 2.0
```

**3. Запусти:**
```bash
python3 macro_sequence.py --config my_sequences.yaml --run my_custom_workflow
#                                   ^^^^^^^^^^^^^^^^      ^^^^^^^^^^^^^^^^^^
#                                   Путь к файлу          Ключ из sequences
```

**Имя последовательности = `my_custom_workflow` (из YAML)**

---

## 📝 Итоги

### DSL (.atlas):
- ✅ **Имя последовательности = Имя файла** (без расширения)
- ✅ Один файл = одна последовательность
- ✅ Простой синтаксис
- ✅ Автоматическое именование

**Пример:**
```bash
examples/tiktok_auto_like.atlas → --run tiktok_auto_like
examples/my_workflow.atlas → --run my_workflow
```

### YAML (.yaml):
- ✅ **Имя последовательности = Ключ в sequences**
- ✅ Один файл = много последовательностей
- ✅ Гибкое именование
- ✅ Можно выбрать любое имя

**Пример:**
```yaml
sequences:
  custom_name: ...  → --run custom_name
  another_one: ...  → --run another_one
```

---

## 🎉 Теперь ты знаешь!

**Команда:**
```bash
python3 macro_sequence.py --config examples/tiktok_auto_like.atlas --run tiktok_auto_like
```

**Что происходит:**
1. Загружает `examples/tiktok_auto_like.atlas`
2. Парсит DSL → YAML
3. Создает последовательность с именем `tiktok_auto_like` (из имени файла)
4. Запускает последовательность `tiktok_auto_like`
5. Выполняет шаги один за другим

**Имя последовательности всегда = Имя файла (для DSL)** 🚀
