# ✅ Инструкции по установке Gemini API обновлены!

## 🔧 Что исправлено

### Было:
```bash
❌ pip install google-generativeai  # Старый пакет
```

### Стало:
```bash
✅ pip install -q -U google-genai  # Новый официальный SDK
```

---

## 📦 Правильная установка

### 1. Установить Google GenAI SDK

**Python 3.9+:**
```bash
pip install -q -U google-genai
```

### 2. Получить API ключ

1. Перейти на [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Нажать **Get API Key**
3. Создать новый ключ
4. Скопировать ключ

### 3. Установить API ключ

**macOS/Linux:**
```bash
# Временно (для текущей сессии)
export GEMINI_API_KEY='your-api-key-here'

# Постоянно
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.zshrc
source ~/.zshrc
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY = "your-api-key-here"

# Постоянно
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'your-api-key-here', 'User')
```

### 4. Проверить установку

```python
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents="Hello!"
)
print(response.text)
```

**Если работает - всё ОК!** ✅

---

## 📁 Обновленные файлы

```
✅ docs/DOM_AUTOMATION_SUMMARY.md  (добавлена секция установки)
✅ docs/DOM_QUICK_START.md         (обновлены инструкции)
✅ docs/DOM_AUTOMATION_GUIDE.md    (полные инструкции)
✅ docs/GEMINI_SETUP_FIXED.md      (этот файл)
```

---

## 🎯 Использование в коде

### Правильный импорт:

```python
from google import genai  # ✅ Новый SDK

# Старый способ (не используй):
# import google.generativeai as genai  # ❌ Устарел
```

### Инициализация:

```python
# Клиент автоматически получает ключ из GEMINI_API_KEY
client = genai.Client()

# Или явно указать ключ
client = genai.Client(api_key="your-key")
```

### Генерация контента:

```python
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents="Your prompt here"
)
print(response.text)
```

---

## 🔧 Обновление существующего кода

### Если у тебя был старый пакет:

```bash
# Удалить старый
pip uninstall google-generativeai

# Установить новый
pip install -q -U google-genai
```

### Обновить импорты:

**Было:**
```python
import google.generativeai as genai
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.0-flash-exp')
```

**Стало:**
```python
from google import genai
client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.0-flash-exp",
    contents="..."
)
```

---

## 📚 Официальная документация

- **Quickstart:** https://ai.google.dev/gemini-api/docs/quickstart
- **API Reference:** https://ai.google.dev/api
- **Python SDK:** https://pypi.org/project/google-genai/

---

## ✅ Итоги

### Обновлено:
- ✅ Правильный пакет: `google-genai`
- ✅ Правильный импорт: `from google import genai`
- ✅ Инструкции для macOS/Linux/Windows
- ✅ Проверка установки
- ✅ Все документы обновлены

### Теперь работает:
```bash
pip install -q -U google-genai
export GEMINI_API_KEY='your-key'
python3 utils/dom_selector_tool.py
# → 1. Извлечь селектор (AI)
# ✅ Работает!
```

---

**Gemini API настроен правильно! ✅**

**Все инструкции обновлены! 📚**

**Готово к использованию! 🚀**
