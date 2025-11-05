#!/usr/bin/env python3
"""
macro_sequence.py
Запуск последовательностей макросов
"""

import time
import argparse
import os
import sys
from pathlib import Path
from typing import Optional, Tuple
import yaml

import numpy as np
from PIL import Image
import pyautogui
import cv2
import pyperclip

# Настройки
DEFAULT_THRESHOLD = 0.86
DEFAULT_INTERVAL = 0.5
USE_GRAYSCALE = True

# Безопасность
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


class MacroRunner:
    """Запуск последовательностей макросов"""
    
    def __init__(self, config_path: str = "my_sequences.yaml"):
        self.config_path = config_path
        self.config = {}
        self.templates = {}
        self.templates_library = {}  # Библиотека шаблонов
        self.variables = {}  # Переменные
        self.display_scale = 1.0
        self.stats = {
            'total_clicks': 0,
            'successful_finds': 0,
            'failed_finds': 0,
        }
        
        self._detect_display_scale()
        self._load_config()
        self._load_templates_library()
        self._load_variables()
    
    def _detect_display_scale(self):
        """Определение Retina scale"""
        screen_size = pyautogui.size()
        screenshot = pyautogui.screenshot()
        
        if screenshot.width != screen_size.width:
            self.display_scale = screenshot.width / screen_size.width
            print(f"🖥️  Retina Display обнаружен (scale: {self.display_scale}x)")
    
    def _load_config(self):
        """Загрузка конфига"""
        if not os.path.exists(self.config_path):
            print(f"❌ Конфиг не найден: {self.config_path}")
            self.config = {'sequences': {}, 'settings': {}}
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {'sequences': {}, 'settings': {}}
            
            sequences = self.config.get('sequences', {})
            print(f"✅ Загружено последовательностей: {len(sequences)}")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки конфига: {e}")
            self.config = {'sequences': {}, 'settings': {}}
    
    def _load_templates_library(self):
        """Загрузка библиотеки шаблонов"""
        library_path = "templates_library.yaml"
        if not os.path.exists(library_path):
            return
        
        try:
            with open(library_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self.templates_library = data.get('templates', {})
            print(f"📚 Загружена библиотека шаблонов: {len(self.templates_library)} шаблонов")
        except Exception as e:
            print(f"⚠️  Ошибка загрузки библиотеки: {e}")
    
    def _load_variables(self):
        """Загрузка переменных из конфига"""
        self.variables = self.config.get('variables', {})
        if self.variables:
            print(f"🔧 Загружено переменных: {len(self.variables)}")
            for key, value in self.variables.items():
                print(f"   {key} = {value}")
    
    def _resolve_variable(self, value):
        """Разрешение переменных вида ${var_name}"""
        if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
            var_name = value[2:-1]
            return self.variables.get(var_name, value)
        return value
    
    def _load_template(self, template_path: str) -> Optional[np.ndarray]:
        """Загрузка шаблона"""
        if template_path in self.templates:
            return self.templates[template_path]
        
        if not os.path.exists(template_path):
            print(f"⚠️  Шаблон не найден: {template_path}")
            return None
        
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE if USE_GRAYSCALE else cv2.IMREAD_COLOR)
        
        if template is None:
            print(f"❌ Не удалось загрузить: {template_path}")
            return None
        
        self.templates[template_path] = template
        print(f"📥 Загружен шаблон: {Path(template_path).name} ({template.shape[1]}x{template.shape[0]})")
        return template
    
    def _find_template(self, template_path: str, threshold: float = DEFAULT_THRESHOLD) -> Tuple[bool, Optional[Tuple[int, int]], float]:
        """Поиск шаблона на экране"""
        template = self._load_template(template_path)
        if template is None:
            return False, None, 0.0
        
        # Захват экрана
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Template matching
        res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        if max_val >= threshold:
            h, w = template.shape
            top_left = max_loc
            
            # Центр на физическом разрешении
            center_x = int((top_left[0] + w // 2) / self.display_scale)
            center_y = int((top_left[1] + h // 2) / self.display_scale)
            
            self.stats['successful_finds'] += 1
            return True, (center_x, center_y), max_val
        
        self.stats['failed_finds'] += 1
        return False, None, max_val
    
    def _perform_click(self, x: int, y: int, clicks: int = 1, interval: float = 0.1):
        """Выполнение клика"""
        try:
            pyautogui.click(x, y, clicks=clicks, interval=interval)
            self.stats['total_clicks'] += clicks
            return True
        except Exception as e:
            print(f"❌ Ошибка клика: {e}")
            return False
    
    def _execute_step(self, step: dict) -> bool:
        """Выполнение одного шага"""
        action = step.get('action')
        
        # CLICK
        if action == 'click':
            clicks = step.get('clicks', 1)
            interval = step.get('interval', DEFAULT_INTERVAL)
            
            # Проверяем тип клика: по шаблону или по координатам
            if step.get('position') == 'absolute':
                # Клик по абсолютным координатам (из записи действий)
                x = int(step.get('x', 0))
                y = int(step.get('y', 0))
                print(f"🎯 Клик по координатам: ({x}, {y})")
                return self._perform_click(x, y, clicks, interval)
            
            # Клик по шаблону (template matching)
            template = step.get('template')
            if not template:
                print("❌ Не указан шаблон или координаты для клика")
                return False
            
            # Поддержка wait_for_appear и timeout
            wait_for_appear = step.get('wait_for_appear', False)
            timeout = step.get('timeout', 5.0)
            
            if wait_for_appear:
                print(f"⏳ Ожидание появления шаблона (timeout: {timeout}с)...")
                start_time = time.time()
                found = False
                
                while time.time() - start_time < timeout:
                    found, coords, score = self._find_template(template)
                    if found:
                        break
                    time.sleep(0.5)
                
                if not found:
                    print(f"❌ Шаблон не появился за {timeout}с")
                    return False
            else:
                found, coords, score = self._find_template(template)
                if not found:
                    print(f"❌ Шаблон не найден: {template} (score: {score:.3f})")
                    return False
            
            x, y = coords
            print(f"✅ Найдено! ({x}, {y}) score: {score:.3f}")
            return self._perform_click(x, y, clicks, interval)
        
        # WAIT
        elif action == 'wait':
            duration = self._resolve_variable(step.get('duration', 1.0))
            duration = float(duration)
            print(f"⏸️  Пауза {duration}с")
            time.sleep(duration)
            return True
        
        # TYPE
        elif action == 'type':
            text = step.get('text', '')
            # Проверка на кириллицу
            has_cyrillic = any('\u0400' <= char <= '\u04FF' for char in text)
            
            if has_cyrillic:
                pyperclip.copy(text)
                pyautogui.hotkey('command', 'v')
            else:
                pyautogui.write(text, interval=0.05)
            
            print(f"⌨️  Введено: {text}")
            return True
        
        # KEY
        elif action == 'key':
            key = step.get('key')
            pyautogui.press(key)
            print(f"🔘 Нажата клавиша: {key}")
            return True
        
        # HOTKEY
        elif action == 'hotkey':
            keys = step.get('keys', [])
            pyautogui.hotkey(*keys)
            print(f"🎹 Комбинация: {'+'.join(keys)}")
            return True
        
        # SCROLL
        elif action == 'scroll':
            direction = step.get('direction', 'down')
            amount = step.get('amount', 5)
            clicks = step.get('clicks', 1)
            
            # Проверяем координаты для скролла
            x = step.get('x')
            y = step.get('y')
            
            # Если координаты не указаны - используем центр экрана
            if x is None or y is None:
                screen_size = pyautogui.size()
                x = screen_size.width // 2
                y = screen_size.height // 2
                print(f"📍 Скролл в центре экрана: ({x}, {y})")
            else:
                print(f"📍 Скролл в позиции: ({x}, {y})")
            
            # Перемещаем курсор в нужную позицию
            pyautogui.moveTo(x, y, duration=0.2)
            
            # Выполняем скролл нужное количество раз
            scroll_amount = amount if direction == 'down' else -amount
            for i in range(clicks):
                pyautogui.scroll(scroll_amount)
                if clicks > 1 and i < clicks - 1:
                    time.sleep(0.3)
            
            emoji = "⬇️" if direction == 'down' else "⬆️"
            print(f"🖱️  Скролл {emoji} {direction}: {amount} x{clicks}")
            return True
        
        else:
            print(f"❌ Неизвестное действие: {action}")
            return False
    
    def run_sequence(self, sequence_name: str, delay: int = 3):
        """Запуск последовательности"""
        sequences = self.config.get('sequences', {})
        
        if sequence_name not in sequences:
            print(f"❌ Последовательность не найдена: {sequence_name}")
            print(f"📋 Доступные: {', '.join(sequences.keys())}")
            return False
        
        sequence = sequences[sequence_name]
        steps = sequence.get('steps', [])
        
        # Вывод метаданных
        print("\n" + "="*60)
        print(f"🚀 Запуск: {sequence_name}")
        
        # Название и описание
        if 'name' in sequence and sequence['name'] != sequence_name:
            print(f"📝 Название: {sequence['name']}")
        if 'description' in sequence:
            print(f"📄 Описание: {sequence['description']}")
        if 'platform' in sequence:
            print(f"🌐 Платформа: {sequence['platform']}")
        if 'tags' in sequence:
            print(f"🏷️  Теги: {', '.join(sequence['tags'])}")
        
        print(f"📊 Шагов: {len(steps)}")
        print("="*60)
        
        if delay > 0:
            print(f"\n⏳ Задержка {delay} секунд...")
            for i in range(delay, 0, -1):
                print(f"   {i}...", end='\r', flush=True)
                time.sleep(1)
            print("   Старт!     ")
        
        # Выполнение шагов
        for i, step in enumerate(steps, 1):
            action = step.get('action')
            desc = step.get('description', action)
            
            print(f"\n📍 Шаг {i}/{len(steps)}: {desc}")
            
            if not self._execute_step(step):
                print(f"❌ Шаг {i} не выполнен")
                return False
        
        # Статистика
        print("\n" + "="*60)
        print("✅ Последовательность завершена!")
        print("="*60)
        print(f"📊 Статистика:")
        print(f"   Шагов выполнено: {len(steps)}")
        print(f"   Кликов: {self.stats['total_clicks']}")
        print(f"   Найдено шаблонов: {self.stats['successful_finds']}")
        print("="*60 + "\n")
        
        return True


def main():
    parser = argparse.ArgumentParser(description='Macro AI - Запуск последовательностей')
    parser.add_argument('--config', type=str, default='my_sequences.yaml', help='Путь к конфигу')
    parser.add_argument('--run', type=str, required=True, help='Имя последовательности')
    parser.add_argument('--delay', type=int, default=3, help='Задержка перед стартом (сек)')
    
    args = parser.parse_args()
    
    runner = MacroRunner(args.config)
    runner.run_sequence(args.run, args.delay)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Остановлено пользователем")
        sys.exit(0)
