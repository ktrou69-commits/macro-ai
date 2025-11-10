# 📁 Macros

Все макросы проекта организованы здесь.

## 📂 Структура

```
macros/
├── production/          # Готовые к использованию макросы
├── examples/            # Примеры для обучения
│   ├── basic/          # Базовые примеры
│   └── advanced/       # Продвинутые примеры
└── templates/          # Шаблоны для копирования
```

## 🚀 Использование

### Production макросы
```bash
python3 macro_sequence.py --config macros/production/tiktok_likes.atlas --run tiktok_likes
```

### AI генератор
```bash
python3 utils/ai_macro_generator.py "поставить 10 лайков в TikTok"
# Сохранится в macros/production/
```

## 📚 Документация

- [DSL Guide](../docs/guides/dsl/README.md)
- [AI Generator](../docs/guides/ai/README.md)
- [Examples](examples/README.md)
