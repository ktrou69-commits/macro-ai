#!/usr/bin/env python3
"""
advanced_coordinate_finder.py
Продвинутая утилита для нахождения координат и областей на экране

Возможности:
    - Сохранение отдельных точек
    - Определение областей (прямоугольников)
    - Измерение расстояний
    - Визуальные маркеры
    - Экспорт в разные форматы

Использование:
    python3 utils/advanced_coordinate_finder.py

Управление:
    SPACE       - Сохранить точку
    R           - Начать/закончить выделение области (rectangle)
    D           - Измерить расстояние между двумя точками
    M           - Показать/скрыть маркеры
    C           - Очистить все
    S           - Показать сохраненные данные
    ESC         - Выход и сохранение
    Q           - Выход без сохранения
"""

import pyautogui
import time
import json
from datetime import datetime
from pynput import keyboard, mouse
from pathlib import Path
import math


class AdvancedCoordinateFinder:
    """Продвинутый поиск координат и областей"""
    
    def __init__(self):
        self.points = []
        self.rectangles = []
        self.distances = []
        self.current_pos = (0, 0)
        self.running = True
        
        # Режимы работы
        self.mode = 'point'  # point, rectangle, distance
        self.temp_points = []  # Временные точки для режимов
        
        # Слушатели
        self.mouse_listener = None
        self.keyboard_listener = None
        
        pyautogui.FAILSAFE = False
        
        self.print_header()
    
    def print_header(self):
        """Вывод заголовка"""
        print("\n" + "="*80)
        print("🎯 ADVANCED COORDINATE FINDER - Продвинутый поиск координат")
        print("="*80)
        print("\n📋 Управление:")
        print("   SPACE       - Сохранить точку")
        print("   R           - Режим области (rectangle) - выдели 2 точки")
        print("   D           - Режим измерения расстояния - выдели 2 точки")
        print("   M           - Показать маркеры (визуализация)")
        print("   C           - Очистить все")
        print("   S           - Показать сохраненные данные")
        print("   ESC         - Выход и сохранение")
        print("   Q           - Выход без сохранения")
        print("\n💡 Режим: ТОЧКА (нажми R для области, D для расстояния)")
        print("="*80 + "\n")
    
    def on_mouse_move(self, x, y):
        """Отслеживание позиции мыши"""
        self.current_pos = (x, y)
        
        # Статус бар
        mode_emoji = {
            'point': '📍',
            'rectangle': '🔲',
            'distance': '📏'
        }
        
        status = f"\r{mode_emoji.get(self.mode, '📍')} Режим: {self.mode.upper():12s} | "
        status += f"Позиция: ({x:4d}, {y:4d}) | "
        status += f"Точек: {len(self.points)} | Областей: {len(self.rectangles)} | "
        status += f"Расстояний: {len(self.distances)}  "
        
        print(status, end='', flush=True)
    
    def on_press(self, key):
        """Обработка нажатий клавиш"""
        try:
            # SPACE - сохранить точку
            if key == keyboard.Key.space:
                self.handle_space()
            
            # R - режим области
            elif hasattr(key, 'char') and key.char == 'r':
                self.toggle_rectangle_mode()
            
            # D - режим расстояния
            elif hasattr(key, 'char') and key.char == 'd':
                self.toggle_distance_mode()
            
            # M - показать маркеры
            elif hasattr(key, 'char') and key.char == 'm':
                self.show_markers()
            
            # C - очистить
            elif hasattr(key, 'char') and key.char == 'c':
                self.clear_all()
            
            # S - показать данные
            elif hasattr(key, 'char') and key.char == 's':
                self.show_data()
            
            # ESC - выход с сохранением
            elif key == keyboard.Key.esc:
                self.exit_and_save()
            
            # Q - выход без сохранения
            elif hasattr(key, 'char') and key.char == 'q':
                self.exit_without_save()
                
        except AttributeError:
            pass
    
    def handle_space(self):
        """Обработка нажатия SPACE в зависимости от режима"""
        x, y = self.current_pos
        
        if self.mode == 'point':
            # Обычная точка
            self.save_point(x, y)
        
        elif self.mode == 'rectangle':
            # Режим области - нужно 2 точки
            self.temp_points.append((x, y))
            
            if len(self.temp_points) == 1:
                print(f"\n\n📍 Первая точка области: ({x}, {y})")
                print("   💡 Наведи на противоположный угол и нажми SPACE")
            elif len(self.temp_points) == 2:
                self.save_rectangle()
        
        elif self.mode == 'distance':
            # Режим расстояния - нужно 2 точки
            self.temp_points.append((x, y))
            
            if len(self.temp_points) == 1:
                print(f"\n\n📍 Первая точка: ({x}, {y})")
                print("   💡 Наведи на вторую точку и нажми SPACE")
            elif len(self.temp_points) == 2:
                self.save_distance()
    
    def save_point(self, x, y):
        """Сохранить точку"""
        print(f"\n\n✅ Точка сохранена: ({x}, {y})")
        description = input("   📝 Описание (Enter для пропуска): ").strip()
        
        point_data = {
            'x': x,
            'y': y,
            'description': description if description else f"Point {len(self.points) + 1}",
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.points.append(point_data)
        print(f"   💾 Всего точек: {len(self.points)}\n")
    
    def save_rectangle(self):
        """Сохранить область (прямоугольник)"""
        x1, y1 = self.temp_points[0]
        x2, y2 = self.temp_points[1]
        
        # Нормализуем координаты
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        width = right - left
        height = bottom - top
        
        print(f"\n\n✅ Область сохранена:")
        print(f"   📍 Левый верхний: ({left}, {top})")
        print(f"   📍 Правый нижний: ({right}, {bottom})")
        print(f"   📏 Размер: {width} x {height}")
        
        description = input("   📝 Описание (Enter для пропуска): ").strip()
        
        rect_data = {
            'x': left,
            'y': top,
            'width': width,
            'height': height,
            'right': right,
            'bottom': bottom,
            'description': description if description else f"Rectangle {len(self.rectangles) + 1}",
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.rectangles.append(rect_data)
        
        # Сброс режима
        self.temp_points = []
        self.mode = 'point'
        print(f"   💾 Всего областей: {len(self.rectangles)}")
        print(f"   🔄 Режим изменен на: ТОЧКА\n")
    
    def save_distance(self):
        """Сохранить расстояние между точками"""
        x1, y1 = self.temp_points[0]
        x2, y2 = self.temp_points[1]
        
        # Вычисляем расстояние
        distance = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        
        print(f"\n\n✅ Расстояние измерено:")
        print(f"   📍 От: ({x1}, {y1})")
        print(f"   📍 До: ({x2}, {y2})")
        print(f"   📏 Расстояние: {distance:.2f} px")
        print(f"   📐 ΔX: {dx} px, ΔY: {dy} px")
        
        description = input("   📝 Описание (Enter для пропуска): ").strip()
        
        dist_data = {
            'from': {'x': x1, 'y': y1},
            'to': {'x': x2, 'y': y2},
            'distance': round(distance, 2),
            'delta_x': dx,
            'delta_y': dy,
            'description': description if description else f"Distance {len(self.distances) + 1}",
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.distances.append(dist_data)
        
        # Сброс режима
        self.temp_points = []
        self.mode = 'point'
        print(f"   💾 Всего расстояний: {len(self.distances)}")
        print(f"   🔄 Режим изменен на: ТОЧКА\n")
    
    def toggle_rectangle_mode(self):
        """Переключить режим области"""
        if self.mode == 'rectangle':
            self.mode = 'point'
            self.temp_points = []
            print("\n\n🔄 Режим изменен на: ТОЧКА\n")
        else:
            self.mode = 'rectangle'
            self.temp_points = []
            print("\n\n🔄 Режим изменен на: ОБЛАСТЬ")
            print("   💡 Нажми SPACE на первом углу, затем на противоположном\n")
    
    def toggle_distance_mode(self):
        """Переключить режим измерения расстояния"""
        if self.mode == 'distance':
            self.mode = 'point'
            self.temp_points = []
            print("\n\n🔄 Режим изменен на: ТОЧКА\n")
        else:
            self.mode = 'distance'
            self.temp_points = []
            print("\n\n🔄 Режим изменен на: РАССТОЯНИЕ")
            print("   💡 Нажми SPACE на первой точке, затем на второй\n")
    
    def show_markers(self):
        """Показать визуальные маркеры (в консоли)"""
        print("\n\n" + "="*80)
        print("🎨 ВИЗУАЛИЗАЦИЯ МАРКЕРОВ")
        print("="*80 + "\n")
        
        if self.points:
            print("📍 ТОЧКИ:")
            for i, point in enumerate(self.points, 1):
                print(f"   {i}. ({point['x']:4d}, {point['y']:4d}) - {point['description']}")
            print()
        
        if self.rectangles:
            print("🔲 ОБЛАСТИ:")
            for i, rect in enumerate(self.rectangles, 1):
                print(f"   {i}. ({rect['x']}, {rect['y']}) → ({rect['right']}, {rect['bottom']})")
                print(f"      Размер: {rect['width']} x {rect['height']} - {rect['description']}")
            print()
        
        if self.distances:
            print("📏 РАССТОЯНИЯ:")
            for i, dist in enumerate(self.distances, 1):
                print(f"   {i}. ({dist['from']['x']}, {dist['from']['y']}) → ({dist['to']['x']}, {dist['to']['y']})")
                print(f"      Расстояние: {dist['distance']} px - {dist['description']}")
            print()
        
        print("="*80 + "\n")
    
    def show_data(self):
        """Показать все сохраненные данные"""
        self.show_markers()
    
    def clear_all(self):
        """Очистить все данные"""
        total = len(self.points) + len(self.rectangles) + len(self.distances)
        
        if total > 0:
            print(f"\n\n🗑️  Очищено:")
            print(f"   📍 Точек: {len(self.points)}")
            print(f"   🔲 Областей: {len(self.rectangles)}")
            print(f"   📏 Расстояний: {len(self.distances)}\n")
            
            self.points = []
            self.rectangles = []
            self.distances = []
            self.temp_points = []
            self.mode = 'point'
        else:
            print("\n\n⚠️  Нет данных для очистки\n")
    
    def exit_and_save(self):
        """Выход с сохранением"""
        print("\n\n" + "="*80)
        
        total = len(self.points) + len(self.rectangles) + len(self.distances)
        
        if total == 0:
            print("⚠️  Нет данных для сохранения")
            self.running = False
            return
        
        print(f"💾 Сохранение данных...")
        print("="*80 + "\n")
        
        # Показываем все данные
        self.show_markers()
        
        # Сохраняем в файл
        self.save_to_file()
        
        # Генерируем код
        self.generate_dsl()
        self.generate_yaml()
        
        print("\n✅ Готово!")
        self.running = False
    
    def exit_without_save(self):
        """Выход без сохранения"""
        print("\n\n❌ Выход без сохранения")
        self.running = False
    
    def save_to_file(self):
        """Сохранить в JSON"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"coordinates_advanced_{timestamp}.json"
        filepath = Path("coordinates") / filename
        
        filepath.parent.mkdir(exist_ok=True)
        
        data = {
            'points': self.points,
            'rectangles': self.rectangles,
            'distances': self.distances,
            'summary': {
                'total_points': len(self.points),
                'total_rectangles': len(self.rectangles),
                'total_distances': len(self.distances)
            },
            'created_at': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Сохранено в: {filepath}\n")
    
    def generate_dsl(self):
        """Генерировать DSL код"""
        print("="*80)
        print("📝 DSL КОД (.atlas):")
        print("="*80 + "\n")
        
        # Точки
        if self.points:
            print("# === ТОЧКИ ===")
            for point in self.points:
                print(f"# {point['description']}")
                print(f"click ({point['x']}, {point['y']})")
                print(f"wait 1s")
                print()
        
        # Области (для скролла в области)
        if self.rectangles:
            print("# === ОБЛАСТИ (для скролла) ===")
            for rect in self.rectangles:
                center_x = rect['x'] + rect['width'] // 2
                center_y = rect['y'] + rect['height'] // 2
                print(f"# {rect['description']}")
                print(f"# Область: ({rect['x']}, {rect['y']}) → ({rect['right']}, {rect['bottom']})")
                print(f"# Центр области: ({center_x}, {center_y})")
                print(f"scroll down  # В центре области")
                print()
    
    def generate_yaml(self):
        """Генерировать YAML код"""
        print("="*80)
        print("📝 YAML КОД:")
        print("="*80 + "\n")
        
        # Точки
        if self.points:
            print("# === ТОЧКИ ===")
            for point in self.points:
                print(f"- action: click")
                print(f"  position: absolute")
                print(f"  x: {point['x']}")
                print(f"  y: {point['y']}")
                print(f"  clicks: 1")
                print(f"  description: {point['description']}")
                print()
        
        # Области
        if self.rectangles:
            print("# === ОБЛАСТИ ===")
            for rect in self.rectangles:
                center_x = rect['x'] + rect['width'] // 2
                center_y = rect['y'] + rect['height'] // 2
                print(f"# {rect['description']}")
                print(f"# Область: {rect['width']} x {rect['height']}")
                print(f"- action: scroll")
                print(f"  direction: down")
                print(f"  amount: 5")
                print(f"  clicks: 1")
                print(f"  x: {center_x}")
                print(f"  y: {center_y}")
                print()
    
    def run(self):
        """Запуск утилиты"""
        self.mouse_listener = mouse.Listener(on_move=self.on_mouse_move)
        self.keyboard_listener = keyboard.Listener(on_press=self.on_press)
        
        self.mouse_listener.start()
        self.keyboard_listener.start()
        
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n\n⚠️  Прервано пользователем")
        finally:
            self.mouse_listener.stop()
            self.keyboard_listener.stop()
            print("\n")


def main():
    """Главная функция"""
    finder = AdvancedCoordinateFinder()
    finder.run()


if __name__ == "__main__":
    main()
