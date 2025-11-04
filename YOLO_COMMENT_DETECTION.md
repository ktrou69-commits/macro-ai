# 🧠 YOLO для детекции комментариев в TikTok

## 🎯 Концепция

Вместо **фиксированных координат** используем **YOLO** для:
1. **Детекция области комментариев**
2. **Поиск кнопки "Ответить"**
3. **Определение поля ввода**
4. **Поиск кнопки отправки**

---

## 📊 Вариации использования YOLO

### **Вариант 1: Детекция UI элементов**

```python
# Обучить YOLO распознавать:
classes = [
    'like_button',      # Кнопка лайка
    'comment_button',   # Кнопка комментариев
    'share_button',     # Кнопка шеринга
    'comment_text',     # Текст комментария
    'reply_button',     # Кнопка "Ответить"
    'input_field',      # Поле ввода
    'send_button',      # Кнопка отправки
    'profile_pic',      # Аватар автора
]
```

**Преимущества:**
- ✅ Не зависит от позиции элементов
- ✅ Работает на разных разрешениях
- ✅ Адаптируется к изменениям UI

---

### **Вариант 2: Детекция + OCR**

```python
# Workflow:
1. YOLO → Найти область комментария
2. Crop → Вырезать найденную область
3. OCR → Прочитать текст
4. LLM → Сгенерировать ответ
5. YOLO → Найти кнопку "Ответить"
6. Click → Кликнуть
7. Type → Вставить ответ
8. YOLO → Найти кнопку отправки
9. Click → Отправить
```

---

### **Вариант 3: Мультимодальный подход**

```python
# Комбинация методов:
if yolo.detect('comment_text'):
    # YOLO нашел комментарий
    bbox = yolo.get_bbox('comment_text', index=0)
    
    # OCR читает текст
    text = ocr.extract(bbox)
    
    # LLM генерирует ответ
    response = llm.generate(text)
    
    # Template matching для точного клика
    reply_btn = template.find('reply_button.png', region=bbox)
    click(reply_btn)
```

---

## 🏗️ Архитектура решения

### **Компоненты:**

```
┌─────────────┐
│   Screen    │ Скриншот экрана
└──────┬──────┘
       │
       v
┌─────────────┐
│    YOLO     │ Детекция элементов
└──────┬──────┘
       │
       ├─→ [comment_text] → OCR → Текст комментария
       │
       ├─→ [reply_button] → Click → Открыть ответы
       │
       ├─→ [input_field] → Click → Фокус на поле
       │
       └─→ [send_button] → Click → Отправить
```

---

## 📚 Обучение YOLO для TikTok

### **Шаг 1: Сбор данных**

```bash
# Сделай 100-200 скриншотов TikTok с комментариями
# Разные видео, разные авторы, разные комментарии
```

**Примеры:**
- Комментарии на русском
- Комментарии на английском
- Длинные и короткие комментарии
- Комментарии с эмодзи
- Разные темы (светлая/темная)

---

### **Шаг 2: Разметка данных**

Используй **Roboflow** или **LabelImg**:

```bash
# Установка LabelImg
pip install labelImg

# Запуск
labelImg
```

**Классы для разметки:**
1. `comment_text` - Текст комментария
2. `reply_button` - Кнопка "Ответить"
3. `input_field` - Поле ввода
4. `send_button` - Кнопка отправки
5. `like_button` - Кнопка лайка (опционально)

---

### **Шаг 3: Обучение модели**

```python
from ultralytics import YOLO

# Загрузка предобученной модели
model = YOLO('yolov8n.pt')

# Обучение на твоих данных
model.train(
    data='tiktok_comments.yaml',  # Конфиг датасета
    epochs=100,
    imgsz=640,
    batch=16,
    device='mps',  # Apple Silicon
    project='tiktok_yolo',
    name='comment_detection'
)

# Сохранение лучшей модели
# runs/detect/comment_detection/weights/best.pt
```

**tiktok_comments.yaml:**
```yaml
path: ./data/tiktok
train: images/train
val: images/val

names:
  0: comment_text
  1: reply_button
  2: input_field
  3: send_button
  4: like_button
```

---

### **Шаг 4: Интеграция в макрос**

```python
from ultralytics import YOLO
import pyautogui

# Загрузка обученной модели
model = YOLO('models/tiktok_comments_best.pt')

# Скриншот
screenshot = pyautogui.screenshot()

# Детекция
results = model(screenshot, conf=0.5)

# Обработка результатов
for result in results:
    boxes = result.boxes
    
    for box in boxes:
        cls = int(box.cls[0])
        conf = float(box.conf[0])
        x1, y1, x2, y2 = box.xyxy[0].tolist()
        
        class_name = model.names[cls]
        
        if class_name == 'comment_text':
            # Найден комментарий
            print(f"📝 Комментарий: ({x1}, {y1}, {x2}, {y2})")
            
            # OCR для чтения текста
            comment_region = screenshot.crop((x1, y1, x2, y2))
            text = ocr.extract(comment_region)
            
        elif class_name == 'reply_button':
            # Найдена кнопка ответа
            center_x = (x1 + x2) / 2
            center_y = (y1 + y2) / 2
            pyautogui.click(center_x, center_y)
```

---

## 🚀 Полный пример использования

```python
#!/usr/bin/env python3
"""
TikTok Auto-Reply Bot с YOLO
"""
from ultralytics import YOLO
import pyautogui
import easyocr
from openai import OpenAI

# Инициализация
yolo_model = YOLO('models/tiktok_comments_best.pt')
ocr_reader = easyocr.Reader(['ru', 'en'])
llm_client = OpenAI()

def find_and_reply():
    # 1. Скриншот
    screenshot = pyautogui.screenshot()
    
    # 2. YOLO детекция
    results = yolo_model(screenshot, conf=0.6)
    
    comment_box = None
    reply_button = None
    
    for result in results:
        for box in result.boxes:
            cls = yolo_model.names[int(box.cls[0])]
            coords = box.xyxy[0].tolist()
            
            if cls == 'comment_text' and not comment_box:
                comment_box = coords
            elif cls == 'reply_button' and not reply_button:
                reply_button = coords
    
    if not comment_box or not reply_button:
        print("❌ Комментарий или кнопка не найдены")
        return False
    
    # 3. OCR - чтение комментария
    x1, y1, x2, y2 = comment_box
    comment_img = screenshot.crop((x1, y1, x2, y2))
    ocr_results = ocr_reader.readtext(np.array(comment_img))
    
    if not ocr_results:
        print("❌ Текст не распознан")
        return False
    
    comment_text = ' '.join([r[1] for r in ocr_results])
    print(f"📝 Комментарий: {comment_text}")
    
    # 4. LLM - генерация ответа
    response = llm_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Ты дружелюбный помощник. Отвечай коротко."},
            {"role": "user", "content": f"Ответь на комментарий: {comment_text}"}
        ],
        max_tokens=50
    )
    
    reply_text = response.choices[0].message.content
    print(f"💬 Ответ: {reply_text}")
    
    # 5. Клик на кнопку "Ответить"
    rx1, ry1, rx2, ry2 = reply_button
    center_x = (rx1 + rx2) / 2
    center_y = (ry1 + ry2) / 2
    pyautogui.click(center_x, center_y)
    time.sleep(0.5)
    
    # 6. Ввод ответа
    pyautogui.write(reply_text, interval=0.05)
    time.sleep(0.3)
    
    # 7. Отправка
    pyautogui.press('enter')
    
    print("✅ Ответ отправлен!")
    return True

# Запуск
if __name__ == '__main__':
    print("⏳ 5 секунд для переключения на TikTok...")
    time.sleep(5)
    
    find_and_reply()
```

---

## 💡 Преимущества YOLO подхода

### **vs Фиксированные координаты:**
- ✅ Работает на любом разрешении
- ✅ Не зависит от позиции элементов
- ✅ Адаптируется к изменениям UI

### **vs Template Matching:**
- ✅ Распознает элементы с разным дизайном
- ✅ Работает при изменении темы
- ✅ Находит частично видимые элементы

---

## 🎯 Рекомендации

### **Для начала:**
1. Собери 100-200 скриншотов TikTok
2. Разметь только `comment_text` и `reply_button`
3. Обучи базовую модель (50 эпох)
4. Протестируй на реальных видео

### **Для продакшена:**
1. Собери 500+ скриншотов
2. Разметь все классы
3. Обучи 100-200 эпох
4. Добавь аугментацию данных
5. Используй ансамбль моделей

---

## 📦 Установка зависимостей

```bash
# YOLO
pip install ultralytics

# OCR
pip install easyocr
# или
pip install pytesseract

# LLM
pip install openai
# или
pip install anthropic

# Дополнительно
pip install pillow numpy opencv-python
```

---

## 🔗 Ресурсы

- [Ultralytics YOLO](https://docs.ultralytics.com/)
- [EasyOCR](https://github.com/JaidedAI/EasyOCR)
- [Roboflow](https://roboflow.com) - Разметка данных
- [LabelImg](https://github.com/heartexlabs/labelImg) - Разметка локально

---

**Итог:** YOLO + OCR + LLM = Полностью автоматические ответы на комментарии! 🚀
