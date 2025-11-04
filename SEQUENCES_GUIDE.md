# 🎯 Руководство по последовательностям

## Быстрый старт

### 1. Подготовка шаблонов

Захвати нужные элементы интерфейса:

```bash
# Захватить иконку Atlas (уже есть в models/button.png)
python3 utils/capture_button.py

# Захватить кнопку "+" для новой вкладки
python3 utils/capture_button.py
# Сохрани как models/plus_button.png
```

### 2. Просмотр доступных последовательностей

```bash
python3 macro_sequence.py --config atlas_sequences.yaml --list
```

### 3. Запуск последовательности

```bash
# Открыть Atlas и создать новую вкладку
python3 macro_sequence.py --config atlas_sequences.yaml --run atlas_new_tab

# Открыть Atlas и создать 3 вкладки
python3 macro_sequence.py --config atlas_sequences.yaml --run atlas_three_tabs

# Открыть Atlas и перейти на сайт
python3 macro_sequence.py --config atlas_sequences.yaml --run atlas_open_url
```

---

## 📋 Структура конфигурации

### Базовый пример

```yaml
sequences:
  my_sequence:
    name: "Описание последовательности"
    repeat: 1  # Сколько раз повторить (опционально)
    steps:
      - action: click
        template: models/button.png
        clicks: 2
        interval: 0.3
        description: "Двойной клик"
```

---

## 🎬 Типы действий

### 1. CLICK - Клик по шаблону

```yaml
- action: click
  template: models/button.png      # Путь к шаблону
  clicks: 2                         # Количество кликов (по умолчанию: 1)
  interval: 0.3                     # Пауза между кликами (сек)
  wait_for_appear: true            # Ждать появления (опционально)
  timeout: 5                        # Таймаут ожидания (сек)
  optional: false                   # Не останавливаться если не найдено
  description: "Описание"
```

### 2. WAIT - Пауза

```yaml
- action: wait
  duration: 1.5                     # Длительность паузы (сек)
  description: "Ждем загрузки"
```

### 3. TYPE - Ввод текста

```yaml
- action: type
  text: "Hello World"               # Текст для ввода
  interval: 0.05                    # Пауза между символами
  description: "Ввод текста"
```

### 4. KEY - Нажатие клавиши

```yaml
- action: key
  key: "enter"                      # Клавиша (enter, tab, esc, space и т.д.)
  presses: 1                        # Количество нажатий
  description: "Нажать Enter"
```

### 5. HOTKEY - Комбинация клавиш

```yaml
- action: hotkey
  keys: ["command", "t"]            # Список клавиш для комбинации
  description: "Cmd+T"
```

**Доступные модификаторы:**
- `command` (⌘) - на macOS
- `ctrl` - Control
- `shift` - Shift
- `alt` / `option` - Alt/Option

---

## 💡 Примеры последовательностей

### Пример 1: Двойной клик и ожидание

```yaml
sequences:
  open_app:
    name: "Открыть приложение"
    steps:
      - action: click
        template: models/app_icon.png
        clicks: 2
        interval: 0.3
        
      - action: wait
        duration: 2.0
```

### Пример 2: Множественные клики с интервалом

```yaml
sequences:
  multiple_clicks:
    name: "5 кликов с паузой"
    steps:
      - action: click
        template: models/button.png
        clicks: 5
        interval: 0.5
```

### Пример 3: Ожидание появления элемента

```yaml
sequences:
  wait_and_click:
    name: "Ждать и кликнуть"
    steps:
      - action: click
        template: models/button.png
        clicks: 1
        wait_for_appear: true
        timeout: 10
```

### Пример 4: Цепочка действий

```yaml
sequences:
  complex_chain:
    name: "Сложная цепочка"
    steps:
      # Шаг 1: Открыть приложение
      - action: click
        template: models/app.png
        clicks: 2
        interval: 0.3
        
      # Шаг 2: Подождать загрузки
      - action: wait
        duration: 2.0
        
      # Шаг 3: Кликнуть на кнопку
      - action: click
        template: models/button1.png
        clicks: 1
        wait_for_appear: true
        
      # Шаг 4: Ввести текст
      - action: type
        text: "Hello World"
        
      # Шаг 5: Нажать Enter
      - action: key
        key: "enter"
        
      # Шаг 6: Подождать
      - action: wait
        duration: 1.0
        
      # Шаг 7: Кликнуть еще раз
      - action: click
        template: models/button2.png
        clicks: 1
```

### Пример 5: Повторяющаяся последовательность

```yaml
sequences:
  repeated_action:
    name: "Повторить 3 раза"
    repeat: 3  # Вся последовательность повторится 3 раза
    steps:
      - action: click
        template: models/button.png
        clicks: 1
        
      - action: wait
        duration: 1.0
```

---

## ⚙️ Глобальные настройки

```yaml
settings:
  default_interval: 0.5      # Пауза между кликами по умолчанию
  default_timeout: 5         # Таймаут ожидания по умолчанию
  threshold: 0.86            # Порог совпадения шаблона (0.0-1.0)
  fail_on_not_found: false   # Останавливаться если элемент не найден
```

---

## 🛡️ Безопасность

- **FAILSAFE**: Двигай мышь в угол экрана для экстренной остановки
- **Ctrl+C**: Остановка выполнения
- **optional: true**: Продолжить даже если элемент не найден

---

## 🎯 Твой случай: Atlas браузер

### Шаг 1: Захватить шаблоны

```bash
# 1. Захватить иконку Atlas (уже есть)
# models/button.png

# 2. Захватить кнопку "+" для новой вкладки
python3 utils/capture_button.py
# Выдели кнопку "+" в Atlas
# Сохранится в models/button.png
# Переименуй в models/plus_button.png
```

### Шаг 2: Создать свою последовательность

Отредактируй `atlas_sequences.yaml`:

```yaml
sequences:
  my_atlas_workflow:
    name: "Моя последовательность для Atlas"
    steps:
      # 1. Открыть Atlas двойным кликом
      - action: click
        template: models/button.png
        clicks: 2
        interval: 0.3
        
      # 2. Подождать открытия
      - action: wait
        duration: 1.5
        
      # 3. Кликнуть на "+" один раз
      - action: click
        template: models/plus_button.png
        clicks: 1
        wait_for_appear: true
        timeout: 5
```

### Шаг 3: Запустить

```bash
python3 macro_sequence.py --config atlas_sequences.yaml --run my_atlas_workflow
```

---

## 📊 Статистика

После выполнения последовательности выводится статистика:
- Количество выполненных последовательностей
- Всего кликов
- Успешных/неудачных поисков шаблонов

---

## 🐛 Отладка

Если что-то не работает:

1. **Проверь шаблоны**: `ls -la models/`
2. **Проверь конфиг**: `cat atlas_sequences.yaml`
3. **Запусти с отладкой**: Смотри вывод в консоли
4. **Тестируй по шагам**: Создай простую последовательность из 1-2 шагов

---

## 🚀 Продвинутое использование

### Создание сложных workflow

Можешь комбинировать любые действия:

```yaml
sequences:
  mega_workflow:
    name: "Мега рабочий процесс"
    repeat: 2
    steps:
      - action: click
        template: models/app.png
        clicks: 2
        interval: 0.3
        
      - action: wait
        duration: 2.0
        
      - action: hotkey
        keys: ["command", "t"]
        
      - action: type
        text: "https://example.com"
        
      - action: key
        key: "enter"
        
      - action: wait
        duration: 3.0
        
      - action: click
        template: models/button1.png
        clicks: 1
        
      - action: click
        template: models/button2.png
        clicks: 3
        interval: 0.5
```

Возможности безграничны! 🎉
