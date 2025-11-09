#!/usr/bin/env python3
"""
simple_coordinate_finder.py
Простая утилита для нахождения координат (без pynput)
Использует только pyautogui - работает на Python 3.13

Использование:
    python3 utils/simple_coordinate_finder.py

Управление:
    Наведи мышь на нужную точку
    Нажми CTRL+C для сохранения координаты
    Нажми CTRL+C дважды для выхода
"""

import pyautogui
import time
import json
from datetime import datetime
from pathlib import Path


class SimpleCoordinateFinder:
    """Простой поиск координат без pynput"""
    
    def __init__(self):
        self.coordinates = []
        self.running = True
        
        pyautogui.FAILSAFE = False
        
        print("\n" + "="*70)
        print("🎯 SIMPLE COORDINATE FINDER - Простой поиск координат")
        print("="*70)
        print("\n📋 Управление:")
        print("   CTRL+C      - Сохранить текущую координату")
        print("   CTRL+C x2   - Выход и сохранение")
        print("\n💡 Наведи мышь на нужную точку и нажми CTRL+C")
        print("="*70 + "\n")
    
    def save_coordinate(self, x, y):
        """Сохранить координату"""
        print(f"\n✅ Координата сохранена: ({x}, {y})")
        description = input("   📝 Описание (Enter для пропуска): ").strip()
        
        coord_data = {
            'x': x,
            'y': y,
            'description': description if description else f"Point {len(self.coordinates) + 1}",
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.coordinates.append(coord_data)
        print(f"   💾 Всего сохранено: {len(self.coordinates)}\n")
    
    def display_coordinates(self):
        """Показать все сохраненные координаты"""
        print("\n📍 Сохраненные координаты:\n")
        for i, coord in enumerate(self.coordinates, 1):
            print(f"   {i}. ({coord['x']:4d}, {coord['y']:4d}) - {coord['description']}")
    
    def save_to_file(self):
        """Сохранить в JSON файл"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"coordinates_simple_{timestamp}.json"
        filepath = Path("coordinates") / filename
        
        filepath.parent.mkdir(exist_ok=True)
        
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
    
    def exit_and_save(self):
        """Выход с сохранением"""
        print("\n\n" + "="*70)
        
        if not self.coordinates:
            print("⚠️  Нет координат для сохранения")
            return
        
        print(f"💾 Сохранение {len(self.coordinates)} координат...")
        print("="*70 + "\n")
        
        self.display_coordinates()
        self.save_to_file()
        self.generate_dsl()
        self.generate_yaml()
        
        print("\n✅ Готово!")
    
    def run(self):
        """Запуск утилиты"""
        consecutive_interrupts = 0
        
        try:
            while self.running:
                # Получаем текущую позицию мыши
                x, y = pyautogui.position()
                
                # Выводим позицию
                print(f"\r🖱️  Позиция: ({x:4d}, {y:4d})  |  Сохранено: {len(self.coordinates)}  ", 
                      end='', flush=True)
                
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            consecutive_interrupts += 1
            
            if consecutive_interrupts == 1:
                # Первое нажатие CTRL+C - сохранить координату
                x, y = pyautogui.position()
                self.save_coordinate(x, y)
                
                # Продолжаем работу
                print("💡 Нажми CTRL+C еще раз для выхода\n")
                self.run()  # Рекурсивный вызов для продолжения
            else:
                # Второе нажатие - выход
                self.exit_and_save()


def main():
    """Главная функция"""
    finder = SimpleCoordinateFinder()
    finder.run()


if __name__ == "__main__":
    main()
