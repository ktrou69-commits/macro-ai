# 🧠 YOLO - Вариации интеграции в макросы

## 📋 Обзор

YOLO8n уже есть в проекте для **детекции кнопок**. Вот **новые вариации** использования:

---

## 🎯 Вариация 1: Детекция UI элементов TikTok

### **Что детектируем:**
```python
classes = [
    'like_button',      # Сердечко лайка
    'comment_button',   # Кнопка комментариев
    'share_button',     # Кнопка шеринга
    'profile_pic',      # Аватар автора
    'subscribe_button', # Кнопка подписки
    'video_player',     # Область видео
]
```

### **Применение:**
```yaml
# В sequence_builder.py
- action: click_yolo
  class: "like_button"
  confidence: 0.7
  description: "Лайк через YOLO"

- action: click_yolo
  class: "comment_button"
  confidence: 0.7
  description: "Открыть комментарии"
```

### **Преимущества:**
- ✅ Не зависит от позиции кнопок
- ✅ Работает при изменении UI
- ✅ Адаптируется к разным разрешениям

---

## 💬 Вариация 2: Автоответы на комментарии

### **Архитектура:**
```
Screenshot → YOLO → OCR → LLM → Reply
```

### **Workflow:**
1. **YOLO** находит область комментария
2. **OCR** (EasyOCR/Tesseract) читает текст
3. **LLM** (GPT/Claude/Ollama) генерирует ответ
4. **YOLO** находит кнопку "Ответить"
5. **Клик** → Ввод → Отправка

### **Код:**
```python
# Детекция комментария
results = yolo.detect('comment_text')
comment_box = results[0].bbox

# Чтение текста
text = ocr.extract(comment_box)

# Генерация ответа
reply = llm.generate(f"Ответь на: {text}")

# Отправка
click(yolo.detect('reply_button'))
type(reply)
click(yolo.detect('send_button'))
```

### **Файлы:**
- `tiktok_comment_bot.py` - Готовая реализация
- `YOLO_COMMENT_DETECTION.md` - Полный гайд

---

## 🔄 Вариация 3: Контекстная автоматизация

### **Идея:**
YOLO определяет **контекст** и выбирает действия:

```python
# Определение контекста
context = yolo.detect_context()

if context == 'video_playing':
    # Лайк + комментарий
    actions = ['like', 'comment', 'scroll']
    
elif context == 'comment_section':
    # Читаем и отвечаем
    actions = ['read_comments', 'reply', 'like_comments']
    
elif context == 'profile_page':
    # Подписка
    actions = ['subscribe', 'like_videos']
```

### **Применение:**
```yaml
# Умная последовательность
smart_tiktok:
  steps:
    - action: detect_context
      yolo_model: "models/tiktok_context.pt"
    
    - action: conditional
      if_context: "video_playing"
      then:
        - action: click_yolo
          class: "like_button"
        - action: scroll
          direction: down
    
    - action: conditional
      if_context: "comment_section"
      then:
        - action: auto_reply
          llm: "gpt-3.5-turbo"
          style: "friendly"
```

---

## 🎨 Вариация 4: Мультимодальный подход

### **Комбинация методов:**

```python
# 1. YOLO - Грубая локализация
region = yolo.detect('comment_area')

# 2. Template Matching - Точный клик внутри
button = template.find('reply_button.png', region=region)

# 3. OCR - Чтение текста
text = ocr.extract(region)

# 4. LLM - Генерация ответа
reply = llm.generate(text)
```

### **Преимущества:**
- ✅ YOLO - для динамических элементов
- ✅ Template - для точности
- ✅ OCR - для текста
- ✅ LLM - для интеллекта

---

## 🏗️ Вариация 5: Обучение на своих данных

### **Кастомные классы:**

```python
# Для TikTok
tiktok_classes = [
    'like_button',
    'comment_button',
    'share_button',
    'comment_text',
    'reply_button',
    'input_field',
    'send_button',
]

# Для Instagram
instagram_classes = [
    'like_heart',
    'comment_bubble',
    'dm_button',
    'story_ring',
]

# Для YouTube
youtube_classes = [
    'like_button',
    'dislike_button',
    'subscribe_button',
    'comment_section',
]
```

### **Обучение:**
```bash
# 1. Собрать 100-200 скриншотов
# 2. Разметить в Roboflow/LabelImg
# 3. Обучить модель
python utils/train_yolo.py --data tiktok.yaml --epochs 100

# 4. Использовать
python macro_sequence.py --yolo-model models/tiktok_best.pt
```

---

## 📊 Вариация 6: Real-time детекция

### **Непрерывный мониторинг:**

```python
from ultralytics import YOLO
import pyautogui
import time

model = YOLO('models/tiktok_best.pt')

while True:
    # Скриншот
    screenshot = pyautogui.screenshot()
    
    # Детекция
    results = model(screenshot, conf=0.6)
    
    # Обработка
    for result in results:
        for box in result.boxes:
            cls = model.names[int(box.cls[0])]
            
            if cls == 'new_comment':
                # Новый комментарий!
                handle_new_comment(box)
            
            elif cls == 'like_button' and not liked:
                # Лайкнуть
                click_center(box)
                liked = True
    
    time.sleep(1)  # Проверка каждую секунду
```

---

## 🎯 Вариация 7: Интеграция в sequence_builder

### **Новые опции:**

```python
# В sequence_builder.py добавить:

def add_yolo_click_step(self):
    """Добавить клик через YOLO детекцию"""
    print("\n🧠 YOLO клик")
    
    # Выбор класса
    print("Доступные классы:")
    print("1. like_button")
    print("2. comment_button")
    print("3. share_button")
    print("4. reply_button")
    
    class_choice = input("Выбор: ").strip()
    class_map = {
        '1': 'like_button',
        '2': 'comment_button',
        '3': 'share_button',
        '4': 'reply_button',
    }
    
    class_name = class_map.get(class_choice, 'like_button')
    confidence = float(input("Минимальная уверенность (0.5-0.9): ") or "0.7")
    
    step = {
        'action': 'click_yolo',
        'class': class_name,
        'confidence': confidence,
        'description': f"YOLO клик на {class_name}"
    }
    
    self.current_sequence.append(step)
```

### **Использование:**
```bash
python3 sequence_builder.py

Что добавить?
------------------------------------------------------------
1. 🖱️  Клик по кнопке (template matching)
...
8. 🧠 Клик через YOLO  ← НОВОЕ!
```

---

## 🚀 Быстрый старт

### **1. Простая детекция кнопок:**
```bash
# Использовать готовую модель
python3 macro_ai.py --yolo --device mps
```

### **2. Автоответы на комментарии:**
```bash
# Установить зависимости
pip install easyocr openai

# Запустить бота
python3 tiktok_comment_bot.py
```

### **3. Обучить свою модель:**
```bash
# Собрать данные → Разметить → Обучить
python3 utils/train_yolo.py --data tiktok.yaml --epochs 100
```

---

## 📦 Зависимости

```bash
# Базовые
pip install ultralytics opencv-python pillow numpy

# Для OCR
pip install easyocr
# или
pip install pytesseract

# Для LLM
pip install openai
# или
pip install anthropic

# Для локальной LLM
# Установить Ollama: https://ollama.ai
ollama pull llama2
```

---

## 🎯 Рекомендации

### **Для начинающих:**
1. Используй готовую модель YOLO8n
2. Начни с template matching
3. Добавь YOLO для сложных случаев

### **Для продвинутых:**
1. Обучи свою модель на TikTok
2. Комбинируй YOLO + OCR + LLM
3. Создай умные последовательности

### **Для экспертов:**
1. Real-time детекция
2. Мультимодальный подход
3. Ансамбль моделей

---

## 📚 Файлы проекта

- `macro_ai.py` - Базовая YOLO детекция
- `tiktok_comment_bot.py` - Автоответы на комментарии
- `YOLO_COMMENT_DETECTION.md` - Полный гайд по детекции
- `YOLO_TRAINING_GUIDE.md` - Обучение своей модели
- `OPTIMIZATION.md` - Оптимизация производительности

---

**Итог:** YOLO открывает **безграничные возможности** для автоматизации! 🚀
