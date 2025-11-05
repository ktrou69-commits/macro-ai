# 📋 Шпаргалка - Macro AI v3.0

## 🚀 Быстрые команды

### Тест AI
```bash
export GEMINI_API_KEY="AIzaSyBGlFjt6bKJLJqcsavArM6wb7voH111gc8"
python3 test_gemini.py
```

### Тест кнопок Atlas
```bash
python3 macro_sequence.py --config examples/test_ai_simple.yaml --run atlas_minimal
```

### Полная автоматизация
```bash
export GEMINI_API_KEY="AIzaSyBGlFjt6bKJLJqcsavArM6wb7voH111gc8"
python3 macro_sequence.py --config examples/tiktok_ai_atlas.yaml --run tiktok_ai_atlas
```

---

## 📸 Шаблоны

### Созданные:
- ✅ `tiktok_comments_btn.png` - кнопка комментариев
- ✅ `tiktok_reply_btn.png` - кнопка ответить
- 🆕 `tiktok_input_field.png` - поле ввода
- 🆕 `tiktok_send_btn.png` - кнопка отправить

### Создать новый:
```bash
python3 utils/smart_capture.py
# или
Cmd + Shift + 4  # скриншот → обрезать → сохранить
```

---

## ⚙️ Настройки

### Количество комментариев:
```yaml
# examples/tiktok_ai_atlas.yaml
variables:
  reply_count: 10  # было 5
```

### Тональность:
```yaml
variables:
  reply_tone: смешной  # дружелюбный, профессиональный, мотивирующий
```

### Область OCR:
```yaml
- action: ai_extract_text
  region: [200, 400, 500, 80]  # [x, y, width, height]
```

---

## 🐛 Troubleshooting

### Шаблон не находится:
```bash
# Создай новый
python3 utils/smart_capture.py

# Или используй координаты
- action: click
  position: absolute
  x: 400
  y: 650
```

### Несколько одинаковых кнопок:
```yaml
# Выбери конкретную по индексу
- action: click
  template: templates/button.png
  index: 0  # Первая (лучший score)
  index: 1  # Вторая
```

### Похожие кнопки (находит не ту):
```yaml
# Решение 1: Специфичный шаблон (только уникальная часть)
# Решение 2: Index
- action: click
  template: templates/button.png
  index: 1  # Попробуй 0, 1, 2
# Решение 3: Координаты
- action: click
  position: absolute
  x: 1245
  y: 275
```

### OCR не читает:
```yaml
# Увеличь область
region: [100, 300, 700, 150]
```

### AI слишком длинный:
```yaml
- action: ai_generate
  prompt: "Короткий ответ (до 30 символов)"
  max_tokens: 30
```

---

## 📁 Структура файлов

```
local-macros/
├── macro_sequence.py           # Основной движок
├── test_gemini.py              # Тест AI
├── QUICKSTART_ATLAS.md         # Быстрый старт
├── CHEATSHEET.md               # Эта шпаргалка
├── examples/
│   ├── tiktok_ai_atlas.yaml    # Полная автоматизация
│   └── test_ai_simple.yaml     # Тестовые конфиги
├── templates/
│   ├── tiktok_comments_btn.png
│   ├── tiktok_reply_btn.png
│   ├── tiktok_input_field.png
│   └── tiktok_send_btn.png
└── docs/
    ├── AI_COMMENTS_GUIDE.md    # Полный гайд AI
    ├── ATLAS_BROWSER_GUIDE.md  # Гайд для Atlas
    └── CREATE_TEMPLATES.md     # Создание шаблонов
```

---

## 🎯 Последовательность действий

### Полный цикл:
1. Открыть комментарии (`tiktok_comments_btn.png`)
2. Кликнуть "Ответить" (`tiktok_reply_btn.png`)
3. Кликнуть поле ввода (`tiktok_input_field.png`)
4. Ввести AI ответ (`type: {reply_text}`)
5. Кликнуть "Отправить" (`tiktok_send_btn.png`)
6. Скролл к следующему (`scroll: down`)

### С AI:
1. OCR → прочитать комментарий
2. Gemini → сгенерировать ответ
3. Template → найти кнопки
4. PyAutoGUI → ввести и отправить

---

## 💡 Полезные команды

### Список последовательностей:
```bash
python3 macro_sequence.py --config examples/tiktok_ai_atlas.yaml --list
```

### С задержкой:
```bash
python3 macro_sequence.py --config examples/tiktok_ai_atlas.yaml --run tiktok_ai_atlas --delay 5
```

### Найти координаты:
```bash
python3 utils/find_coordinates.py
```

---

## 🔧 Переменные

### В YAML:
```yaml
variables:
  my_var: значение

# Использование:
text: "{my_var}"
times: "{my_var}"
prompt: "Текст с {my_var}"
```

### Поддерживаемые типы:
- `times: 5` - число
- `times: "{reply_count}"` - переменная
- `times: "5"` - строка с числом
- `text: "{reply_text}"` - подстановка в текст

---

## 📊 Статус

### Что работает:
- ✅ Gemini API (gemini-2.5-flash)
- ✅ Template matching (4 шаблона)
- ✅ OCR (EasyOCR)
- ✅ Переменные в repeat
- ✅ Atlas браузер

### В разработке:
- 🔄 Selenium (не работает с Atlas)
- 🔄 Локальная LLM
- 🔄 GUI для настройки

---

**Сохрани эту шпаргалку!** 📌
