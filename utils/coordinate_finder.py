#!/usr/bin/env python3
"""
coordinate_finder.py
Утилита для нахождения координат на экране

Использование:
    python3 utils/coordinate_finder.py

Управление:
    SPACE       - Сохранить текущую координату
    C           - Очистить все координаты
    ESC         - Выход и сохранение
    Q           - Выход без сохранения
"""

import pyautogui
import time
import json
from datetime import datetime
from pynput import keyboard, mouse
from pathlib import Path


class CoordinateFinder:
    """Интерактивный поиск координат на экране"""
    
    def __init__(self):
        self.coordinates = []
        self.current_pos = (0, 0)
        self.running = True
        self.mouse_listener = None
        self.keyboard_listener = None
        
        # Отключаем fail-safe для удобства
        pyautogui.FAILSAFE = False
        
        print("\n" + "="*70)
        print("🎯 COORDINATE FINDER - Поиск координат на экране")
        print("="*70)
        print("\n📋 Управление:")
        print("   SPACE       - Сохранить текущую координату")
        print("   C           - Очистить все координаты")
        print("   ESC         - Выход и сохранение")
        print("   Q           - Выход без сохранения")
        print("\n💡 Наведи мышь на нужную точку и нажми SPACE")
        print("="*70 + "\n")
    
    def on_mouse_move(self, x, y):
        """Отслеживание позиции мыши"""
        self.current_pos = (x, y)
        # Обновляем вывод в реальном времени
        print(f"\r🖱️  Позиция: ({x:4d}, {y:4d})  |  Сохранено: {len(self.coordinates)}  ", end='', flush=True)
    
    def on_press(self, key):
        """Обработка нажатий клавиш"""
        try:
            # SPACE - сохранить координату
            if key == keyboard.Key.space:
                self.save_coordinate()
            
            # C - очистить
            elif hasattr(key, 'char') and key.char == 'c':
                self.clear_coordinates()
            
            # ESC - выход с сохранением
            elif key == keyboard.Key.esc:
                self.exit_and_save()
            
            # Q - выход без сохранения
            elif hasattr(key, 'char') and key.char == 'q':
                self.exit_without_save()
                
        except AttributeError:
            pass
    
    def save_coordinate(self):
        """Сохранить текущую координату"""
        x, y = self.current_pos
        
        print(f"\n\n✅ Координата сохранена: ({x}, {y})")
        
        # Запрашиваем описание
        description = input("   📝 Описание (Enter для пропуска): ").strip()
        
        coord_data = {
            'x': x,
            'y': y,
            'description': description if description else f"Point {len(self.coordinates) + 1}",
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.coordinates.append(coord_data)
        
        print(f"   💾 Всего сохранено: {len(self.coordinates)}")
        print(f"\n🖱️  Позиция: ({x:4d}, {y:4d})  |  Сохранено: {len(self.coordinates)}  ", end='', flush=True)
    
    def clear_coordinates(self):
        """Очистить все координаты"""
        if self.coordinates:
            print(f"\n\n🗑️  Очищено {len(self.coordinates)} координат")
            self.coordinates = []
        else:
            print("\n\n⚠️  Нет координат для очистки")
        
        x, y = self.current_pos
        print(f"\n🖱️  Позиция: ({x:4d}, {y:4d})  |  Сохранено: {len(self.coordinates)}  ", end='', flush=True)
    
    def exit_and_save(self):
        """Выход с сохранением"""
        print("\n\n" + "="*70)
        
        if not self.coordinates:
            print("⚠️  Нет координат для сохранения")
            self.running = False
            return
        
        print(f"💾 Сохранение {len(self.coordinates)} координат...")
        print("="*70 + "\n")
        
        # Показываем все координаты
        self.display_coordinates()
        
        # Сохраняем в файл
        self.save_to_file()
        
        # Генерируем DSL код
        self.generate_dsl()
        
        # Генерируем YAML код
        self.generate_yaml()
        
        print("\n✅ Готово!")
        self.running = False
    
    def exit_without_save(self):
        """Выход без сохранения"""
        print("\n\n❌ Выход без сохранения")
        self.running = False
    
    def display_coordinates(self):
        """Показать все сохраненные координаты"""
        print("📍 Сохраненные координаты:\n")
        for i, coord in enumerate(self.coordinates, 1):
            print(f"   {i}. ({coord['x']:4d}, {coord['y']:4d}) - {coord['description']}")
    
    def save_to_file(self):
        """Сохранить в JSON файл"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"coordinates_{timestamp}.json"
        filepath = Path("coordinates") / filename
        
        # Создаем папку если нет
        filepath.parent.mkdir(exist_ok=True)
        
        # Сохраняем
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'coordinates': self.coordinates,
                'total': len(self.coordinates),
                'created_at': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Сохранено в: {filepath}")
    
    def generate_dsl(self):
        """Генерировать DSL код"""
        print("\n" + "="*70)
        print("📝 DSL КОД (.atlas):")
        print("="*70)
        
        for coord in self.coordinates:
            print(f"# {coord['description']}")
            print(f"click ({coord['x']}, {coord['y']})")
            print(f"wait 1s")
            print()
    
    def generate_yaml(self):
        """Генерировать YAML код"""
        print("="*70)
        print("📝 YAML КОД:")
        print("="*70)
        
        for coord in self.coordinates:
            print(f"- action: click")
            print(f"  position: absolute")
            print(f"  x: {coord['x']}")
            print(f"  y: {coord['y']}")
            print(f"  clicks: 1")
            print(f"  description: {coord['description']}")
            print()
    
    def run(self):
        """Запуск утилиты"""
        # Запускаем слушатели
        self.mouse_listener = mouse.Listener(on_move=self.on_mouse_move)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
        # Основной цикл
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\n⚠️  Прервано пользователем")
        finally:
            # Останавливаем слушатели
            self.mouse_listener.stop()
            self.keyboard_listener.stop()
            print("\n")


def main():
    """Главная функция"""
    finder = CoordinateFinder()
    finder.run()


if __name__ == "__main__":
    main()
