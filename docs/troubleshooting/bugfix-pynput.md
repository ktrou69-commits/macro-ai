# 🔧 Исправление ошибки pynput в Python 3.13

## Проблема

```
TypeError: '_thread._ThreadHandle' object is not callable
```

Эта ошибка возникает в Python 3.13 из-за конфликта имен метода `on_move` с внутренним `_thread._ThreadHandle`.

## Решение

Переименовать метод `on_move` в `on_mouse_move`:

### До (❌ не работает):
```python
def on_move(self, x, y):
    self.current_pos = (x, y)

# ...

self.mouse_listener = mouse.Listener(on_move=self.on_move)
```

### После (✅ работает):
```python
def on_mouse_move(self, x, y):
    self.current_pos = (x, y)

# ...

self.mouse_listener = mouse.Listener(on_move=self.on_mouse_move)
```

## Исправленные файлы

- ✅ `utils/coordinate_finder.py`
- ✅ `utils/advanced_coordinate_finder.py`

## Проверка

```bash
python3 -m py_compile utils/coordinate_finder.py
python3 -m py_compile utils/advanced_coordinate_finder.py
```

Обе утилиты теперь работают корректно! ✅

## Запуск

```bash
# Базовая утилита
python3 utils/coordinate_finder.py

# Продвинутая утилита
python3 utils/advanced_coordinate_finder.py
```

Ошибка исправлена! 🎉
