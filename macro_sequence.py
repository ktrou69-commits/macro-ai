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
    print("⚠️  EasyOCR не установлен. Установи: pip install easyocr")

try:
    from google import genai
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️  Gemini API не установлен. Установи: pip install google-genai")

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
        
        # Selenium & AI
        self.driver = None  # Selenium WebDriver
        self.ocr_reader = None  # EasyOCR reader
        self.ai_model = None  # Gemini AI model
        
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
            
            # Центр на физическом разрешении
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
            
            found = False
            coords = None
            score = 0.0
            used_template = None
            
            # Попробовать каждый шаблон из списка
            for tmpl in template_list:
                if wait_for_appear:
                    print(f"⏳ Ожидание появления шаблона (timeout: {timeout}с)...")
                    start_time = time.time()
                    
                    while time.time() - start_time < timeout:
                        found, coords, score = self._find_template(tmpl, index=index)
                        if found:
                            used_template = tmpl
                            break
                        time.sleep(0.5)
                    
                    if found:
                        break
                else:
                    found, coords, score = self._find_template(tmpl, index=index)
                    if found:
                        used_template = tmpl
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
                
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
            
            print("✅ Selenium подключен к существующему браузеру")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            print("💡 Убедись что Chrome запущен с --remote-debugging-port=9222")
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
        save_to = step.get('save_to')
        wait_for_element = step.get('wait_for_element', True)
        timeout = step.get('timeout', 10.0)
        
        try:
            if wait_for_element:
                print(f"⏳ Ожидание элемента (timeout: {timeout}с)...")
                wait = WebDriverWait(self.driver, timeout)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            if not elements:
                print(f"❌ Элемент не найден: {selector}")
                return False
            
            if index >= len(elements):
                print(f"⚠️  Индекс {index} вне диапазона (найдено {len(elements)} элементов)")
                index = 0
            
            element = elements[index]
            text = element.text
            
            if text and save_to:
                self.variables[save_to] = text
                print(f"✅ Selenium: извлечено {len(text)} символов")
                print(f"📝 Текст: {text[:100]}...")
                return True
            else:
                print("⚠️  Текст пустой")
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
        element = step.get('element')  # или сохраненный элемент
        
        try:
            if element and isinstance(element, str):
                # Используем сохраненный элемент
                elem = self.variables.get(element)
            else:
                # Ищем по селектору
                elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            
            elem.click()
            print(f"🖱️  Selenium клик: {selector}")
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
        
        # Подставляем переменные
        text = text.format(**self.variables)
        
        try:
            elem = self.driver.find_element(By.CSS_SELECTOR, selector)
            elem.clear()
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
