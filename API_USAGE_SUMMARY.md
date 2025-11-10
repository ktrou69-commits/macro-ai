# 📊 Сводка использования Gemini API

**Все файлы, которые используют Gemini API ключ**

---

## ✅ Статус: Централизовано через `.env`

**Все файлы читают ключ из `.env` автоматически!**

Меняешь ключ в `.env` → работает везде.

---

## 📁 Файлы с Gemini API

### 1. **utils/api_config.py** ⭐ (Новый!)
**Назначение:** Централизованная конфигурация API ключей

**Код:**
```python
class APIConfig:
    def __init__(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
    
    def has_gemini(self) -> bool:
        return bool(self.gemini_key)
    
    def get_gemini_key(self) -> str:
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY не найден!")
        return self.gemini_key
```

**Использование:**
```python
from utils.api_config import api_config
client = genai.Client(api_key=api_config.gemini_key)
```

---

### 2. **main.py**
**Назначение:** Главное меню

**Строка 575:**
```python
gemini_key = os.getenv("GEMINI_API_KEY")
if not gemini_key:
    print("❌ GEMINI_API_KEY не установлен")
    return
client = genai.Client(api_key=gemini_key)
```

**Статус:** ✅ Использует `.env` через `os.getenv()`

---

### 3. **macro_sequence.py**
**Назначение:** Выполнение макросов с AI комментариями

**Строка 1447:**
```python
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ GEMINI_API_KEY не найден")
    return False
self.ai_model = genai.Client(api_key=api_key)
```

**Статус:** ✅ Использует `.env` через `os.getenv()`

---

### 4. **utils/ai_macro_generator.py**
**Назначение:** AI генератор макросов (оптимизированный)

**Строка 32:**
```python
self.gemini_key = os.getenv("GEMINI_API_KEY")

# Использование (строка 338):
if not self.gemini_key:
    print("❌ GEMINI_API_KEY не установлен")
    return None
client = genai.Client(api_key=self.gemini_key)
```

**Статус:** ✅ Использует `.env` через `os.getenv()`

---

### 5. **utils/ai_macro_generator_legacy.py**
**Назначение:** AI генератор макросов (legacy версия)

**Строка 35:**
```python
self.gemini_key = os.getenv("GEMINI_API_KEY")

# Использование (строка 301):
if not self.gemini_key:
    print("❌ GEMINI_API_KEY не установлен")
    return None
client = genai.Client(api_key=self.gemini_key)
```

**Статус:** ✅ Использует `.env` через `os.getenv()`

---

### 6. **utils/prompt_updater.py**
**Назначение:** Автоматическое обновление промптов

**Строка 34:**
```python
self.gemini_key = os.getenv("GEMINI_API_KEY")

# Использование (строка 121):
if not self.gemini_key:
    print("❌ GEMINI_API_KEY не установлен")
    return None
client = genai.Client(api_key=self.gemini_key)
```

**Статус:** ✅ Использует `.env` через `os.getenv()`

---

### 7. **utils/ai_dom_analyzer.py**
**Назначение:** AI анализ DOM структуры

**Строка 50:**
```python
self.api_key = api_key or os.getenv('GEMINI_API_KEY')

if not self.api_key:
    raise ValueError("GEMINI_API_KEY не найден!")

self.client = genai.Client(api_key=self.api_key)
```

**Статус:** ✅ Использует `.env` через `os.getenv()`

---

### 8. **utils/dom_selector_tool.py**
**Назначение:** DOM селектор с AI анализом

**Строка 45:**
```python
api_key = os.getenv('GEMINI_API_KEY')

if GEMINI_AVAILABLE and api_key:
    try:
        self.ai_analyzer = AIDOMAnalyzer(api_key=api_key)
    except Exception as e:
        print(f"⚠️  Ошибка инициализации AI: {e}")
```

**Статус:** ✅ Использует `.env` через `os.getenv()`

---

### 9. **tests/test_gemini.py**
**Назначение:** Тест Gemini API

**Строка 27:**
```python
from utils.api_config import APIConfig

config = APIConfig()
if not config.has_gemini():
    print("❌ GEMINI_API_KEY не найден в .env")
    sys.exit(1)

client = genai.Client(api_key=config.get_gemini_key())
```

**Статус:** ✅ Использует `.env` через `APIConfig` (обновлено!)

**Было:** Хардкод `'AIzaSyBGlFjt6bKJLJqcsavArM6wb7voH111gc8'`  
**Стало:** Читает из `.env`

---

## 📊 Итоговая статистика

| Файл | Использует .env | Хардкод | Статус |
|------|----------------|---------|--------|
| utils/api_config.py | ✅ | ❌ | ⭐ Новый |
| main.py | ✅ | ❌ | ✅ OK |
| macro_sequence.py | ✅ | ❌ | ✅ OK |
| utils/ai_macro_generator.py | ✅ | ❌ | ✅ OK |
| utils/ai_macro_generator_legacy.py | ✅ | ❌ | ✅ OK |
| utils/prompt_updater.py | ✅ | ❌ | ✅ OK |
| utils/ai_dom_analyzer.py | ✅ | ❌ | ✅ OK |
| utils/dom_selector_tool.py | ✅ | ❌ | ✅ OK |
| tests/test_gemini.py | ✅ | ❌ | ✅ Исправлено |

**Итого:**
- ✅ **9 файлов** используют Gemini API
- ✅ **Все** читают ключ из `.env`
- ✅ **0** хардкодов (был 1, исправлен)
- ✅ **100%** централизация

---

## 🎯 Как это работает

### 1. Ключ в `.env`:
```bash
GEMINI_API_KEY=AIzaSyBGlFjt6bKJLJqcsavArM6wb7voH111gc8
```

### 2. Загрузка в коде:
```python
# Вариант 1: Прямо
import os
api_key = os.getenv("GEMINI_API_KEY")

# Вариант 2: Через APIConfig (рекомендуется)
from utils.api_config import api_config
api_key = api_config.gemini_key
```

### 3. Использование:
```python
from google import genai
client = genai.Client(api_key=api_key)
```

---

## 🔄 Как сменить ключ

### Шаг 1: Откройте `.env`
```bash
nano .env
```

### Шаг 2: Измените ключ
```bash
GEMINI_API_KEY=NEW_KEY_HERE
```

### Шаг 3: Сохраните

**Готово!** Все 9 файлов автоматически используют новый ключ.

---

## ✅ Проверка

### Тест 1: Проверить что ключ загружается
```bash
python3 utils/api_config.py
```

**Ожидаемый вывод:**
```
📊 Статус API ключей:
   Gemini:    ✅ Установлен
```

### Тест 2: Проверить что API работает
```bash
python3 tests/test_gemini.py
```

**Ожидаемый вывод:**
```
✅ Gemini API инициализирован
🎉 Gemini API работает корректно!
```

### Тест 3: Проверить AI генератор
```bash
python3 utils/ai_macro_generator.py "тестовый макрос"
```

**Ожидаемый вывод:**
```
🤖 ОПТИМИЗИРОВАННЫЙ AI ГЕНЕРАТОР
🤖 Генерация через Google Gemini...
```

---

## 🆘 Troubleshooting

### Проблема: "GEMINI_API_KEY не найден"

**Причина:** Ключ не установлен в `.env`

**Решение:**
```bash
# 1. Проверьте .env
cat .env | grep GEMINI_API_KEY

# 2. Если нет - добавьте
echo "GEMINI_API_KEY=your-key-here" >> .env

# 3. Проверьте
python3 utils/api_config.py
```

### Проблема: "Quota exceeded"

**Причина:** Исчерпана квота API

**Решение:**
1. Получите новый ключ: https://makersuite.google.com/app/apikey
2. Обновите `.env`:
   ```bash
   nano .env
   # GEMINI_API_KEY=new-key
   ```
3. Сохраните и перезапустите

---

## 📚 Документация

- **API_CONFIG_GUIDE.md** - Подробное руководство по использованию
- **utils/api_config.py** - Исходный код конфигурации
- **.env** - Файл с ключами (не в git!)

---

## 🎉 Итог

### ✅ Что сделано:
1. Создан `utils/api_config.py` - централизованная конфигурация
2. Убран хардкод из `tests/test_gemini.py`
3. Все 9 файлов используют `.env`
4. Создана документация

### ✅ Результат:
**Меняешь ключ в `.env` → автоматически работает в 9 файлах!**

**Больше не нужно искать и менять ключи в коде!** 🎉
