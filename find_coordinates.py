#!/usr/bin/env python3
"""
Инструмент для определения координат на экране
Помогает найти координаты кнопок для TikTok бота
"""

import pyautogui
import time
import sys

def find_single_position(name):
    """Определение одной позиции"""
    print(f"\n📍 Определение: {name}")
    print("   1. Наведи мышь на нужное место")
    print("   2. НЕ ДВИГАЙ мышь!")
    
    for i in range(3, 0, -1):
        print(f"   {i}...", end='\r')
        time.sleep(1)
    
    pos = pyautogui.position()
    print(f"\n   ✅ Координаты: x={pos.x}, y={pos.y}")
    
    return pos.x, pos.y

def find_coordinates_interactive():
    """Интерактивное определение всех координат"""
    print("\n" + "="*60)
    print("📍 Инструмент определения координат")
    print("="*60)
    print("\n💡 Инструкция:")
    print("   1. Открой TikTok с комментариями")
    print("   2. Следуй инструкциям на экране")
    print("   3. Наводи мышь и жди 3 секунды")
    print("\n⚠️  НЕ ДВИГАЙ мышь во время отсчета!\n")
    
    input("Нажми Enter когда будешь готов...")
    
    # Задержка для переключения на TikTok
    print("\n⏳ 5 секунд для переключения на TikTok...")
    for i in range(5, 0, -1):
        print(f"   {i}...", end='\r')
        time.sleep(1)
    print()
    
    coords = {}
    
    # 1. Первый комментарий (или кнопка "Ответить")
    print("\n" + "-"*60)
    print("1️⃣  ПЕРВЫЙ КОММЕНТАРИЙ")
    print("-"*60)
    print("Наведи мышь на ПЕРВЫЙ комментарий в списке")
    print("(или на кнопку 'Ответить' под ним)")
    
    coords['reply_button'] = find_single_position("Кнопка ответа / Первый комментарий")
    
    # 2. Поле ввода комментария
    print("\n" + "-"*60)
    print("2️⃣  ПОЛЕ ВВОДА")
    print("-"*60)
    print("Сначала КЛИКНИ на первый комментарий чтобы открыть ответы")
    input("Кликнул? Нажми Enter...")
    
    print("\nТеперь наведи мышь на ПОЛЕ ВВОДА комментария")
    print("(там где написано 'Добавить комментарий...')")
    
    coords['input_field'] = find_single_position("Поле ввода комментария")
    
    # Результаты
    print("\n" + "="*60)
    print("✅ Координаты определены!")
    print("="*60)
    print(f"\n📍 Кнопка ответа: x={coords['reply_button'][0]}, y={coords['reply_button'][1]}")
    print(f"📍 Поле ввода: x={coords['input_field'][0]}, y={coords['input_field'][1]}")
    
    # Сохранение в файл
    print("\n💾 Сохранение координат...")
    
    with open('tiktok_coordinates.txt', 'w') as f:
        f.write(f"# TikTok координаты\n")
        f.write(f"# Определены: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"reply_button_x = {coords['reply_button'][0]}\n")
        f.write(f"reply_button_y = {coords['reply_button'][1]}\n\n")
        f.write(f"input_field_x = {coords['input_field'][0]}\n")
        f.write(f"input_field_y = {coords['input_field'][1]}\n")
    
    print("✅ Сохранено в: tiktok_coordinates.txt")
    
    # Код для вставки в бота
    print("\n" + "="*60)
    print("📋 Код для вставки в бота:")
    print("="*60)
    print(f"""
self.reply_button_pos = ({coords['reply_button'][0]}, {coords['reply_button'][1]})
self.input_field_pos = ({coords['input_field'][0]}, {coords['input_field'][1]})
""")
    
    return coords

def quick_position():
    """Быстрое определение текущей позиции мыши"""
    print("\n" + "="*60)
    print("🖱️  Быстрое определение позиции")
    print("="*60)
    print("\n💡 Наведи мышь на нужное место и жди...")
    print("⚠️  Нажми Ctrl+C для остановки\n")
    
    try:
        while True:
            pos = pyautogui.position()
            print(f"   Позиция: x={pos.x:4d}, y={pos.y:4d}", end='\r')
            time.sleep(0.1)
    except KeyboardInterrupt:
        pos = pyautogui.position()
        print(f"\n\n✅ Финальная позиция: x={pos.x}, y={pos.y}")

def test_coordinates():
    """Тест сохраненных координат"""
    print("\n" + "="*60)
    print("🧪 Тест координат")
    print("="*60)
    
    try:
        with open('tiktok_coordinates.txt', 'r') as f:
            lines = f.readlines()
            
        coords = {}
        for line in lines:
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=')
                coords[key.strip()] = int(value.strip())
        
        print("\n📍 Загруженные координаты:")
        print(f"   Кнопка ответа: x={coords.get('reply_button_x')}, y={coords.get('reply_button_y')}")
        print(f"   Поле ввода: x={coords.get('input_field_x')}, y={coords.get('input_field_y')}")
        
        print("\n🖱️  Тест кликов...")
        print("⏳ 5 секунд для переключения на TikTok...")
        time.sleep(5)
        
        # Тест клика на кнопку ответа
        print("\n1. Клик на кнопку ответа...")
        pyautogui.click(coords['reply_button_x'], coords['reply_button_y'])
        time.sleep(1)
        
        # Тест клика на поле ввода
        print("2. Клик на поле ввода...")
        pyautogui.click(coords['input_field_x'], coords['input_field_y'])
        time.sleep(0.5)
        
        # Тест ввода
        print("3. Тест ввода текста...")
        pyautogui.write("Test", interval=0.1)
        
        print("\n✅ Тест завершен!")
        print("⚠️  Проверь что клики попали в нужные места")
        
    except FileNotFoundError:
        print("\n❌ Файл tiktok_coordinates.txt не найден")
        print("   Сначала определи координаты (опция 1)")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")

def main():
    """Главное меню"""
    print("\n" + "="*60)
    print("📍 Инструмент определения координат для TikTok")
    print("="*60)
    
    print("\nВыбери режим:")
    print("1. 🎯 Интерактивное определение (рекомендуется)")
    print("2. 🖱️  Быстрый режим (показывает позицию мыши)")
    print("3. 🧪 Тест сохраненных координат")
    print("4. ❌ Выход")
    
    choice = input("\nВыбор (1/2/3/4): ").strip()
    
    if choice == '1':
        find_coordinates_interactive()
    elif choice == '2':
        quick_position()
    elif choice == '3':
        test_coordinates()
    elif choice == '4':
        print("\n👋 До встречи!")
        sys.exit(0)
    else:
        print("\n⚠️  Неверный выбор")
        main()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Остановлено пользователем")
        sys.exit(0)
