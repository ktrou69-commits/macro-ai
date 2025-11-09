# 📚 DSL Reference Generator - Быстрый старт

## 🎯 Что это?

Утилита которая создает **текстовый справочник** со всеми:
- ✅ DSL командами (open, click, wait, ...)
- ✅ Именами шаблонов (ChromeSearchField, Like, ...)

**Зачем?** Чтобы не гадать какие имена использовать в `.atlas` файлах!

---

## 🚀 Использование

### Все шаблоны
```bash
python3 utils/dsl_reference_generator.py
```

### Конкретная папка
```bash
# TikTok
python3 utils/dsl_reference_generator.py --templates-path templates/Chrome/TikTok

# Chrome
python3 utils/dsl_reference_generator.py --templates-path templates/Chrome

# Atlas
python3 utils/dsl_reference_generator.py --templates-path templates/Atlas
```

### Свой файл
```bash
python3 utils/dsl_reference_generator.py --output my_reference.txt
```

---

## 📖 Что в справочнике

### 1. DSL Команды
```
click <template>         # Клик
type "<text>"            # Ввод текста
press <key>              # Клавиша
wait <duration>          # Ожидание
repeat <N>:              # Цикл
```

### 2. Доступные шаблоны
```
📄 templates/Chrome/TikTok/ChromeSearchField.png
   Доступные имена:
     • ChromeSearchField  ← Используй это!
```

### 3. Все имена (алфавитный список)
```
  • Chrome-TikTok-Like
  • ChromeApp
  • ChromeSearchField
  • Like
```

---

## 💡 Workflow

```bash
# 1. Сгенерируй справочник
python3 utils/dsl_reference_generator.py --templates-path templates/Chrome/TikTok

# 2. Открой справочник
cat DSL_REFERENCE.txt

# 3. Найди нужное имя
# ChromeSearchField ✅

# 4. Используй в .atlas
click ChromeSearchField
```

---

## 🎯 Примеры

### TikTok справочник
```bash
python3 utils/dsl_reference_generator.py \
  --templates-path templates/Chrome/TikTok \
  --output TikTok_Reference.txt
```

### Chrome справочник
```bash
python3 utils/dsl_reference_generator.py \
  --templates-path templates/Chrome \
  --output Chrome_Reference.txt
```

---

**Полное руководство:** `utils/DSL_REFERENCE_GENERATOR_README.md`
