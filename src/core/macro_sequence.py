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

# AI & Selenium (опциональные импорты)
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.common.action_chains import ActionChains
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium не установлен. Установи: pip install selenium webdriver-manager")

try:
    import easyocr
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("⚠️  EasyOCR не установлен. OCR функции недоступны.")

# Learning System
try:
    from learning import LearningSystem
    LEARNING_AVAILABLE = True
except ImportError:
    LEARNING_AVAILABLE = False
    print("⚠️  Learning System не установлен. Обучение недоступно.")

# CNN Detector
try:
    from learning.cnn_detector import CNNDetector
    CNN_AVAILABLE = True
except ImportError:
    CNN_AVAILABLE = False
    print("⚠️  CNN Detector недоступен (нужен TensorFlow)")

try:
    from google import genai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️  Gemini API не установлен. Установи: pip install google-genai")

# Настройки
DEFAULT_THRESHOLD = 0.75  # Понижен с 0.86 для лучшего поиска
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
        
        # Selenium & AI
        self.driver = None  # Selenium WebDriver
        self.ocr_reader = None  # EasyOCR reader
        self.ai_model = None  # Gemini AI model
        
        # Learning System
        self.learning_enabled = True  # Включить обучение
        self.learning_system = None
        
        # CNN Detector
        self.cnn_enabled = True  # Включить CNN детектор
        self.cnn_detector = None
        
        # Execution Tracking
        self.execution_state = {
            'sequence_name': '',
            'completed_steps': [],
            'failed_step': None,
            'screenshots': []
        }
        
        self._detect_display_scale()
        self._load_config()
        self._load_templates_library()
        self._load_variables()
        self._init_learning_system()
        self._init_cnn_detector()
    
    def _detect_display_scale(self):
        """Определение Retina scale"""
        screen_size = pyautogui.size()
        screenshot = pyautogui.screenshot()
        
        # PyAutoGUI уже возвращает физическое разрешение
        # Поэтому НЕ нужно масштабировать шаблоны
        # Но нужно корректировать координаты для pyautogui.click()
        if screenshot.width != screen_size.width:
            self.display_scale = screenshot.width / screen_size.width
            print(f"🖥️  Retina Display обнаружен (scale: {self.display_scale}x)")
            print(f"   📐 Логическое разрешение: {screen_size.width}x{screen_size.height}")
            print(f"   📐 Физическое разрешение: {screenshot.width}x{screenshot.height}")
        else:
            self.display_scale = 1.0
    
    def _load_config(self):
        """Загрузка конфига (YAML или DSL .atlas)"""
        if not os.path.exists(self.config_path):
            print(f"❌ Конфиг не найден: {self.config_path}")
            self.config = {'sequences': {}, 'settings': {}}
            return
        
        try:
            # Проверяем расширение файла
            if self.config_path.endswith('.atlas'):
                # DSL формат - конвертируем в YAML
                print(f"🔄 Обнаружен DSL формат (.atlas)")
                from src.core.atlas_dsl_parser import AtlasDSLParser
                parser = AtlasDSLParser()
                parsed = parser.parse_file(self.config_path)
                
                # Создаем структуру конфига
                sequence_name = Path(self.config_path).stem
                self.config = {
                    'sequences': {sequence_name: parsed},
                    'settings': {}
                }
                print(f"✅ DSL конвертирован: {sequence_name}")
            else:
                # Обычный YAML
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
    
    def _init_learning_system(self):
        """Инициализация системы обучения"""
        if not LEARNING_AVAILABLE:
            self.learning_enabled = False
            return
        
        if self.learning_enabled:
            try:
                self.learning_system = LearningSystem(
                    db_path="learning/memory.db",
                    retrain_threshold=100
                )
                print("🧠 Learning System активирована")
            except Exception as e:
                print(f"⚠️  Ошибка инициализации Learning System: {e}")
                self.learning_enabled = False
    
    def _init_cnn_detector(self):
        """Инициализация CNN детектора"""
        if not CNN_AVAILABLE:
            self.cnn_enabled = False
            return
        
        if self.cnn_enabled:
            try:
                self.cnn_detector = CNNDetector(models_dir="learning/models/cnn")
                available_models = self.cnn_detector.get_available_models()
                if available_models:
                    print(f"🧠 CNN Detector активирован ({len(available_models)} моделей)")
                else:
                    print("⚠️  CNN Detector активирован (нет обученных моделей)")
            except Exception as e:
                print(f"⚠️  Ошибка инициализации CNN Detector: {e}")
                self.cnn_enabled = False
    
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
        
        # НЕ масштабируем шаблон, так как PyAutoGUI уже возвращает физическое разрешение
        # Шаблоны должны быть созданы в физическом разрешении (Retina)
        
        self.templates[template_path] = template
        print(f"📥 Загружен шаблон: {Path(template_path).name} ({template.shape[1]}x{template.shape[0]})")
        return template
    
    def _find_all_templates(self, template_path: str, threshold: float = DEFAULT_THRESHOLD) -> list:
        """Поиск ВСЕХ совпадений шаблона на экране"""
        template = self._load_template(template_path)
        if template is None:
            return []
        
        # Захват экрана
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Template matching
        res = cv2.matchTemplate(gray, template, cv2.TM_CCOEFF_NORMED)
        
        # Найти ВСЕ совпадения выше threshold
        locations = np.where(res >= threshold)
        matches = []
        
        h, w = template.shape
        
        for pt in zip(*locations[::-1]):  # Switch x and y
            score = res[pt[1], pt[0]]
            
            # Координаты центра в физическом разрешении
            # Делим на scale для pyautogui.click() (который работает в логическом разрешении)
            center_x = int((pt[0] + w / 2) / self.display_scale)
            center_y = int((pt[1] + h / 2) / self.display_scale)
            
            matches.append({
                'coords': (center_x, center_y),
                'score': float(score),
                'top_left': pt
            })
        
        # Сортировать по score (лучшие первые)
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        # Убрать дубликаты (близкие координаты)
        filtered_matches = []
        for match in matches:
            is_duplicate = False
            for existing in filtered_matches:
                dx = abs(match['coords'][0] - existing['coords'][0])
                dy = abs(match['coords'][1] - existing['coords'][1])
                if dx < 20 and dy < 20:  # Если ближе 20px - дубликат
                    is_duplicate = True
                    break
            if not is_duplicate:
                filtered_matches.append(match)
        
        return filtered_matches
    
    def _find_template(self, template_path: str, threshold: float = DEFAULT_THRESHOLD, index: int = 0) -> Tuple[bool, Optional[Tuple[int, int]], float]:
        """Поиск шаблона на экране (с поддержкой выбора конкретного совпадения)"""
        # Конвертировать index в int если это строка
        if isinstance(index, str):
            try:
                index = int(index)
            except ValueError:
                index = 0
        
        # Найти все совпадения
        matches = self._find_all_templates(template_path, threshold)
        
        if not matches:
            return False, None, 0.0
        
        # Выбрать нужное совпадение по индексу
        if index >= len(matches):
            print(f"⚠️  Индекс {index} вне диапазона (найдено {len(matches)} совпадений), используем первое")
            index = 0
        
        match = matches[index]
        
        if len(matches) > 1:
            print(f"ℹ️  Найдено {len(matches)} совпадений, выбрано #{index + 1}")
        
        return True, match['coords'], match['score']
    
    def _find_template_with_cnn(self, template_path: str, threshold: float = 0.8) -> Tuple[bool, Optional[Tuple[int, int]], float]:
        """
        Поиск с использованием CNN (если модель доступна)
        
        Args:
            template_path: Путь к шаблону
            threshold: Порог уверенности (0-1)
            
        Returns:
            (найдено, координаты, уверенность)
        """
        if not self.cnn_enabled or not self.cnn_detector:
            # Fallback на template matching
            return self._find_template_old(template_path, threshold=DEFAULT_THRESHOLD)
        
        # Проверяем доступность модели
        if not self.cnn_detector.is_model_available(template_path):
            # Модель не обучена, используем template matching
            return self._find_template_old(template_path, threshold=DEFAULT_THRESHOLD)
        
        # Захват экрана
        screenshot = pyautogui.screenshot()
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        
        # CNN детекция
        try:
            found, location, confidence = self.cnn_detector.detect_fast(
                frame, 
                template_path, 
                threshold=threshold
            )
            
            if found:
                # Корректируем координаты для Retina
                center_x = int(location[0] / self.display_scale)
                center_y = int(location[1] / self.display_scale)
                
                self.stats['successful_finds'] += 1
                
                # Запись успеха в Learning System
                if self.learning_enabled and self.learning_system:
                    # Вырезаем область для записи
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    x, y = location
                    region_size = 64  # Размер окна CNN
                    x1 = max(0, x - region_size // 2)
                    y1 = max(0, y - region_size // 2)
                    x2 = min(gray.shape[1], x + region_size // 2)
                    y2 = min(gray.shape[0], y + region_size // 2)
                    
                    region_screenshot = gray[y1:y2, x1:x2]
                    self.learning_system.record_success(
                        template_id=template_path,
                        screenshot=region_screenshot,
                        region=(x1, y1, x2-x1, y2-y1),
                        method="cnn"
                    )
                
                return True, (center_x, center_y), confidence
            else:
                self.stats['failed_finds'] += 1
                
                # Запись неудачи
                if self.learning_enabled and self.learning_system:
                    last_success = self.learning_system.db.get_last_success(template_path)
                    if last_success and last_success['region']:
                        region = last_success['region']
                        x, y, w, h = region
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        if y + h <= gray.shape[0] and x + w <= gray.shape[1]:
                            region_screenshot = gray[y:y+h, x:x+w]
                            self.learning_system.record_failure(
                                template_id=template_path,
                                screenshot=region_screenshot,
                                region=region,
                                method="cnn",
                                context=f"CNN not found, confidence: {confidence:.2f}"
                            )
                
                # Fallback на template matching
                print(f"   ⚠️  CNN не нашел (confidence: {confidence:.2f}), пробуем template matching...")
                return self._find_template_old(template_path, threshold=DEFAULT_THRESHOLD)
                
        except Exception as e:
            print(f"   ⚠️  Ошибка CNN детекции: {e}, fallback на template matching")
            return self._find_template_old(template_path, threshold=DEFAULT_THRESHOLD)
    
    def _find_template_old(self, template_path: str, threshold: float = DEFAULT_THRESHOLD) -> Tuple[bool, Optional[Tuple[int, int]], float]:
        """Старый метод поиска (одно лучшее совпадение)"""
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
            
            # Запись успеха в Learning System
            if self.learning_enabled and self.learning_system:
                region_screenshot = gray[top_left[1]:top_left[1]+h, top_left[0]:top_left[0]+w]
                self.learning_system.record_success(
                    template_id=template_path,
                    screenshot=region_screenshot,
                    region=(top_left[0], top_left[1], w, h),
                    method="template_match"
                )
            
            return True, (center_x, center_y), max_val
        
        self.stats['failed_finds'] += 1
        
        # Запись неудачи в Learning System
        if self.learning_enabled and self.learning_system:
            # Пытаемся найти область где искали (последняя успешная позиция)
            last_success = self.learning_system.db.get_last_success(template_path)
            if last_success and last_success['region']:
                region = last_success['region']
                x, y, w, h = region
                # Делаем скриншот этой области
                if y + h <= gray.shape[0] and x + w <= gray.shape[1]:
                    region_screenshot = gray[y:y+h, x:x+w]
                    self.learning_system.record_failure(
                        template_id=template_path,
                        screenshot=region_screenshot,
                        region=region,
                        method="template_match",
                        context=f"Template not found, score: {max_val:.2f}"
                    )
        
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
        
        # Проверка флага пропуска (кроме selenium_extract)
        if action != 'selenium_extract' and self.variables.get('_skip_steps', False):
            print(f"   ⏭️  Пропущен шаг: {action}")
            return True  # Продолжить, но пропустить
        
        # REPEAT - повторение вложенных шагов
        if action == 'repeat':
            times = step.get('times', 1)
            
            # Обработка переменных в times
            if isinstance(times, str):
                # Если это строка с переменной типа "{reply_count}"
                if times.startswith('{') and times.endswith('}'):
                    var_name = times[1:-1]
                    times = self.variables.get(var_name, 1)
                # Или просто строка с числом
                try:
                    times = int(times)
                except (ValueError, TypeError):
                    print(f"⚠️  Неверное значение times: {times}, используем 1")
                    times = 1
            
            nested_steps = step.get('steps', [])
            
            if not nested_steps:
                print("⚠️  Нет шагов для повторения")
                return True
            
            print(f"🔄 Повторение {times} раз ({len(nested_steps)} шагов)")
            
            for iteration in range(times):
                print(f"\n   ━━━ Итерация {iteration + 1}/{times} ━━━")
                
                for i, nested_step in enumerate(nested_steps, 1):
                    nested_action = nested_step.get('action')
                    nested_desc = nested_step.get('description', nested_action)
                    print(f"   📍 {i}. {nested_desc}")
                    
                    if not self._execute_step(nested_step):
                        print(f"   ❌ Шаг {i} не выполнен")
                        return False
                
                # Пауза между итерациями (кроме последней)
                if iteration < times - 1:
                    time.sleep(0.5)
            
            print(f"\n✅ Повторение завершено ({times} итераций)")
            return True
        
        # CLICK
        elif action == 'click':
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
            templates = step.get('templates')  # Список шаблонов (fallback)
            
            # Если указан список шаблонов, попробуем каждый
            if templates:
                template_list = templates if isinstance(templates, list) else [templates]
            elif template:
                template_list = [template]
            else:
                print("❌ Не указан шаблон или координаты для клика")
                return False
            
            # Поддержка выбора конкретного совпадения
            index = step.get('index', 0)
            
            # Поддержка wait_for_appear и timeout
            wait_for_appear = step.get('wait_for_appear', False)
            timeout = step.get('timeout', 5.0)
            
            # Поддержка custom threshold
            threshold = step.get('threshold', DEFAULT_THRESHOLD)
            
            # По умолчанию всегда ждем 10 секунд перед ошибкой
            default_retry_timeout = 10.0
            
            found = False
            coords = None
            score = 0.0
            used_template = None
            
            # Попробовать каждый шаблон из списка
            for tmpl in template_list:
                if wait_for_appear:
                    print(f"⏳ Ожидание появления шаблона (timeout: {timeout}с, threshold: {threshold})...")
                    start_time = time.time()
                    
                    while time.time() - start_time < timeout:
                        found, coords, score = self._find_template(tmpl, threshold=threshold, index=index)
                        if found:
                            used_template = tmpl
                            break
                        time.sleep(0.5)
                    
                    if found:
                        break
                else:
                    # Повторяем поиск в течение 10 секунд
                    print(f"🔍 Поиск шаблона (макс. {default_retry_timeout}с, threshold: {threshold})...")
                    start_time = time.time()
                    
                    while time.time() - start_time < default_retry_timeout:
                        found, coords, score = self._find_template(tmpl, threshold=threshold, index=index)
                        if found:
                            used_template = tmpl
                            break
                        time.sleep(0.5)
                    
                    if found:
                        break
            
            if not found:
                if len(template_list) > 1:
                    print(f"❌ Ни один из {len(template_list)} шаблонов не найден")
                else:
                    print(f"❌ Шаблон не найден: {template_list[0]} (score: {score:.3f})")
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
            
            # Подставить переменные
            text = text.format(**self.variables)
            
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
            
            # На macOS логика инвертирована:
            # положительное значение = скролл вверх
            # отрицательное значение = скролл вниз
            # На Windows/Linux - наоборот
            import platform
            is_macos = platform.system() == 'Darwin'
            
            # Инвертируем для macOS
            if is_macos:
                scroll_amount = -amount if direction == 'down' else amount
            else:
                scroll_amount = amount if direction == 'down' else -amount
            
            # Выполняем скролл нужное количество раз
            for i in range(clicks):
                pyautogui.scroll(scroll_amount)
                if clicks > 1 and i < clicks - 1:
                    time.sleep(0.3)
            
            emoji = "⬇️" if direction == 'down' else "⬆️"
            print(f"🖱️  Скролл {emoji} {direction}: {abs(scroll_amount)} x{clicks}")
            return True
        
        # SELENIUM ACTIONS
        elif action == 'selenium_init':
            return self._selenium_init(step)
        elif action == 'selenium_connect':
            return self._selenium_connect(step)
        elif action == 'selenium_navigate':
            return self._selenium_navigate(step)
        elif action == 'selenium_find':
            return self._selenium_find(step)
        elif action == 'selenium_extract':
            return self._selenium_extract(step)
        elif action == 'selenium_get_coordinates':
            return self._selenium_get_coordinates(step)
        elif action == 'selenium_click':
            return self._selenium_click(step)
        elif action == 'selenium_type':
            return self._selenium_type(step)
        elif action == 'selenium_scroll':
            return self._selenium_scroll(step)
        elif action == 'selenium_close':
            return self._selenium_close(step)
        
        # AI ACTIONS
        elif action == 'ai_extract_text':
            return self._ai_extract_text(step)
        elif action == 'ai_generate':
            return self._ai_generate(step)
        
        else:
            print(f"❌ Неизвестное действие: {action}")
            return False
    
    # ==================== SELENIUM МЕТОДЫ ====================
    
    def _selenium_init(self, step: dict) -> bool:
        """Инициализация Selenium WebDriver"""
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium недоступен")
            return False
        
        browser = step.get('browser', 'chrome')
        headless = step.get('headless', False)
        url = step.get('url')
        
        try:
            print(f"🌐 Запуск {browser} (headless={headless})...")
            
            if browser == 'chrome':
                options = webdriver.ChromeOptions()
                
                # Путь к Chrome на macOS
                chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                if os.path.exists(chrome_path):
                    options.binary_location = chrome_path
                
                if headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')
                
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            
            if url:
                print(f"📍 Переход на: {url}")
                self.driver.get(url)
            
            print("✅ Selenium инициализирован")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка Selenium: {e}")
            return False
    
    def _selenium_connect(self, step: dict) -> bool:
        """Подключение к существующему браузеру через remote debugging"""
        if not SELENIUM_AVAILABLE:
            print("❌ Selenium недоступен")
            return False
        
        browser = step.get('browser', 'chrome')
        debugger_address = step.get('debugger_address', '127.0.0.1:9222')
        
        try:
            print(f"🔗 Подключение к {browser} на {debugger_address}...")
            
            if browser == 'chrome':
                options = webdriver.ChromeOptions()
                options.add_experimental_option("debuggerAddress", debugger_address)
                
                # Попробовать использовать уже скачанный ChromeDriver
                chromedriver_path = "/tmp/chromedriver_temp/chromedriver-mac-arm64/chromedriver"
                
                if os.path.exists(chromedriver_path):
                    print(f"   ✅ Используем скачанный ChromeDriver: {chromedriver_path}")
                    service = Service(chromedriver_path)
                else:
                    print(f"   ⚠️  Скачиваем ChromeDriver через webdriver-manager...")
                    service = Service(ChromeDriverManager().install())
                
                self.driver = webdriver.Chrome(service=service, options=options)
            
            # Переключаемся на последнюю вкладку (обычно активную)
            try:
                handles = self.driver.window_handles
                if len(handles) > 0:
                    self.driver.switch_to.window(handles[-1])
                    print(f"   ✅ Переключено на вкладку: {self.driver.title[:50]}...")
            except:
                pass
            
            print("✅ Selenium подключен к существующему браузеру")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            print("💡 Убедись что Chrome запущен с --remote-debugging-port=9222")
            print("💡 Или запусти: python3 tests/test_selenium_alt.py (скачает правильный ChromeDriver)")
            return False
    
    def _selenium_navigate(self, step: dict) -> bool:
        """Навигация на URL"""
        if not self.driver:
            print("❌ Selenium не инициализирован")
            return False
        
        url = step.get('url')
        if not url:
            print("❌ URL не указан")
            return False
        
        try:
            print(f"📍 Переход на: {url}")
            self.driver.get(url)
            return True
        except Exception as e:
            print(f"❌ Ошибка навигации: {e}")
            return False
    
    def _selenium_find(self, step: dict) -> bool:
        """Поиск элемента через Selenium"""
        if not self.driver:
            print("❌ Selenium не инициализирован")
            return False
        
        selector = step.get('selector')
        index = step.get('index', 0)
        wait_for_element = step.get('wait_for_element', False)
        timeout = step.get('timeout', 10.0)
        save_element = step.get('save_element')
        
        try:
            if wait_for_element:
                print(f"⏳ Ожидание элемента (timeout: {timeout}с)...")
                wait = WebDriverWait(self.driver, timeout)
                element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            else:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if not elements:
                    print(f"❌ Элемент не найден: {selector}")
                    return False
                element = elements[index]
            
            print(f"✅ Элемент найден: {selector}")
            
            if save_element:
                self.variables[save_element] = element
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
            return False
    
    def _selenium_extract(self, step: dict) -> bool:
        """Извлечение текста элемента через Selenium"""
        if not self.driver:
            print("❌ Selenium не инициализирован")
            return False
        
        selector = step.get('selector')
        index = step.get('index', 0)

        # Конвертировать index в int если это строка
        if isinstance(index, str):
            try:
                index = int(index)
            except ValueError:
                index = 0
        
        save_to = step.get('save_to')
        save_index_to = step.get('save_index_to')  # Сохранить найденный индекс
        save_previous_to = step.get('save_previous_to')  # Сохранить предыдущее значение
        skip_if_same = step.get('skip_if_same', False)  # Пропустить если совпадает с предыдущим
        wait_for_element = step.get('wait_for_element', True)
        timeout = step.get('timeout', 10.0)
        skip_empty = step.get('skip_empty', True)  # Пропускать пустые комментарии
        max_attempts = step.get('max_attempts', 10)  # Максимум попыток
        extract_all = step.get('extract_all', False)  # Извлечь все элементы
        save_all_to = step.get('save_all_to')  # Сохранить все в список
        
        try:
            if wait_for_element:
                print(f"⏳ Ожидание элемента (timeout: {timeout}с)...")
                wait = WebDriverWait(self.driver, timeout)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if not elements:
                print(f"❌ Элемент не найден: {selector}")
                return False
            
            print(f"📊 Найдено элементов: {len(elements)}")
            
            # Если extract_all=True, извлечь все элементы
            if extract_all:
                all_texts = []
                for elem in elements:
                    text = elem.text.strip()
                    if text and len(text) > 5:
                        all_texts.append(text)
                
                if save_all_to:
                    self.variables[save_all_to] = all_texts
                
                print(f"✅ Selenium: извлечено {len(all_texts)} элементов")
                for i, text in enumerate(all_texts[:5]):
                    print(f"   [{i}] {text[:60]}...")
                
                if len(all_texts) > 5:
                    print(f"   ... и еще {len(all_texts) - 5}")
                
                return True
            
            # Если skip_empty=True, ищем первый непустой комментарий
            elif skip_empty:
                original_index = index
                attempts = 0
                
                while attempts < max_attempts:
                    if index >= len(elements):
                        print(f"⚠️  Достигнут конец списка (всего {len(elements)} элементов)")
                        return False
                    
                    element = elements[index]
                    text = element.text.strip()
                    
                    # Фильтруем служебные тексты
                    skip_words = ["Комментарии", "Ответить", "Нравится", "Добавить", "Показать", "Просмотреть"]
                    is_service_text = any(word in text for word in skip_words)
                    
                    if text and len(text) > 5 and not is_service_text:
                        # Нашли комментарий с текстом!
                        if index != original_index:
                            print(f"⏭️  Пропущено комментариев: {index - original_index}")
                        
                        if save_to:
                            self.variables[save_to] = text
                        
                        if save_index_to:
                            self.variables[save_index_to] = index
                        
                        print(f"✅ Selenium: извлечено {len(text)} символов (индекс: {index})")
                        print(f"📝 Текст: {text[:100]}...")
                        return True
                    else:
                        if not text:
                            print(f"   ⏭️  Индекс {index}: пустой (возможно картинка)")
                        else:
                            print(f"   ⏭️  Индекс {index}: служебный текст ({text[:30]}...)")
                        
                        index += 1
                        attempts += 1
                
                print(f"❌ Не найдено комментариев с текстом (проверено {attempts} элементов)")
                return False
            
            else:
                # Обычный режим (без пропуска пустых)
                if index >= len(elements):
                    print(f"⚠️  Индекс {index} вне диапазона (найдено {len(elements)} элементов)")
                    index = 0
                
                element = elements[index]
                text = element.text
                
                if text and save_to:
                    # Проверка на совпадение с предыдущим
                    if skip_if_same and save_previous_to:
                        previous_text = self.variables.get(save_previous_to, '')
                        if text == previous_text:
                            print(f"⏭️  Нет новых сообщений (текст совпадает)")
                            print(f"⏸️  Пауза 10 секунд перед следующей проверкой...")
                            # Установить флаг для пропуска остальных шагов
                            self.variables['_skip_steps'] = True
                            time.sleep(10)
                            return True  # Продолжить цикл, но пропустить шаги
                        else:
                            print(f"✅ Новое сообщение обнаружено!")
                            # Сохранить текущее как предыдущее
                            self.variables[save_previous_to] = text
                            # Сбросить флаг пропуска
                            self.variables['_skip_steps'] = False
                    
                    self.variables[save_to] = text
                    
                    if save_index_to:
                        self.variables[save_index_to] = index
                    
                    print(f"✅ Selenium: извлечено {len(text)} символов")
                    print(f"📝 Текст: {text[:100]}...")
                    return True
                else:
                    print("❌ Текст пустой")
                    return False
            
        except Exception as e:
            print(f"❌ Ошибка извлечения: {e}")
            return False
    
    def _selenium_get_coordinates(self, step: dict) -> bool:
        """Получить координаты элемента через Selenium"""
        if not self.driver:
            print("❌ Selenium не инициализирован")
            return False
        
        selector = step.get('selector')
        index = step.get('index', 0)
        parent_selector = step.get('parent_selector')  # Найти родителя
        
        # Конвертировать index в int если это строка
        if isinstance(index, str):
            try:
                index = int(index)
            except ValueError:
                index = 0
        
        save_x = step.get('save_x', 'element_x')
        save_y = step.get('save_y', 'element_y')
        
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if not elements:
                print(f"❌ Элемент не найден: {selector}")
                return False
            
            if index >= len(elements):
                print(f"⚠️  Индекс {index} вне диапазона (найдено {len(elements)} элементов)")
                index = 0
            
            element = elements[index]
            
            # Если нужен родительский элемент
            if parent_selector:
                try:
                    parent = element.find_element(By.XPATH, f"./ancestor::{parent_selector}")
                    element = parent
                    print(f"   ✅ Найден родитель: {parent_selector}")
                except:
                    print(f"   ⚠️  Родитель не найден, используем исходный элемент")
            
            # Получить координаты и размер
            location = element.location
            size = element.size
            
            # Вычислить центр элемента
            center_x = location['x'] + size['width'] / 2
            center_y = location['y'] + size['height'] / 2
            
            # Сохранить в переменные
            self.variables[save_x] = int(center_x)
            self.variables[save_y] = int(center_y)
            
            print(f"✅ Координаты получены: ({center_x}, {center_y})")
            print(f"   Сохранено: {save_x}={center_x}, {save_y}={center_y}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка получения координат: {e}")
            return False
    
    def _selenium_click(self, step: dict) -> bool:
        """Клик через Selenium"""
        if not self.driver:
            print("❌ Selenium не инициализирован")
            return False
        
        selector = step.get('selector')
        index = step.get('index', 0)
        element = step.get('element')  # или сохраненный элемент
        parent_selector = step.get('parent_selector')  # Селектор родителя
        child_selector = step.get('child_selector')  # Селектор дочернего элемента
        
        # Конвертировать index в int если это строка
        if isinstance(index, str):
            try:
                index = int(index)
            except ValueError:
                index = 0
        
        try:
            if element and isinstance(element, str):
                # Используем сохраненный элемент
                elem = self.variables.get(element)
            else:
                # Ищем по селектору
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                if not elements:
                    print(f"❌ Элемент не найден: {selector}")
                    return False
                
                print(f"   🔍 Найдено элементов: {len(elements)}")
                
                # Если index не указан, ищем видимый элемент в viewport
                if index == 0 and len(elements) > 1:
                    print(f"   👁️  Ищем видимый элемент в viewport...")
                    visible_elem = None
                    for i, el in enumerate(elements):
                        try:
                            # Проверяем видимость в viewport
                            is_visible = self.driver.execute_script("""
                                var elem = arguments[0];
                                var rect = elem.getBoundingClientRect();
                                var windowHeight = window.innerHeight || document.documentElement.clientHeight;
                                var windowWidth = window.innerWidth || document.documentElement.clientWidth;
                                
                                // Элемент в центре экрана (±30% от центра)
                                var centerY = windowHeight / 2;
                                var elemCenterY = rect.top + rect.height / 2;
                                var distanceFromCenter = Math.abs(elemCenterY - centerY);
                                
                                return distanceFromCenter < windowHeight * 0.3;
                            """, el)
                            
                            if is_visible:
                                visible_elem = el
                                print(f"   ✅ Найден видимый элемент #{i}")
                                break
                        except:
                            continue
                    
                    if visible_elem:
                        elem = visible_elem
                    else:
                        print(f"   ⚠️  Видимый элемент не найден, используем #{index}")
                        elem = elements[index]
                else:
                    if index >= len(elements):
                        print(f"⚠️  Индекс {index} вне диапазона (найдено {len(elements)} элементов)")
                        index = 0
                    
                    elem = elements[index]
                
                # Если нужен родительский элемент
                if parent_selector:
                    try:
                        elem = elem.find_element(By.XPATH, parent_selector)
                        print(f"   ✅ Найден родитель: {parent_selector}")
                    except:
                        print(f"   ⚠️  Родитель не найден: {parent_selector}")
                        return False
                
                # Если нужен дочерний элемент
                if child_selector:
                    try:
                        elem = elem.find_element(By.CSS_SELECTOR, child_selector)
                        print(f"   ✅ Найден дочерний элемент: {child_selector}")
                    except:
                        print(f"   ⚠️  Дочерний элемент не найден: {child_selector}")
                        return False
            
            # Человекоподобное поведение
            humanlike = step.get('humanlike', False)  # По умолчанию ВЫКЛЮЧЕНО (только Selenium)
            
            if humanlike:
                print(f"   🤖 Humanlike режим активирован")
                
                # 1. Прокрутка к элементу (если нужно)
                print(f"   📜 Прокрутка к элементу...")
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", elem)
                delay1 = 0.1 + np.random.uniform(0, 0.2)
                print(f"   ⏱️  Пауза {delay1:.2f}s")
                time.sleep(delay1)
                
                # 2. Получаем координаты элемента на экране
                print(f"   📍 Получение координат элемента...")
                try:
                    # Координаты в браузере
                    location = elem.location
                    size = elem.size
                    
                    # Координаты окна браузера
                    window_pos = self.driver.get_window_position()
                    
                    # Центр элемента на экране
                    elem_x = window_pos['x'] + location['x'] + size['width'] / 2
                    elem_y = window_pos['y'] + location['y'] + size['height'] / 2 + 80  # +80 для toolbar
                    
                    print(f"   🎯 Координаты: ({int(elem_x)}, {int(elem_y)})")
                    
                    # 3. Плавное движение РЕАЛЬНОГО курсора
                    print(f"   🖱️  Движение РЕАЛЬНОГО курсора...")
                    current_x, current_y = pyautogui.position()
                    
                    # Плавное движение с случайной траекторией
                    duration = 0.3 + np.random.uniform(0, 0.2)
                    pyautogui.moveTo(elem_x, elem_y, duration=duration, tween=pyautogui.easeInOutQuad)
                    
                    # 4. Пауза после наведения
                    delay2 = 0.15 + np.random.uniform(0, 0.15)
                    print(f"   ⏱️  Hover пауза {delay2:.2f}s")
                    time.sleep(delay2)
                    
                    # 5. Клик через Selenium (DOM)
                    print(f"   👆 Клик через DOM...")
                    elem.click()
                    print(f"✅ Selenium клик выполнен (humanlike + real mouse)")
                    
                except Exception as e:
                    print(f"   ⚠️  Ошибка humanlike: {e}")
                    print(f"   ↩️  Откат на обычный клик...")
                    elem.click()
                    print(f"✅ Selenium клик выполнен (fallback)")
            else:
                # Обычный клик без имитации
                elem.click()
                print(f"🖱️  Selenium клик выполнен")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка клика: {e}")
            return False
    
    def _selenium_type(self, step: dict) -> bool:
        """Ввод текста через Selenium"""
        if not self.driver:
            print("❌ Selenium не инициализирован")
            return False
        
        selector = step.get('selector')
        text = step.get('text', '')
        interval = step.get('interval', 0)  # Интервал между символами (для имитации печати)
        
        # Подставляем переменные
        text = text.format(**self.variables)
        
        try:
            elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            elem.clear()
            
            # Если interval > 0 - печатать посимвольно (имитация)
            if interval > 0:
                print(f"⌨️  Selenium печать (имитация): {text[:50]}...")
                for char in text:
                    elem.send_keys(char)
                    time.sleep(interval)
            else:
                # Обычный ввод
                elem.send_keys(text)
                print(f"⌨️  Selenium ввод: {text[:50]}...")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка ввода: {e}")
            return False
    
    def _selenium_scroll(self, step: dict) -> bool:
        """Скролл через Selenium"""
        if not self.driver:
            print("❌ Selenium не инициализирован")
            return False
        
        direction = step.get('direction', 'down')
        amount = step.get('amount', 300)
        
        try:
            scroll_amount = amount if direction == 'down' else -amount
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount})")
            
            emoji = "⬇️" if direction == 'down' else "⬆️"
            print(f"🖱️  Selenium скролл {emoji}: {amount}px")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка скролла: {e}")
            return False
    
    def _selenium_close(self, step: dict) -> bool:
        """Закрыть Selenium"""
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                print("✅ Selenium закрыт")
                return True
            except Exception as e:
                print(f"❌ Ошибка закрытия: {e}")
                return False
        return True
    
    # ==================== AI МЕТОДЫ ====================
    
    def _ai_extract_text(self, step: dict) -> bool:
        """Извлечение текста (Selenium или OCR)"""
        method = step.get('method', 'selenium')
        fallback = step.get('fallback', 'ocr')
        save_to = step.get('save_to')
        
        text = None
        
        # 1️⃣ Попытка через Selenium
        if method == 'selenium' and self.driver:
            selector = step.get('selector')
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                text = element.text
                print(f"✅ Selenium: извлечено {len(text)} символов")
            except Exception as e:
                print(f"⚠️  Selenium не сработал: {e}")
                
                # 2️⃣ Fallback на OCR
                if fallback == 'ocr':
                    print("🔄 Переключение на OCR...")
                    text = self._ocr_extract(step)
        
        # Или сразу OCR
        elif method == 'ocr':
            text = self._ocr_extract(step)
        
        # Сохраняем в переменную
        if text and save_to:
            self.variables[save_to] = text
            print(f"📝 Текст: {text[:100]}...")
            return True
        else:
            print("❌ Не удалось извлечь текст")
            return False
    
    def _ocr_extract(self, step: dict) -> Optional[str]:
        """Извлечение текста через OCR с предобработкой"""
        if not OCR_AVAILABLE:
            print("❌ EasyOCR недоступен")
            return None
        
        # Инициализация OCR (один раз)
        if not self.ocr_reader:
            print("🔄 Инициализация EasyOCR...")
            self.ocr_reader = easyocr.Reader(['ru', 'en'], gpu=False)
        
        region = step.get('region')
        preprocess = step.get('preprocess', True)  # Предобработка по умолчанию
        
        try:
            # Скриншот региона
            if region and region != 'auto':
                x, y, w, h = region
                screenshot = pyautogui.screenshot(region=(x, y, w, h))
            else:
                # Автопоиск текстового блока (упрощенно - весь экран)
                screenshot = pyautogui.screenshot()
            
            # Конвертация в numpy array
            img_array = np.array(screenshot)
            
            # Предобработка для лучшего распознавания
            if preprocess:
                # Конвертация в grayscale
                if len(img_array.shape) == 3:
                    img_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                else:
                    img_gray = img_array
                
                # Увеличение контраста (CLAHE)
                clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
                img_enhanced = clahe.apply(img_gray)
                
                # Бинаризация (Otsu)
                _, img_binary = cv2.threshold(img_enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                
                # Используем обработанное изображение
                img_array = img_binary
            
            # OCR
            results = self.ocr_reader.readtext(img_array)
            
            # Объединяем весь текст (сортируем по Y-координате для правильного порядка)
            if results:
                # Сортировка по вертикали (Y), затем по горизонтали (X)
                sorted_results = sorted(results, key=lambda r: (r[0][0][1], r[0][0][0]))
                text = ' '.join([result[1] for result in sorted_results])
            else:
                text = ""
            
            if text:
                print(f"✅ OCR: извлечено {len(text)} символов")
                print(f"📝 Текст: {text[:100]}...")
            else:
                print("⚠️  OCR: текст не найден")
            
            return text
            
        except Exception as e:
            print(f"❌ Ошибка OCR: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _ai_generate(self, step: dict) -> bool:
        """Генерация ответа через AI"""
        if not AI_AVAILABLE:
            print("❌ Gemini API недоступен")
            return False
        
        model = step.get('model', 'gemini')
        prompt = step.get('prompt', '')
        save_to = step.get('save_to')
        max_tokens = step.get('max_tokens', 100)
        temperature = step.get('temperature', 0.7)
        
        # Подставляем переменные в промпт
        prompt = prompt.format(**self.variables)
        
        try:
            # Инициализация AI (один раз)
            if not self.ai_model:
                api_key = os.getenv('GEMINI_API_KEY')
                if not api_key:
                    print("❌ GEMINI_API_KEY не найден в переменных окружения")
                    return False
                
                self.ai_model = genai.Client(api_key=api_key)
                print("✅ Gemini API инициализирован")
            
            # Генерация
            print(f"🤖 AI генерация...")
            print(f"   Промпт: {prompt[:100]}...")
            
            response = self.ai_model.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            
            reply = response.text.strip()
            
            # Сохраняем
            if save_to:
                self.variables[save_to] = reply
            
            print(f"✅ AI ответ: {reply}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка AI: {e}")
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
        
        # Инициализация состояния выполнения
        self.execution_state = {
            'sequence_name': sequence_name,
            'completed_steps': [],
            'failed_step': None,
            'screenshots': []
        }
        
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
            
            success = self._execute_step(step)
            
            # Записываем результат
            step_record = {
                **step,
                'index': i,
                'success': success,
                'description': desc
            }
            
            if success:
                self.execution_state['completed_steps'].append(step_record)
            else:
                step_record['error'] = f"Шаг {i} не выполнен"
                self.execution_state['failed_step'] = step_record
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
