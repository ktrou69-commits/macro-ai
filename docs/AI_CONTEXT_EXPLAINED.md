# 🧠 Что получает AI - Подробное объяснение

## 🎯 Краткий ответ

AI получает 2 источника информации:

1. **`{templates_structure}`** - Список всех доступных кнопок/шаблонов
2. **`{dsl_reference}`** - Справочник DSL команд

---

## 📂 Источник 1: templates_structure

### Откуда берется:
```python
def get_templates_structure(self) -> str:
    # 1. Читает все structure.txt файлы из templates/
    for structure_file in self.templates_dir.rglob("structure.txt"):
        content = f.read()  # Читает содержимое
    
    # 2. Сканирует все PNG файлы
    for png_file in self.templates_dir.rglob("*.png"):
        name = png_file.stem  # Имя файла без .png
```

### Файлы-источники:
```
templates/Chrome/TikTok/structure.txt
templates/Chrome/structure.txt
templates/Atlas/structure.txt
... и все PNG файлы в templates/
```

### Что получает AI:
```
📂 СТРУКТУРА ШАБЛОНОВ:

├── Chrome/
│   ├── ChromeBasicGuiButtons/
│   │   ├── ChromeApp-btn.png              # Иконка запуска Chrome
│   │   ├── ChromeNewTab-btn.png           # Кнопка "плюс" — открыть новую вкладку
│   │   ├── ChromeSearchField-btn.png      # Поле ввода адреса/поиска
│   │   ├── ChromeSearchSend-btn.png       # Кнопка "Enter"
│   │   ├── ChromeReload-btn.png           # Кнопка обновления страницы

📄 ДОСТУПНЫЕ ШАБЛОНЫ:
  • ChromeApp (Chrome/ChromeBasicGuiButtons/ChromeApp-btn.png)
  • ChromeNewTab (Chrome/ChromeBasicGuiButtons/ChromeNewTab-btn.png)
  • ChromeSearchField (Chrome/ChromeBasicGuiButtons/ChromeSearchField-btn.png)
  • Chrome-TikTok-Like (Chrome/TikTok/Chrome-TikTok-Like.png)
  • Like (Chrome/TikTok/Chrome-TikTok-Like.png)
  ... и все остальные
```

**Это список всех кнопок которые AI может использовать!**

---

## 📚 Источник 2: dsl_reference

### Откуда берется:
```python
def get_dsl_reference(self) -> str:
    # Читает файл dsl_references/DSL_REFERENCE.txt
    if self.dsl_ref_path.exists():
        with open(self.dsl_ref_path, 'r') as f:
            return f.read()
```

### Файл-источник:
```
dsl_references/DSL_REFERENCE.txt
```

### Что получает AI:
```
================================================================================
DSL СПРАВОЧНИК - Доступные команды и шаблоны
================================================================================

📖 РАЗДЕЛ 1: DSL КОМАНДЫ
================================================================================

Клики и взаимодействие:
--------------------------------------------------------------------------------
  open <template>                          # Запуск приложения (клик по иконке)
  click <template>                         # Клик по кнопке/элементу
  click (<x>, <y>)                         # Клик по абсолютным координатам
  double_click <template>                  # Двойной клик
  right_click <template>                   # Правый клик

Ввод текста:
--------------------------------------------------------------------------------
  type "<text>"                            # Ввод текста
  paste "<text>"                           # Вставка текста

Клавиатура:
--------------------------------------------------------------------------------
  press <key>                              # Нажатие клавиши
  hotkey <key1>+<key2>                     # Комбинация клавиш

Прокрутка:
--------------------------------------------------------------------------------
  scroll <direction>                       # Прокрутка
  scroll <direction> <amount>              # Прокрутка на N пикселей

Ожидание:
--------------------------------------------------------------------------------
  wait <duration>                          # Ожидание (3s, 1.5s, 500ms)

Циклы:
--------------------------------------------------------------------------------
  repeat <N>:                              # Повторить N раз

📝 ПРИМЕРЫ:
--------------------------------------------------------------------------------

# Простой клик
click ChromeSearchField

# Ввод текста
type "Hello World"

# Цикл
repeat 5:
  click LikeButton
  wait 1s

... и весь остальной справочник
```

**Это инструкция как писать DSL код!**

---

## 🔄 Полный процесс

### 1. Пользователь вводит:
```
"открыть TikTok и поставить 5 лайков"
```

### 2. AI генератор собирает контекст:

```python
# Шаг 1: Читает structure.txt файлы
templates_structure = self.get_templates_structure()
# Результат: Список всех кнопок

# Шаг 2: Читает DSL_REFERENCE.txt
dsl_reference = self.get_dsl_reference()
# Результат: Справочник команд
```

### 3. Формирует промпт для AI:

```python
prompt = f"""
Ты — AI-интерпретатор DSL-сценариев...

📘 ОСНОВНЫЙ КОНТЕКСТ
{templates_structure}  ← Список кнопок

📚 DSL СПРАВОЧНИК
{dsl_reference}  ← Справочник команд

INPUT: открыть TikTok и поставить 5 лайков
"""
```

### 4. Отправляет AI:
```python
response = ai_api.generate(prompt)
```

### 5. AI видит:
```
Системный промпт:
- Ты AI-интерпретатор DSL
- У тебя есть список кнопок: ChromeApp, ChromeNewTab, Like...
- У тебя есть команды: open, click, type, wait, repeat...

Запрос пользователя:
- "открыть TikTok и поставить 5 лайков"

Задача:
- Создай DSL макрос используя доступные кнопки и команды
```

### 6. AI генерирует:
```atlas
open ChromeApp
wait 2s
click ChromeNewTab
type "tiktok.com"
press enter
wait 5s
repeat 5:
  click Like
  wait 1.5s
  scroll down
  wait 2s
```

---

## 📊 Визуальная схема

```
┌─────────────────────────────────────────────────────────────┐
│  ФАЙЛЫ-ИСТОЧНИКИ                                            │
├─────────────────────────────────────────────────────────────┤
│  1. templates/Chrome/TikTok/structure.txt                   │
│  2. templates/Chrome/structure.txt                          │
│  3. templates/**/*.png (все PNG файлы)                      │
│  4. dsl_references/DSL_REFERENCE.txt                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  ФУНКЦИИ ЗАГРУЗКИ                                           │
├─────────────────────────────────────────────────────────────┤
│  get_templates_structure() → Читает 1, 2, 3                │
│  get_dsl_reference() → Читает 4                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  КОНТЕКСТ ДЛЯ AI                                            │
├─────────────────────────────────────────────────────────────┤
│  {templates_structure}:                                     │
│    • ChromeApp                                              │
│    • ChromeNewTab                                           │
│    • ChromeSearchField                                      │
│    • Like                                                   │
│    • ... все кнопки                                         │
│                                                             │
│  {dsl_reference}:                                           │
│    • open <template>                                        │
│    • click <template>                                       │
│    • type "<text>"                                          │
│    • wait <duration>                                        │
│    • repeat <N>:                                            │
│    • ... все команды                                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  ПРОМПТ ДЛЯ AI                                              │
├─────────────────────────────────────────────────────────────┤
│  System: "Ты AI-интерпретатор DSL..."                      │
│  Context: templates_structure + dsl_reference               │
│  User: "INPUT: открыть TikTok и поставить 5 лайков"        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│  AI ГЕНЕРИРУЕТ DSL КОД                                      │
├─────────────────────────────────────────────────────────────┤
│  open ChromeApp                                             │
│  wait 2s                                                    │
│  click ChromeNewTab                                         │
│  type "tiktok.com"                                          │
│  press enter                                                │
│  wait 5s                                                    │
│  repeat 5:                                                  │
│    click Like                                               │
│    wait 1.5s                                                │
│    scroll down                                              │
│    wait 2s                                                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 💡 Ключевые моменты

### 1. Два источника информации:
- **Кнопки** (из `templates/` и `structure.txt`)
- **Команды** (из `dsl_references/DSL_REFERENCE.txt`)

### 2. Динамическая загрузка:
- При каждом запуске читаются заново
- Если добавил новую кнопку → AI сразу знает о ней
- Если обновил справочник → AI использует новые команды

### 3. Автоматическая генерация:
- Если `DSL_REFERENCE.txt` нет → генерируется автоматически
- Сканируются все PNG файлы → AI знает все кнопки

---

## 🎯 Итоги

### Что получает AI:

1. **Список всех кнопок:**
   - Из `templates/**/*.png`
   - Из `templates/**/structure.txt`
   - Пример: ChromeApp, ChromeNewTab, Like, SearchField...

2. **Справочник DSL команд:**
   - Из `dsl_references/DSL_REFERENCE.txt`
   - Пример: open, click, type, wait, repeat...

3. **Запрос пользователя:**
   - "открыть TikTok и поставить 5 лайков"

### AI комбинирует:
```
Кнопки + Команды + Запрос = DSL макрос
```

**Просто и эффективно!** 🚀
