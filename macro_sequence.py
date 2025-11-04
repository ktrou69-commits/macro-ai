#!/usr/bin/env python3
"""
macro_sequence.py
Макрос с поддержкой последовательностей действий
Поддерживает: множественные клики, ожидание, цепочки действий
"""

import time
import argparse
import os
import sys
from pathlib import Path
from typing import Optional, Tuple, Dict, List, Any
import yaml

import numpy as np
from PIL import Image
import pyautogui
import cv2
import pyperclip

# Настройки
DEFAULT_THRESHOLD = 0.86
DEFAULT_INTERVAL = 0.5
DEFAULT_TIMEOUT = 5
USE_GRAYSCALE = True

# Безопасность
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.05


class SequenceMacro:
    """Макрос с поддержкой последовательностей действий"""
    
    def __init__(self, config_path: str = "sequence_config.yaml"):
        self.config_path = config_path
        self.config = {}
        self.templates = {}  # Кэш загруженных шаблонов
        self.display_scale = 1.0
        self.stats = {
            'total_clicks': 0,
            'successful_finds': 0,
            'failed_finds': 0,
            'sequences_completed': 0
        }
        
        # Определяем Retina scale
        self._detect_display_scale()
        
        # Загружаем конфигурацию
        self._load_config()
        
    def _detect_display_scale(self):
        """Определение scale factor для Retina дисплеев"""
        try:
            img = pyautogui.screenshot()
            physical_w, physical_h = img.size
            logical_w, logical_h = pyautogui.size()
            self.display_scale = physical_w / logical_w
            
            print(f"🖥️  Display: {logical_w}x{logical_h} (scale: {self.display_scale}x)")
        except Exception as e:
            print(f"⚠️  Не удалось определить display scale: {e}")
            self.display_scale = 1.0
    
    def _load_config(self):
        """Загрузка конфигурации из YAML"""
        if not os.path.exists(self.config_path):
            print(f"⚠️  Конфиг не найден: {self.config_path}")
            print(f"💡 Создайте файл {self.config_path} или используйте --interactive режим")
            self.config = {'sequences': {}, 'settings': {}}
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f) or {}
            
            sequences = self.config.get('sequences', {})
            print(f"✅ Загружено последовательностей: {len(sequences)}")
            
            for name, seq in sequences.items():
                steps = len(seq.get('steps', []))
                print(f"   • {name}: {steps} шагов")
                
        except Exception as e:
            print(f"❌ Ошибка загрузки конфига: {e}")
            self.config = {'sequences': {}, 'settings': {}}
    
    def _load_template(self, template_path: str) -> Optional[np.ndarray]:
        """Загрузка и кэширование шаблона"""
        if template_path in self.templates:
            return self.templates[template_path]
        
        if not os.path.exists(template_path):
            print(f"⚠️  Шаблон не найден: {template_path}")
            return None
        
        template = cv2.imread(
            template_path,
            cv2.IMREAD_GRAYSCALE if USE_GRAYSCALE else cv2.IMREAD_COLOR
        )
        
        if template is None:
            print(f"❌ Не удалось загрузить: {template_path}")
            return None
        
        self.templates[template_path] = template
        print(f"📥 Загружен шаблон: {template_path} ({template.shape[1]}x{template.shape[0]})")
        return template
    
    def _find_template(self, template_path: str, threshold: float = None) -> Tuple[bool, Optional[Tuple[int, int]], float]:
        """Поиск шаблона на экране"""
        template = self._load_template(template_path)
        if template is None:
            return False, None, 0.0
        
        if threshold is None:
            threshold = self.config.get('settings', {}).get('threshold', DEFAULT_THRESHOLD)
        
        # Захват экрана
        img = pyautogui.screenshot()
        frame = np.array(img)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Template matching
        res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        
        if max_val >= threshold:
            h, w = template.shape
            top_left = max_loc
            
            # Центр на физическом разрешении
            center_physical = (int(top_left[0] + w/2), int(top_left[1] + h/2))
            
            # Конвертируем в логическое разрешение
            center_logical = (
                int(center_physical[0] / self.display_scale),
                int(center_physical[1] / self.display_scale)
            )
            
            self.stats['successful_finds'] += 1
            return True, center_logical, max_val
        
        self.stats['failed_finds'] += 1
        return False, None, max_val
    
    def _wait_for_template(self, template_path: str, timeout: float = None) -> Tuple[bool, Optional[Tuple[int, int]]]:
        """Ожидание появления шаблона"""
        if timeout is None:
            timeout = self.config.get('settings', {}).get('default_timeout', DEFAULT_TIMEOUT)
        
        print(f"⏳ Ожидание появления: {Path(template_path).name} (макс. {timeout}с)")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            found, coords, score = self._find_template(template_path)
            if found:
                print(f"✅ Найдено! Score: {score:.3f}")
                return True, coords
            time.sleep(0.2)
        
        print(f"⏰ Таймаут: шаблон не найден за {timeout}с")
        return False, None
    
    def _perform_click(self, x: int, y: int, clicks: int = 1, interval: float = 0.0):
        """Выполнение кликов"""
        screen_w, screen_h = pyautogui.size()
        
        if x < 0 or x >= screen_w or y < 0 or y >= screen_h:
            print(f"⚠️  Координаты вне экрана: ({x}, {y})")
            return False
        
        for i in range(clicks):
            pyautogui.click(x, y)
            self.stats['total_clicks'] += 1
            
            if clicks > 1:
                print(f"   🖱️  Клик {i+1}/{clicks} → ({x}, {y})")
            else:
                print(f"🖱️  Клик → ({x}, {y})")
            
            if i < clicks - 1 and interval > 0:
                time.sleep(interval)
        
        return True
    
    def _execute_step(self, step: Dict[str, Any], step_num: int) -> bool:
        """Выполнение одного шага последовательности"""
        action = step.get('action', 'click')
        description = step.get('description', '')
        
        print(f"\n{'='*60}")
        print(f"📍 Шаг {step_num}: {action.upper()}")
        if description:
            print(f"   {description}")
        print(f"{'='*60}")
        
        # CLICK - клик по шаблону или координатам
        if action == 'click':
            template = step.get('template')
            position = step.get('position')
            
            clicks = step.get('clicks', 1)
            interval = step.get('interval', DEFAULT_INTERVAL)
            wait_for_appear = step.get('wait_for_appear', False)
            timeout = step.get('timeout', DEFAULT_TIMEOUT)
            optional = step.get('optional', False)
            
            # Клик по абсолютным координатам
            if position == 'absolute':
                x = step.get('x')
                y = step.get('y')
                
                if x is None or y is None:
                    print("❌ Не указаны координаты x, y для клика")
                    return False
                
                # Конвертируем float в int
                x = int(x)
                y = int(y)
                
                print(f"🖱️  Клик по координатам ({x}, {y}) x{clicks}")
                return self._perform_click(x, y, clicks, interval)
            
            # Клик по шаблону
            if not template:
                print("❌ Не указан шаблон или координаты для клика")
                return False
            
            # Ожидание появления если нужно
            if wait_for_appear:
                found, coords = self._wait_for_template(template, timeout)
                if not found:
                    if optional:
                        print("⚠️  Шаблон не найден, но шаг опциональный - продолжаем")
                        return True
                    return False
            else:
                found, coords, score = self._find_template(template)
                if not found:
                    print(f"❌ Шаблон не найден: {template} (score: {score:.3f})")
                    if optional:
                        print("⚠️  Шаг опциональный - продолжаем")
                        return True
                    return False
                print(f"✅ Найдено! Score: {score:.3f}")
            
            # Выполняем клики
            return self._perform_click(coords[0], coords[1], clicks, interval)
        
        # WAIT - пауза
        elif action == 'wait':
            duration = step.get('duration', 1.0)
            print(f"⏸️  Пауза {duration}с...")
            time.sleep(duration)
            return True
        
        # TYPE - ввод текста
        elif action == 'type':
            text = step.get('text', '')
            method = step.get('method', 'auto')  # auto, clipboard, keyboard
            interval = step.get('interval', 0.05)
            
            print(f"⌨️  Ввод текста: '{text}'")
            
            # Определяем метод ввода
            has_cyrillic = any('\u0400' <= char <= '\u04FF' for char in text)
            
            if method == 'clipboard' or (method == 'auto' and has_cyrillic):
                # Метод через буфер обмена (для кириллицы)
                try:
                    pyperclip.copy(text)
                    pyautogui.hotkey('command', 'v')  # Cmd+V на macOS
                    print(f"   └─ Метод: буфер обмена (кириллица)")
                except Exception as e:
                    print(f"⚠️  Ошибка буфера обмена: {e}")
                    return False
            else:
                # Метод через pyautogui.write (только латиница)
                try:
                    pyautogui.write(text, interval=interval)
                    print(f"   └─ Метод: клавиатура (латиница)")
                except Exception as e:
                    print(f"⚠️  Ошибка ввода: {e}")
                    return False
            
            return True
        
        # KEY - нажатие клавиши
        elif action == 'key':
            key = step.get('key', '')
            presses = step.get('presses', 1)
            print(f"⌨️  Нажатие клавиши: {key} (x{presses})")
            for _ in range(presses):
                pyautogui.press(key)
            return True
        
        # HOTKEY - комбинация клавиш
        elif action == 'hotkey':
            keys = step.get('keys', [])
            print(f"⌨️  Комбинация: {'+'.join(keys)}")
            pyautogui.hotkey(*keys)
            return True
        
        # SCROLL - скролл
        elif action == 'scroll':
            direction = step.get('direction', 'down')  # down, up
            amount = step.get('amount', 3)  # Количество "кликов" колесика
            clicks = step.get('clicks', 1)  # Сколько раз повторить
            pause = step.get('pause', 0.0)  # Пауза между скроллами
            
            # Конвертируем направление в значение для pyautogui
            if direction == 'down':
                scroll_amount = -amount  # Отрицательное = вниз
                direction_text = "⬇️  вниз"
            elif direction == 'up':
                scroll_amount = amount  # Положительное = вверх
                direction_text = "⬆️  вверх"
            else:
                print(f"❌ Неизвестное направление скролла: {direction}")
                return False
            
            print(f"🖱️  Скролл {direction_text} (amount: {amount}, повторов: {clicks})")
            
            for i in range(clicks):
                pyautogui.scroll(scroll_amount)
                if clicks > 1:
                    print(f"   └─ Скролл {i+1}/{clicks}")
                if i < clicks - 1 and pause > 0:
                    time.sleep(pause)
            
            return True
        
        else:
            print(f"❌ Неизвестное действие: {action}")
            return False
    
    def run_sequence(self, sequence_name: str) -> bool:
        """Запуск последовательности по имени"""
        sequences = self.config.get('sequences', {})
        
        if sequence_name not in sequences:
            print(f"❌ Последовательность не найдена: {sequence_name}")
            print(f"💡 Доступные: {', '.join(sequences.keys())}")
            return False
        
        sequence = sequences[sequence_name]
        seq_name = sequence.get('name', sequence_name)
        steps = sequence.get('steps', [])
        repeat = sequence.get('repeat', 1)
        
        print(f"\n{'='*60}")
        print(f"🚀 Запуск последовательности: {seq_name}")
        print(f"📋 Шагов: {len(steps)} | Повторов: {repeat}")
        print(f"{'='*60}\n")
        
        fail_on_error = self.config.get('settings', {}).get('fail_on_not_found', False)
        
        for rep in range(repeat):
            if repeat > 1:
                print(f"\n{'🔄'*20}")
                print(f"🔄 Повтор {rep + 1}/{repeat}")
                print(f"{'🔄'*20}\n")
            
            for i, step in enumerate(steps, 1):
                success = self._execute_step(step, i)
                
                if not success and fail_on_error:
                    print(f"\n❌ Последовательность прервана на шаге {i}")
                    return False
                
                # Небольшая пауза между шагами
                time.sleep(0.1)
        
        self.stats['sequences_completed'] += 1
        print(f"\n{'='*60}")
        print(f"✅ Последовательность завершена успешно!")
        print(f"{'='*60}\n")
        
        return True
    
    def list_sequences(self):
        """Вывод списка доступных последовательностей"""
        sequences = self.config.get('sequences', {})
        
        if not sequences:
            print("📋 Нет доступных последовательностей")
            return
        
        print(f"\n{'='*60}")
        print(f"📋 Доступные последовательности:")
        print(f"{'='*60}\n")
        
        for name, seq in sequences.items():
            seq_name = seq.get('name', name)
            steps = len(seq.get('steps', []))
            repeat = seq.get('repeat', 1)
            
            print(f"• {name}")
            print(f"  Название: {seq_name}")
            print(f"  Шагов: {steps} | Повторов: {repeat}")
            print()
    
    def print_stats(self):
        """Вывод статистики"""
        print(f"\n{'='*60}")
        print(f"📊 Статистика:")
        print(f"{'='*60}")
        print(f"  Последовательностей выполнено: {self.stats['sequences_completed']}")
        print(f"  Всего кликов: {self.stats['total_clicks']}")
        print(f"  Успешных поисков: {self.stats['successful_finds']}")
        print(f"  Неудачных поисков: {self.stats['failed_finds']}")
        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description="🤖 Macro Sequence: выполнение последовательностей действий",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python macro_sequence.py --list                    # Список последовательностей
  python macro_sequence.py --run atlas_new_tab       # Запустить последовательность
  python macro_sequence.py --config my_config.yaml   # Свой конфиг
        """
    )
    
    parser.add_argument('--config', default='sequence_config.yaml',
                       help='Путь к конфигурационному файлу')
    parser.add_argument('--list', action='store_true',
                       help='Показать список последовательностей')
    parser.add_argument('--run', type=str,
                       help='Запустить последовательность по имени')
    
    args = parser.parse_args()
    
    try:
        macro = SequenceMacro(config_path=args.config)
        
        if args.list:
            macro.list_sequences()
        elif args.run:
            success = macro.run_sequence(args.run)
            macro.print_stats()
            sys.exit(0 if success else 1)
        else:
            parser.print_help()
            print("\n💡 Используйте --list для просмотра последовательностей")
            print("💡 Используйте --run <name> для запуска")
            
    except KeyboardInterrupt:
        print("\n\n✋ Остановлено пользователем")
        sys.exit(0)
    except pyautogui.FailSafeException:
        print("\n\n🛑 FAILSAFE активирован!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
