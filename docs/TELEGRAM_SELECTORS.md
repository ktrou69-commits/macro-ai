# 📱 Telegram Web - Селекторы и примеры

## 🔍 Типы чатов

### **1. Личные чаты (Private)**
```yaml
selector: "li.chatlist-chat[data-peer-type='user']"
```

### **2. Группы (Groups)**
```yaml
selector: "li.chatlist-chat[data-peer-type='chat']"
```

### **3. Каналы (Channels)**
```yaml
selector: "li.chatlist-chat[data-peer-type='channel']"
```

### **4. Все чаты**
```yaml
selector: "li.chatlist-chat"
```

---

## 🔍 Основные селекторы

### **1. Входящие сообщения (от друга)**

```yaml
selector: ".bubble.is-in .translatable-message"
```

**HTML:**
```html
<div class="bubble is-in">
  <span class="translatable-message">Ого</span>
</div>
```

---

### **2. Исходящие сообщения (твои)**

```yaml
selector: ".bubble.is-out .translatable-message"
```

**HTML:**
```html
<div class="bubble is-out">
  <span class="translatable-message">Привет!</span>
</div>
```

---

### **3. ВСЕ сообщения**

```yaml
selector: ".translatable-message"
```

---

### **4. Контейнеры сообщений**

```yaml
selector: ".bubble"
```

**Атрибуты:**
- `data-mid` - ID сообщения
- `data-peer-id` - ID собеседника
- `data-timestamp` - Unix timestamp

---

## 🎯 Примеры использования

### **Пример 1: Извлечь ПОСЛЕДНЕЕ сообщение**

```yaml
- action: selenium_extract
  selector: ".bubble.is-in .translatable-message"
  index: -1  # Последний элемент
  save_to: last_message
  description: Извлечь последнее сообщение
```

**Результат:**
```
✅ Selenium: извлечено 3 символов
📝 Текст: Ого
```

---

### **Пример 2: Извлечь ВСЕ входящие сообщения**

```yaml
- action: selenium_extract
  selector: ".bubble.is-in .translatable-message"
  extract_all: true
  save_all_to: all_messages
  description: Извлечь все сообщения
```

**Результат:**
```
✅ Selenium: извлечено 5 элементов
   [0] Привет!
   [1] Как дела?
   [2] Что делаешь?
   [3] Ого
   [4] Круто!
```

---

### **Пример 3: Извлечь N-ое сообщение**

```yaml
- action: selenium_extract
  selector: ".bubble.is-in .translatable-message"
  index: 2  # Третье сообщение (индекс с 0)
  save_to: message_3
  description: Извлечь 3-е сообщение
```

---

### **Пример 4: Автоответчик**

```yaml
# 1. Извлечь последнее сообщение
- action: selenium_extract
  selector: ".bubble.is-in .translatable-message"
  index: -1
  save_to: last_message

# 2. AI генерирует ответ
- action: ai_generate
  model: gemini-2.0-flash-exp
  prompt: "Ответь на: {last_message}"
  save_to: reply_text

# 3. Кликнуть поле ввода
- action: click
  template: templates/telegram_input.png

# 4. Ввести ответ
- action: type
  text: "{reply_text}"

# 5. Отправить
- action: key
  key: enter
```

---

## 🔧 Как найти селектор для Telegram

### **Метод 1: Chrome DevTools**

1. Открой Telegram Web
2. Нажми **F12**
3. Нажми **Ctrl+Shift+C**
4. Кликни на сообщение
5. Посмотри HTML:

```html
<div class="bubble is-in" data-mid="203072">
  <div class="bubble-content">
    <div class="message">
      <span class="translatable-message">Ого</span>
    </div>
  </div>
</div>
```

6. Создай селектор:
   - Для текста: `.translatable-message`
   - Для контейнера: `.bubble.is-in`

---

### **Метод 2: Selenium Helper (автоматически)**

```bash
python3 sequence_builder.py
```

1. Выбери **5. Selenium Helper**
2. Выбери **4. Автопоиск селекторов**
3. Helper покажет все найденные элементы!

---

## 💡 Советы

### **1. Используй `-1` для последнего элемента**

```yaml
index: -1  # Последнее сообщение (самое новое)
```

### **2. Извлекай только входящие**

```yaml
selector: ".bubble.is-in .translatable-message"  # Только от друга
```

### **3. Фильтруй по времени (advanced)**

```yaml
# Извлечь сообщения за последнюю минуту
selector: ".bubble.is-in[data-timestamp]"
# Дальше фильтровать в Python по timestamp
```

### **4. Используй `extract_all` для массового извлечения**

```yaml
extract_all: true
save_all_to: all_messages  # Список всех сообщений
```

---

## 🚀 Полный пример: Telegram Bot

```yaml
sequences:
  telegram_bot:
    name: "Telegram Auto Reply Bot"
    description: "Отвечает на каждое новое сообщение"
    
    steps:
    # 1. Подключиться
    - action: selenium_connect
      browser: chrome
      debugger_address: "127.0.0.1:9222"
    
    # 2. Цикл: проверять новые сообщения
    - action: repeat
      times: 10
      steps:
      
      # 2.1. Извлечь последнее сообщение
      - action: selenium_extract
        selector: ".bubble.is-in .translatable-message"
        index: -1
        save_to: last_message
      
      # 2.2. AI ответ
      - action: ai_generate
        model: gemini-2.0-flash-exp
        prompt: "Ответь дружелюбно: {last_message}"
        save_to: reply_text
      
      # 2.3. Кликнуть поле ввода
      - action: click
        template: templates/telegram_input.png
      
      # 2.4. Ввести ответ
      - action: type
        text: "{reply_text}"
      
      # 2.5. Отправить
      - action: key
        key: enter
      
      # 2.6. Пауза перед следующей проверкой
      - action: wait
        duration: 10.0

variables:
  ai_model: "gemini-2.0-flash-exp"
```

---

## 📚 Дополнительные селекторы

### **Имя собеседника:**
```yaml
selector: ".chat-info-title"
```

### **Время сообщения:**
```yaml
selector: ".time-inner"
```

### **Непрочитанные сообщения:**
```yaml
selector: ".badge.unread"
```

### **Поле ввода:**
```yaml
selector: ".input-message-input"
```

---

## 🎉 Итог

**Теперь ты можешь:**
- ✅ Извлекать любые сообщения из Telegram
- ✅ Создавать автоответчики
- ✅ Обрабатывать несколько сообщений
- ✅ Интегрировать с AI

**Используй `examples/telegram_auto_reply.yaml` как шаблон!** 🚀
