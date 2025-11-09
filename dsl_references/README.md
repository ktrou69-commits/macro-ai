# 📚 DSL References - Справочники DSL

## 🎯 Что здесь?

Эта папка содержит **автоматически сгенерированные справочники** DSL команд и шаблонов.

**Файлы создаются утилитой:** `utils/dsl_reference_generator.py`

---

## 📖 Типичные файлы

```
dsl_references/
├── DSL_REFERENCE.txt              # Все шаблоны
├── TikTok_DSL_Reference.txt       # Только TikTok
├── Chrome_DSL_Reference.txt       # Только Chrome
└── Atlas_DSL_Reference.txt        # Только Atlas
```

---

## 🚀 Как создать справочник

### Через main.py (рекомендуется):
```bash
python3 main.py
# → 1. Инструменты
# → 1. DSL Reference Generator
# → Выбрать папку
```

### Напрямую:
```bash
# Все шаблоны
python3 utils/dsl_reference_generator.py

# TikTok
python3 utils/dsl_reference_generator.py \
  --templates-path templates/Chrome/TikTok \
  --output dsl_references/TikTok_DSL_Reference.txt

# Chrome
python3 utils/dsl_reference_generator.py \
  --templates-path templates/Chrome \
  --output dsl_references/Chrome_DSL_Reference.txt
```

---

## 📖 Что содержит справочник

### Раздел 1: DSL Команды
```
click <template>         # Клик
type "<text>"            # Ввод текста
press <key>              # Клавиша
wait <duration>          # Ожидание
repeat <N>:              # Цикл
try:                     # Try/Catch блок
  ...
catch:
  ...
end
log "<message>"          # Логирование
abort                    # Прерывание
```

### Раздел 2: Доступные шаблоны
```
📄 templates/Chrome/TikTok/ChromeSearchField.png
   Доступные имена:
     • ChromeSearchField  ← Используй это!
```

### Раздел 3: Все имена (алфавитный список)
```
  • Chrome-TikTok-Like
  • ChromeApp
  • ChromeSearchField
```

---

## 💡 Использование

### 1. Сгенерируй справочник
```bash
python3 utils/dsl_reference_generator.py --templates-path templates/Chrome/TikTok
```

### 2. Открой файл
```bash
cat dsl_references/DSL_REFERENCE.txt
```

### 3. Найди нужное имя
```
ChromeSearchField ✅
```

### 4. Используй в .atlas
```atlas
click ChromeSearchField
```

---

## 🗑️ Очистка

Справочники можно безопасно удалять - они генерируются заново при необходимости:

```bash
rm dsl_references/*.txt
```

---

## 📚 Документация

- **Генератор:** `utils/DSL_REFERENCE_GENERATOR_README.md`
- **Быстрый старт:** `docs/DSL_REFERENCE_QUICKSTART.md`

---

**Справочники автоматически сохраняются в эту папку!** 📁
