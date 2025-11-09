# 📚 DSL Reference Generator - Генератор справочника

## 🎯 Что это?

**DSL Reference Generator** - утилита которая сканирует папку с шаблонами и создает **текстовый справочник** со всеми доступными:
- ✅ DSL командами (open, click, wait, type, ...)
- ✅ Именами шаблонов (ChromeSearchField, Like, ...)
- ✅ Примерами использования

**Зачем это нужно?**  
Когда пишешь `.atlas` файлы, не нужно гадать какие имена использовать - просто открой справочник!

---

## 🚀 Быстрый старт

### 1. Сгенерировать справочник для всех шаблонов

```bash
python3 utils/dsl_reference_generator.py
```

**Результат:**  
Создается файл `dsl_references/DSL_REFERENCE.txt` со всеми шаблонами из папки `templates/`

---

### 2. Справочник для конкретной папки

```bash
# Только TikTok шаблоны
python3 utils/dsl_reference_generator.py --templates-path templates/Chrome/TikTok

# Только Chrome шаблоны
python3 utils/dsl_reference_generator.py --templates-path templates/Chrome

# Только Atlas шаблоны
python3 utils/dsl_reference_generator.py --templates-path templates/Atlas
```

---

### 3. Сохранить в другой файл

```bash
python3 utils/dsl_reference_generator.py \
  --templates-path templates/Chrome/TikTok \
  --output dsl_references/TikTok_Reference.txt
```

---

## 📖 Что содержит справочник

### Раздел 1: DSL Команды

**Все доступные команды с описанием:**

```
Клики и взаимодействие:
  open <template>          # Запуск приложения
  click <template>         # Клик по кнопке
  double_click <template>  # Двойной клик
  right_click <template>   # Правый клик

Ввод текста:
  type "<text>"            # Ввод текста
  paste "<text>"           # Вставка из буфера

Клавиатура:
  press <key>              # Нажатие клавиши
  hotkey <key1>+<key2>     # Комбинация клавиш

Прокрутка:
  scroll <direction>       # Прокрутка
  scroll down 500          # Прокрутка на N пикселей

Ожидание:
  wait <duration>          # Ожидание (3s, 1.5s, 500ms)

Циклы:
  repeat <N>:              # Повторить N раз
```

---

### Раздел 2: Доступные шаблоны

**Все файлы с их именами:**

```
📄 templates/Chrome/TikTok/Chrome-TikTok-Like.png
   Доступные имена:
     • Chrome-TikTok-Like
     • Like
     • Chrome_TikTok_Like

📄 templates/Chrome/TikTok/ChromeSearchField.png
   Доступные имена:
     • ChromeSearchField
```

**Теперь знаешь какие имена можно использовать!**

---

### Раздел 3: Все имена (алфавитный список)

**Быстрый поиск:**

```
  • Chrome-TikTok-Like
  • ChromeApp
  • ChromeNewTab
  • ChromeSearchField
  • Like
```

---

## 💡 Примеры использования

### Пример 1: Справочник для всех шаблонов

```bash
python3 utils/dsl_reference_generator.py
```

**Результат: `DSL_REFERENCE.txt`**
```
================================================================================
DSL СПРАВОЧНИК - Доступные команды и шаблоны
================================================================================

📂 Папка с шаблонами: templates
📄 Всего файлов: 62
🏷️  Всего уникальных имен: 150

📖 РАЗДЕЛ 1: DSL КОМАНДЫ
...

📋 РАЗДЕЛ 2: ДОСТУПНЫЕ ШАБЛОНЫ
...

🏷️  РАЗДЕЛ 3: ВСЕ ДОСТУПНЫЕ ИМЕНА
...
```

---

### Пример 2: Справочник для TikTok

```bash
python3 utils/dsl_reference_generator.py \
  --templates-path templates/Chrome/TikTok \
  --output TikTok_Reference.txt
```

**Результат: `TikTok_Reference.txt`**
```
📂 Папка с шаблонами: templates/Chrome/TikTok
📄 Всего файлов: 4
🏷️  Всего уникальных имен: 6

Доступные имена:
  • Chrome-TikTok-Like
  • ChromeApp
  • ChromeNewTab
  • ChromeSearchField
  • Like
```

**Теперь можешь писать `.atlas` файлы для TikTok!**

---

### Пример 3: Справочник для Chrome

```bash
python3 utils/dsl_reference_generator.py \
  --templates-path templates/Chrome \
  --output Chrome_Reference.txt
```

---

## 🎯 Как использовать справочник

### Шаг 1: Сгенерируй справочник

```bash
python3 utils/dsl_reference_generator.py --templates-path templates/Chrome/TikTok
```

### Шаг 2: Открой `DSL_REFERENCE.txt`

```bash
cat DSL_REFERENCE.txt
# или
open DSL_REFERENCE.txt
```

### Шаг 3: Найди нужное имя

```
📄 templates/Chrome/TikTok/ChromeSearchField.png
   Доступные имена:
     • ChromeSearchField  ← Используй это!
```

### Шаг 4: Используй в `.atlas` файле

```atlas
# examples/my_workflow.atlas
click ChromeSearchField  ← Скопировал из справочника!
type "tiktok.com"
press enter
```

**Готово!** ✅

---

## 📊 Аргументы командной строки

| Аргумент | Описание | По умолчанию |
|----------|----------|--------------|
| `--templates-path` | Путь к папке с шаблонами | `templates` |
| `--output` | Имя выходного файла | `DSL_REFERENCE.txt` |

---

## 🎨 Примеры команд

### Все шаблоны
```bash
python3 utils/dsl_reference_generator.py
```

### TikTok шаблоны
```bash
python3 utils/dsl_reference_generator.py --templates-path templates/Chrome/TikTok
```

### Chrome шаблоны
```bash
python3 utils/dsl_reference_generator.py --templates-path templates/Chrome
```

### Atlas шаблоны
```bash
python3 utils/dsl_reference_generator.py --templates-path templates/Atlas
```

### Свой файл
```bash
python3 utils/dsl_reference_generator.py --output my_reference.txt
```

### Комбинация
```bash
python3 utils/dsl_reference_generator.py \
  --templates-path templates/Chrome/TikTok \
  --output TikTok_DSL.txt
```

---

## 🔍 Как работает

### 1. Сканирование папки

```python
# Находит все .png файлы
for png_file in templates_dir.rglob("*.png"):
    # templates/Chrome/TikTok/Chrome-TikTok-Like.png
```

### 2. Извлечение имен

```python
# Для файла: Chrome-TikTok-Like.png
names = [
    "Chrome-TikTok-Like",  # Полное имя
    "Like",                # Без префиксов
    "Chrome_TikTok_Like"   # С подчеркиваниями
]
```

### 3. Создание справочника

```python
# Формирует текстовый файл с:
# - DSL командами
# - Доступными шаблонами
# - Всеми именами
```

---

## 💡 Советы

### 1. Генерируй справочник после добавления шаблонов

```bash
# Добавил новые шаблоны в templates/Chrome/TikTok
# Обнови справочник
python3 utils/dsl_reference_generator.py --templates-path templates/Chrome/TikTok
```

### 2. Держи справочник открытым при написании `.atlas`

```bash
# Терминал 1: Открой справочник
cat DSL_REFERENCE.txt

# Терминал 2: Пиши .atlas файл
nano examples/my_workflow.atlas
```

### 3. Создай справочники для каждой платформы

```bash
# TikTok
python3 utils/dsl_reference_generator.py \
  --templates-path templates/Chrome/TikTok \
  --output TikTok_Reference.txt

# YouTube
python3 utils/dsl_reference_generator.py \
  --templates-path templates/Chrome/YouTube \
  --output YouTube_Reference.txt

# Chrome
python3 utils/dsl_reference_generator.py \
  --templates-path templates/Chrome \
  --output Chrome_Reference.txt
```

---

## 🎉 Преимущества

### Без справочника:
```atlas
# Как называется кнопка поиска?
click ChromeSearch?  # ❌ Не работает
click SearchField?   # ❌ Не работает
click Chrome-Search? # ❌ Не работает
```

### Со справочником:
```bash
# Открыл DSL_REFERENCE.txt
# Нашел: ChromeSearchField

click ChromeSearchField  # ✅ Работает!
```

---

## 📁 Созданные файлы

```
utils/
├── dsl_reference_generator.py         ⭐ Утилита
└── DSL_REFERENCE_GENERATOR_README.md  📚 Это руководство

DSL_REFERENCE.txt                      📄 Справочник (генерируется)
TikTok_DSL_Reference.txt              📄 Справочник TikTok (пример)
```

---

## 🎯 Итоги

**DSL Reference Generator** - незаменимая утилита для написания `.atlas` файлов!

**Теперь ты всегда знаешь:**
- ✅ Какие команды доступны
- ✅ Какие имена шаблонов использовать
- ✅ Как правильно писать DSL

**Никогда больше не гадай - просто открой справочник!** 🚀
