#!/usr/bin/env python3
"""Тест скролла на macOS"""

import pyautogui
import platform
import time

print("🧪 Тест скролла")
print("="*60)
print(f"🖥️  Система: {platform.system()}")
print()

# Определяем центр экрана
screen_size = pyautogui.size()
center_x = screen_size.width // 2
center_y = screen_size.height // 2

print(f"📍 Центр экрана: ({center_x}, {center_y})")
print()
print("⏳ Через 3 секунды:")
print("   1. Курсор переместится в центр")
print("   2. Скролл ВНИЗ на 15 единиц")
print()

for i in range(3, 0, -1):
    print(f"   {i}...", end='\r', flush=True)
    time.sleep(1)

print("   Старт!     ")

# Перемещаем курсор
pyautogui.moveTo(center_x, center_y, duration=0.2)
print(f"✅ Курсор перемещен в ({center_x}, {center_y})")

# Скролл вниз (для macOS используем отрицательное значение)
is_macos = platform.system() == 'Darwin'
scroll_amount = -15 if is_macos else 15

print(f"🖱️  Выполняю скролл: {scroll_amount}")
pyautogui.scroll(scroll_amount)

print()
print("✅ Готово! Скролл должен был произойти визуально")
print()
print("💡 Если не сработало:")
print("   - Убедись что окно браузера активно")
print("   - Попробуй увеличить значение (например, -30)")
