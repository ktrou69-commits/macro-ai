# 🔧 Troubleshooting - Решение проблем

## 🚫 Частые проблемы и решения

### 1. Скрипт не делает скриншоты
**Причина:** Нет разрешения Screen Recording
**Решение:** System Settings → Privacy & Security → Screen Recording → добавь Terminal

### 2. Клики не работают
**Причина:** Нет разрешения Accessibility
**Решение:** System Settings → Privacy & Security → Accessibility → добавь Terminal

### 3. Template не находит кнопку
**Решения:**
- Уменьши `TEMPLATE_THRESHOLD = 0.75`
- Захвати новый шаблон: `python utils/capture_button.py`
- Используй grayscale: `USE_GRAYSCALE_TEMPLATE = True`

### 4. YOLO не работает
**Решения:**
```bash
pip install ultralytics torch torchvision
```

### 5. Низкий FPS
**Решения:**
- Установи `MAX_SCREEN_WIDTH = 1280`
- Используй только template без YOLO
- На Apple Silicon: `--device mps`

### 6. MPS не работает
**Решение:**
```bash
pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu
```

### 7. ModuleNotFoundError
**Решение:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### 8. Слишком много кликов
**Решение:** Увеличь `CLICK_COOLDOWN = 1.0`

### 9. Проверка установки
```bash
python test_setup.py
```
