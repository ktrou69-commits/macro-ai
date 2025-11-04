#!/usr/bin/env python3
"""
sequence_builder.py
Интерактивный конструктор последовательностей макросов
Создавай последовательности прямо в консоли!

Новая архитектура v2.0 - обновленные пути
"""

import os
import sys
import yaml
import time
from pathlib import Path
from typing import List, Dict, Any
from pynput import mouse, keyboard
from pynput.keyboard import Key

# Автономный скрипт - работает без зависимостей

class SequenceBuilder:
    """Интерактивный конструктор последовательностей"""
    
    def __init__(self, config_path: str = "my_sequences.yaml"):
        self.config_path = config_path
        self.config = {'sequences': {}, 'settings': {}}
        self.current_sequence = []
        self.sequence_name = ""
        
        # Для записи действий
        self.recording = False
        self.recorded_actions = []
        self.start_time = None
        self.last_action_time = None
        self.scroll_buffer = []
        self.scroll_timeout = 0.5
        
        # Загружаем существующий конфиг если есть
        self._load_config()
    
    def _load_config(self):
        """Загрузка существующего конфига"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f) or {'sequences': {}, 'settings': {}}
                print(f"✅ Загружен конфиг: {self.config_path}")
                print(f"   Последовательностей: {len(self.config.get('sequences', {}))}")
            except Exception as e:
                print(f"⚠️  Ошибка загрузки конфига: {e}")
                self.config = {'sequences': {}, 'settings': {}}
    
    def _save_config(self):
        """Сохранение конфига"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            print(f"\n✅ Конфиг сохранен: {self.config_path}")
            return True
        except Exception as e:
            print(f"\n❌ Ошибка сохранения: {e}")
            return False
    
    def _show_templates(self):
        """Показать доступные шаблоны"""
        # Ищем шаблоны в папке templates
        templates_dir = Path("templates")
        
        if not templates_dir.exists():
            print("⚠️  Папка templates/ не найдена")
            print("💡 Сначала захвати шаблоны: python3 utils/smart_capture.py")
            return []
        
        templates = list(templates_dir.glob("*.png"))
        
        if not templates:
            print("⚠️  Нет шаблонов в templates/")
            print("💡 Сначала захвати шаблоны: python3 utils/smart_capture.py")
            return []
        
        print("\n📁 Доступные шаблоны:")
        for i, template in enumerate(templates, 1):
            print(f"   {i}. {template.name}")
        
        return templates
    
    def list_templates(self):
        """Показать доступные шаблоны (публичный метод)"""
        return self._show_templates()
    
    def list_sequences(self):
        """Показать существующие последовательности"""
        sequences = self.config.get('sequences', {})
        if not sequences:
            print("\n📋 Нет сохраненных последовательностей")
            return
        
        print("\n📋 Сохраненные последовательности:")
        for name, seq in sequences.items():
            steps = len(seq.get('steps', []))
            desc = seq.get('name', name)
            print(f"   • {name}: {desc} ({steps} шагов)")
    
    def add_click_step(self):
        """Добавить шаг клика"""
        print("\n" + "="*60)
        print("➕ Добавление шага: КЛИК")
        print("="*60)
        
        # Выбор шаблона
        templates = self.list_templates()
        if not templates:
            print("💡 Сначала создай шаблоны: python3 utils/smart_capture.py")
            return False
        
        while True:
            choice = input("\n📝 Номер шаблона (или путь): ").strip()
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(templates):
                    # Используем относительный путь
                    template_path = f"templates/{templates[idx].name}"
                    break
            elif choice:
                # Если указан путь
                if Path(choice).exists():
                    template_path = choice
                    break
                # Пробуем найти в templates/
                full_path = Path("templates") / choice
                if full_path.exists():
                    template_path = f"templates/{choice}"
                    break
                print(f"⚠️  Файл не найден: {choice}")
                continue
            
            print("⚠️  Неверный выбор")
        
        # Количество кликов
        while True:
            clicks_input = input("🖱️  Количество кликов (Enter=1): ").strip()
            if clicks_input == "":
                clicks = 1
                break
            try:
                clicks = int(clicks_input)
                if clicks > 0:
                    break
            except ValueError:
                pass
            print("⚠️  Введи число > 0")
        
        # Интервал между кликами
        interval = 0.0
        if clicks > 1:
            while True:
                interval_input = input("⏱️  Интервал между кликами в сек (Enter=0.3): ").strip()
                if interval_input == "":
                    interval = 0.3
                    break
                try:
                    interval = float(interval_input)
                    if interval >= 0:
                        break
                except ValueError:
                    pass
                print("⚠️  Введи число >= 0")
        
        # Ожидание появления
        wait_for = input("⏳ Ждать появления? (y/n, Enter=n): ").strip().lower()
        wait_for_appear = wait_for == 'y'
        
        timeout = 5
        if wait_for_appear:
            while True:
                timeout_input = input("⏰ Таймаут ожидания в сек (Enter=5): ").strip()
                if timeout_input == "":
                    break
                try:
                    timeout = float(timeout_input)
                    if timeout > 0:
                        break
                except ValueError:
                    pass
                print("⚠️  Введи число > 0")
        
        # Описание
        description = input("📝 Описание (Enter=пропустить): ").strip()
        
        # Создаем шаг
        step = {
            'action': 'click',
            'template': template_path,
            'clicks': clicks
        }
        
        if clicks > 1 and interval > 0:
            step['interval'] = interval
        
        if wait_for_appear:
            step['wait_for_appear'] = True
            step['timeout'] = timeout
        
        if description:
            step['description'] = description
        
        self.current_sequence.append(step)
        
        print(f"\n✅ Шаг добавлен: клик по {Path(template_path).name} x{clicks}")
        return True
    
    def add_wait_step(self):
        """Добавить шаг паузы"""
        print("\n" + "="*60)
        print("➕ Добавление шага: ПАУЗА")
        print("="*60)
        
        while True:
            duration_input = input("⏸️  Длительность паузы в сек (Enter=1.0): ").strip()
            if duration_input == "":
                duration = 1.0
                break
            try:
                duration = float(duration_input)
                if duration > 0:
                    break
            except ValueError:
                pass
            print("⚠️  Введи число > 0")
        
        description = input("📝 Описание (Enter=пропустить): ").strip()
        
        step = {
            'action': 'wait',
            'duration': duration
        }
        
        if description:
            step['description'] = description
        
        self.current_sequence.append(step)
        print(f"\n✅ Шаг добавлен: пауза {duration}с")
        return True
    
    def add_type_step(self):
        """Добавить шаг ввода текста"""
        print("\n" + "="*60)
        print("➕ Добавление шага: ВВОД ТЕКСТА")
        print("="*60)
        
        text = input("⌨️  Текст для ввода: ").strip()
        if not text:
            print("⚠️  Текст не может быть пустым")
            return False
        
        description = input("📝 Описание (Enter=пропустить): ").strip()
        
        step = {
            'action': 'type',
            'text': text
        }
        
        if description:
            step['description'] = description
        
        self.current_sequence.append(step)
        print(f"\n✅ Шаг добавлен: ввод '{text}'")
        return True
    
    def add_key_step(self):
        """Добавить шаг нажатия клавиши"""
        print("\n" + "="*60)
        print("➕ Добавление шага: НАЖАТИЕ КЛАВИШИ")
        print("="*60)
        print("💡 Примеры: enter, tab, esc, space, backspace")
        
        key = input("⌨️  Клавиша: ").strip().lower()
        if not key:
            print("⚠️  Клавиша не может быть пустой")
            return False
        
        description = input("📝 Описание (Enter=пропустить): ").strip()
        
        step = {
            'action': 'key',
            'key': key
        }
        
        if description:
            step['description'] = description
        
        self.current_sequence.append(step)
        print(f"\n✅ Шаг добавлен: нажатие '{key}'")
        return True
    
    def add_hotkey_step(self):
        """Добавить шаг комбинации клавиш"""
        print("\n" + "="*60)
        print("➕ Добавление шага: КОМБИНАЦИЯ КЛАВИШ")
        print("="*60)
        print("💡 Примеры: command+t, command+w, command+shift+n")
        
        hotkey = input("⌨️  Комбинация (через +): ").strip().lower()
        if not hotkey or '+' not in hotkey:
            print("⚠️  Введи комбинацию через +")
            return False
        
        keys = [k.strip() for k in hotkey.split('+')]
        
        description = input("📝 Описание (Enter=пропустить): ").strip()
        
        step = {
            'action': 'hotkey',
            'keys': keys
        }
        
        if description:
            step['description'] = description
        
        self.current_sequence.append(step)
        print(f"\n✅ Шаг добавлен: {'+'.join(keys)}")
        return True
    
    def add_scroll_step(self):
        """Добавить шаг скролла"""
        print("\n" + "="*60)
        print("➕ Добавление шага: СКРОЛЛ")
        print("="*60)
        
        # Направление
        while True:
            direction_input = input("🖱️  Направление (down/up, Enter=down): ").strip().lower()
            if direction_input == "":
                direction = "down"
                break
            elif direction_input in ['down', 'up', 'd', 'u']:
                direction = 'down' if direction_input in ['down', 'd'] else 'up'
                break
            print("⚠️  Введи 'down' или 'up'")
        
        # Количество (сила скролла)
        while True:
            amount_input = input("📏 Сила скролла (Enter=3): ").strip()
            if amount_input == "":
                amount = 3
                break
            try:
                amount = int(amount_input)
                if amount > 0:
                    break
            except ValueError:
                pass
            print("⚠️  Введи число > 0")
        
        # Количество повторов
        while True:
            clicks_input = input("🔄 Количество повторов (Enter=1): ").strip()
            if clicks_input == "":
                clicks = 1
                break
            try:
                clicks = int(clicks_input)
                if clicks > 0:
                    break
            except ValueError:
                pass
            print("⚠️  Введи число > 0")
        
        # Пауза между повторами
        pause = 0.0
        if clicks > 1:
            while True:
                pause_input = input("⏱️  Пауза между повторами в сек (Enter=0): ").strip()
                if pause_input == "":
                    break
                try:
                    pause = float(pause_input)
                    if pause >= 0:
                        break
                except ValueError:
                    pass
                print("⚠️  Введи число >= 0")
        
        # Описание
        description = input("📝 Описание (Enter=пропустить): ").strip()
        
        # Создаем шаг
        step = {
            'action': 'scroll',
            'direction': direction,
            'amount': amount,
            'clicks': clicks
        }
        
        if pause > 0:
            step['pause'] = pause
        
        if description:
            step['description'] = description
        
        self.current_sequence.append(step)
        
        direction_text = "⬇️ вниз" if direction == 'down' else "⬆️ вверх"
        print(f"\n✅ Шаг добавлен: скролл {direction_text} x{clicks}")
        return True
    
    def record_actions_step(self):
        """Записать действия как один или несколько шагов"""
        print("\n" + "="*60)
        print("🎬 Запись действий")
        print("="*60)
        
        # Задержка
        countdown = input("\n⏱️  Задержка перед записью в сек (Enter=3): ").strip()
        countdown = int(countdown) if countdown.isdigit() else 3
        
        print(f"\n💡 Переключись на нужное окно/приложение!")
        print(f"💡 Запись начнется через {countdown} секунд...")
        print(f"💡 Нажми ESC для остановки\n")
        
        for i in range(countdown, 0, -1):
            print(f"   {i}...", end='\r')
            time.sleep(1)
        
        print("\n🔴 ЗАПИСЬ НАЧАЛАСЬ!\n")
        
        # Сброс
        self.recorded_actions = []
        self.recording = True
        self.start_time = time.time()
        self.last_action_time = self.start_time
        self.scroll_buffer = []
        
        # Создаем listeners
        mouse_listener = mouse.Listener(
            on_click=self._on_click,
            on_scroll=self._on_scroll
        )
        
        keyboard_listener = keyboard.Listener(
            on_press=self._on_press
        )
        
        # Запускаем
        mouse_listener.start()
        keyboard_listener.start()
        
        # Ждем остановки
        keyboard_listener.join()
        
        # Останавливаем mouse listener
        mouse_listener.stop()
        
        # Сохраняем оставшиеся скроллы
        self._flush_scroll_buffer()
        
        self.recording = False
        
        # Показываем что записали
        if self.recorded_actions:
            print("\n" + "="*60)
            print(f"✅ Записано действий: {len(self.recorded_actions)}")
            print("="*60)
            
            for i, action in enumerate(self.recorded_actions, 1):
                action_type = action['action'].upper()
                if action_type == 'CLICK':
                    x, y = action.get('x', 0), action.get('y', 0)
                    clicks = action.get('clicks', 1)
                    print(f"   {i}. CLICK: ({x}, {y}) x{clicks}")
                elif action_type == 'SCROLL':
                    direction = action.get('direction', 'down')
                    amount = action.get('amount', 3)
                    direction_emoji = "⬇️" if direction == 'down' else "⬆️"
                    print(f"   {i}. SCROLL: {direction_emoji} (amount: {amount})")
                elif action_type == 'WAIT':
                    print(f"   {i}. WAIT: {action['duration']}с")
                elif action_type == 'TYPE':
                    print(f"   {i}. TYPE: '{action['text']}'")
                elif action_type == 'KEY':
                    print(f"   {i}. KEY: {action['key']}")
            
            # Добавляем в последовательность
            add = input("\n➕ Добавить записанные действия в последовательность? (y/n): ").strip().lower()
            if add == 'y':
                self.current_sequence.extend(self.recorded_actions)
                print(f"✅ Добавлено {len(self.recorded_actions)} шагов")
                return True
            else:
                print("❌ Не добавлено")
                return False
        else:
            print("\n⚠️  Ничего не записано")
            return False
    
    def _add_wait_if_needed(self, current_time: float):
        """Добавить паузу если прошло время"""
        if self.last_action_time is not None:
            pause = current_time - self.last_action_time
            if pause > 0.5:
                self.recorded_actions.append({
                    'action': 'wait',
                    'duration': round(pause, 1),
                    'description': 'Пауза'
                })
                print(f"⏸️  Пауза: {pause:.1f}с")
    
    def _flush_scroll_buffer(self):
        """Сохранить накопленные скроллы"""
        if not self.scroll_buffer:
            return
        
        total_scroll = sum(self.scroll_buffer)
        
        if total_scroll > 0:
            direction = 'up'
            amount = abs(total_scroll)
        else:
            direction = 'down'
            amount = abs(total_scroll)
        
        amount = max(1, int(amount / 3))
        
        self.recorded_actions.append({
            'action': 'scroll',
            'direction': direction,
            'amount': amount,
            'clicks': 1,
            'description': f'Скролл {direction}'
        })
        
        direction_emoji = "⬆️" if direction == 'up' else "⬇️"
        print(f"🖱️  Скролл {direction_emoji} (amount: {amount})")
        
        self.scroll_buffer = []
    
    def _on_click(self, x, y, button, pressed):
        """Обработка кликов"""
        if not self.recording or not pressed:
            return
        
        current_time = time.time()
        self._flush_scroll_buffer()
        self._add_wait_if_needed(current_time)
        
        self.recorded_actions.append({
            'action': 'click',
            'position': 'absolute',
            'x': x,
            'y': y,
            'clicks': 1,
            'description': f'Клик в ({x}, {y})'
        })
        print(f"🖱️  Клик в ({x}, {y})")
        
        self.last_action_time = current_time
    
    def _on_scroll(self, x, y, dx, dy):
        """Обработка скролла"""
        if not self.recording:
            return
        
        self.scroll_buffer.append(dy)
        self.last_action_time = time.time()
    
    def _on_press(self, key):
        """Обработка нажатий клавиш"""
        if not self.recording:
            return
        
        # ESC - остановка
        if key == Key.esc:
            print("\n\n⏹️  Остановка записи...")
            return False
        
        current_time = time.time()
        self._flush_scroll_buffer()
        self._add_wait_if_needed(current_time)
        
        # Обрабатываем клавиши
        if hasattr(key, 'name'):
            key_name = key.name
            
            if key_name in ['shift', 'shift_r', 'ctrl', 'ctrl_r', 'cmd', 'cmd_r', 'alt', 'alt_r']:
                return
            
            self.recorded_actions.append({
                'action': 'key',
                'key': key_name,
                'description': f'Нажатие {key_name}'
            })
            print(f"⌨️  Клавиша: {key_name}")
        else:
            try:
                char = key.char
                if char:
                    if self.recorded_actions and self.recorded_actions[-1]['action'] == 'type':
                        self.recorded_actions[-1]['text'] += char
                        print(f"⌨️  Ввод: '{self.recorded_actions[-1]['text']}'", end='\r')
                    else:
                        self.recorded_actions.append({
                            'action': 'type',
                            'text': char,
                            'method': 'auto',
                            'description': 'Ввод текста'
                        })
                        print(f"⌨️  Ввод: '{char}'", end='\r')
            except AttributeError:
                pass
        
        self.last_action_time = current_time
    
    def show_current_sequence(self):
        """Показать текущую последовательность"""
        if not self.current_sequence:
            print("\n⚠️  Последовательность пуста")
            return
        
        print("\n" + "="*60)
        print(f"📋 Текущая последовательность: {len(self.current_sequence)} шагов")
        print("="*60)
        
        for i, step in enumerate(self.current_sequence, 1):
            action = step['action'].upper()
            desc = step.get('description', '')
            
            if action == 'CLICK':
                clicks = step.get('clicks', 1)
                # Проверяем тип клика: template или coordinates
                if 'template' in step:
                    template = Path(step['template']).name
                    info = f"{template} x{clicks}"
                elif step.get('position') == 'absolute':
                    x = step.get('x', 0)
                    y = step.get('y', 0)
                    info = f"({int(x)}, {int(y)}) x{clicks}"
                else:
                    info = "неизвестный тип клика"
            elif action == 'WAIT':
                info = f"{step['duration']}с"
            elif action == 'TYPE':
                info = f"'{step['text']}'"
            elif action == 'KEY':
                info = step['key']
            elif action == 'HOTKEY':
                info = '+'.join(step['keys'])
            elif action == 'SCROLL':
                direction = step.get('direction', 'down')
                amount = step.get('amount', 3)
                clicks = step.get('clicks', 1)
                direction_text = "⬇️ вниз" if direction == 'down' else "⬆️ вверх"
                info = f"{direction_text} (amount: {amount}, x{clicks})"
            else:
                info = ""
            
            print(f"   {i}. {action}: {info}")
            if desc:
                print(f"      └─ {desc}")
    
    def save_sequence(self):
        """Сохранить последовательность"""
        if not self.current_sequence:
            print("\n⚠️  Нечего сохранять - последовательность пуста")
            return False
        
        print("\n" + "="*60)
        print("💾 Сохранение последовательности")
        print("="*60)
        
        # Имя последовательности
        while True:
            name = input("📝 Имя последовательности (латиница, _): ").strip()
            if name and name.replace('_', '').isalnum():
                self.sequence_name = name
                break
            print("⚠️  Используй только буквы, цифры и _")
        
        # Описание
        description = input("📝 Описание: ").strip()
        if not description:
            description = self.sequence_name
        
        # Повторы
        while True:
            repeat_input = input("🔄 Количество повторов (Enter=1): ").strip()
            if repeat_input == "":
                repeat = 1
                break
            try:
                repeat = int(repeat_input)
                if repeat > 0:
                    break
            except ValueError:
                pass
            print("⚠️  Введи число > 0")
        
        # Создаем последовательность
        sequence = {
            'name': description,
            'steps': self.current_sequence
        }
        
        if repeat > 1:
            sequence['repeat'] = repeat
        
        # Сохраняем в конфиг
        if 'sequences' not in self.config:
            self.config['sequences'] = {}
        
        self.config['sequences'][self.sequence_name] = sequence
        
        # Сохраняем в файл
        if self._save_config():
            print(f"\n🎉 Последовательность '{self.sequence_name}' сохранена!")
            print(f"\n💡 Запуск:")
            print(f"   python3 macro_sequence.py --config {self.config_path} --run {self.sequence_name}")
            return True
        
        return False
    
    def load_existing_sequence(self):
        """Загрузить существующую последовательность для редактирования"""
        sequences = self.config.get('sequences', {})
        
        if not sequences:
            print("\n⚠️  Нет сохраненных последовательностей")
            return False
        
        print("\n" + "="*60)
        print("📂 Выбор последовательности для редактирования")
        print("="*60)
        
        # Показываем список
        seq_list = list(sequences.keys())
        for i, name in enumerate(seq_list, 1):
            seq = sequences[name]
            steps = len(seq.get('steps', []))
            desc = seq.get('name', name)
            print(f"   {i}. {name}: {desc} ({steps} шагов)")
        
        # Выбор
        while True:
            choice = input("\n📝 Номер последовательности (или q для отмены): ").strip().lower()
            
            if choice == 'q':
                return False
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(seq_list):
                    seq_name = seq_list[idx]
                    seq = sequences[seq_name]
                    
                    # Загружаем
                    self.sequence_name = seq_name
                    self.current_sequence = seq.get('steps', [])
                    
                    print(f"\n✅ Загружена последовательность: {seq_name}")
                    print(f"   Текущих шагов: {len(self.current_sequence)}")
                    
                    return True
            
            print("⚠️  Неверный выбор")
    
    def delete_step(self):
        """Удалить шаг из последовательности"""
        if not self.current_sequence:
            print("\n⚠️  Последовательность пуста")
            return False
        
        self.show_current_sequence()
        
        while True:
            choice = input("\n🗑️  Номер шага для удаления (или q для отмены): ").strip().lower()
            
            if choice == 'q':
                return False
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(self.current_sequence):
                    removed = self.current_sequence.pop(idx)
                    print(f"\n✅ Шаг {idx + 1} удален: {removed['action']}")
                    return True
            
            print("⚠️  Неверный номер")
    
    def edit_step(self):
        """Редактировать существующий шаг"""
        if not self.current_sequence:
            print("\n⚠️  Последовательность пуста")
            return False
        
        self.show_current_sequence()
        
        while True:
            choice = input("\n✏️  Номер шага для редактирования (или q для отмены): ").strip().lower()
            
            if choice == 'q':
                return False
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(self.current_sequence):
                    step = self.current_sequence[idx]
                    action_type = step['action']
                    
                    print(f"\n📝 Редактирование шага {idx + 1}: {action_type.upper()}")
                    print("="*60)
                    
                    # Редактирование в зависимости от типа действия
                    if action_type == 'type':
                        # Редактирование текста
                        print(f"Текущий текст: '{step.get('text', '')}'")
                        new_text = input("Новый текст (Enter=оставить): ").strip()
                        if new_text:
                            step['text'] = new_text
                            print(f"✅ Текст изменен на: '{new_text}'")
                        
                        # Метод ввода
                        print(f"\nТекущий метод: {step.get('method', 'auto')}")
                        method = input("Метод (auto/clipboard/keyboard, Enter=оставить): ").strip().lower()
                        if method in ['auto', 'clipboard', 'keyboard']:
                            step['method'] = method
                            print(f"✅ Метод изменен на: {method}")
                    
                    elif action_type == 'click':
                        # Редактирование клика
                        if 'template' in step:
                            print(f"Текущий шаблон: {step['template']}")
                            new_template = input("Новый шаблон (Enter=оставить): ").strip()
                            if new_template:
                                step['template'] = new_template
                                print(f"✅ Шаблон изменен на: {new_template}")
                        elif step.get('position') == 'absolute':
                            print(f"Текущие координаты: x={step.get('x', 0)}, y={step.get('y', 0)}")
                            new_x = input("Новая координата X (Enter=оставить): ").strip()
                            if new_x:
                                try:
                                    step['x'] = float(new_x)
                                    print(f"✅ X изменен на: {new_x}")
                                except ValueError:
                                    pass
                            
                            new_y = input("Новая координата Y (Enter=оставить): ").strip()
                            if new_y:
                                try:
                                    step['y'] = float(new_y)
                                    print(f"✅ Y изменен на: {new_y}")
                                except ValueError:
                                    pass
                        
                        print(f"\nТекущее количество кликов: {step.get('clicks', 1)}")
                        clicks = input("Новое количество кликов (Enter=оставить): ").strip()
                        if clicks.isdigit():
                            step['clicks'] = int(clicks)
                            print(f"✅ Клики изменены на: {clicks}")
                        
                        if 'timeout' in step:
                            print(f"\nТекущий timeout: {step['timeout']}с")
                            timeout = input("Новый timeout в сек (Enter=оставить): ").strip()
                            if timeout:
                                try:
                                    step['timeout'] = float(timeout)
                                    print(f"✅ Timeout изменен на: {timeout}с")
                                except ValueError:
                                    pass
                    
                    elif action_type == 'wait':
                        # Редактирование паузы
                        print(f"Текущая длительность: {step.get('duration', 1.0)}с")
                        duration = input("Новая длительность в сек (Enter=оставить): ").strip()
                        if duration:
                            try:
                                step['duration'] = float(duration)
                                print(f"✅ Длительность изменена на: {duration}с")
                            except ValueError:
                                pass
                    
                    elif action_type == 'scroll':
                        # Редактирование скролла
                        print(f"Текущее направление: {step.get('direction', 'down')}")
                        direction = input("Новое направление (down/up, Enter=оставить): ").strip().lower()
                        if direction in ['down', 'up']:
                            step['direction'] = direction
                            print(f"✅ Направление изменено на: {direction}")
                        
                        print(f"\nТекущая сила: {step.get('amount', 3)}")
                        amount = input("Новая сила (Enter=оставить): ").strip()
                        if amount.isdigit():
                            step['amount'] = int(amount)
                            print(f"✅ Сила изменена на: {amount}")
                        
                        print(f"\nТекущее количество повторов: {step.get('clicks', 1)}")
                        clicks = input("Новое количество повторов (Enter=оставить): ").strip()
                        if clicks.isdigit():
                            step['clicks'] = int(clicks)
                            print(f"✅ Повторы изменены на: {clicks}")
                    
                    elif action_type == 'key':
                        # Редактирование клавиши
                        print(f"Текущая клавиша: {step.get('key', '')}")
                        new_key = input("Новая клавиша (Enter=оставить): ").strip()
                        if new_key:
                            step['key'] = new_key
                            print(f"✅ Клавиша изменена на: {new_key}")
                    
                    elif action_type == 'hotkey':
                        # Редактирование комбинации
                        print(f"Текущая комбинация: {step.get('keys', [])}")
                        print("Введи клавиши через пробел (например: command t)")
                        keys_input = input("Новая комбинация (Enter=оставить): ").strip()
                        if keys_input:
                            step['keys'] = keys_input.split()
                            print(f"✅ Комбинация изменена на: {step['keys']}")
                    
                    # Редактирование описания (для всех типов)
                    print(f"\nТекущее описание: {step.get('description', '')}")
                    new_desc = input("Новое описание (Enter=оставить): ").strip()
                    if new_desc:
                        step['description'] = new_desc
                        print(f"✅ Описание изменено")
                    
                    print("\n✅ Шаг отредактирован!")
                    return True
            
            print("⚠️  Неверный номер")
    
    def build_sequence(self, edit_mode=False):
        """Основной процесс построения последовательности"""
        if edit_mode:
            print("\n" + "="*60)
            print("✏️  Редактирование последовательности")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("🎯 Конструктор последовательностей")
            print("="*60)
            
            self.current_sequence = []
        
        while True:
            print("\n" + "-"*60)
            print("Что добавить?")
            print("-"*60)
            print("1. 🖱️  Клик по кнопке (template matching)")
            print("2. ⏸️  Пауза")
            print("3. ⌨️  Ввод текста")
            print("4. 🔘 Нажатие клавиши")
            print("5. 🎹 Комбинация клавиш")
            print("6. 🖱️  Скролл")
            print("7. 🎬 Записать действия (координаты)")
            print()
            print("e. ✏️  Редактировать шаг")
            print("8. 🗑️  Удалить шаг")
            print("9. 👁️  Показать последовательность")
            print("0. 💾 Сохранить и выйти")
            print("q. ❌ Отмена")
            print("-"*60)
            
            choice = input("Выбор: ").strip().lower()
            
            if choice == '1':
                self.add_click_step()
            elif choice == '2':
                self.add_wait_step()
            elif choice == '3':
                self.add_type_step()
            elif choice == '4':
                self.add_key_step()
            elif choice == '5':
                self.add_hotkey_step()
            elif choice == '6':
                self.add_scroll_step()
            elif choice == '7':
                self.record_actions_step()
            elif choice == 'e':
                self.edit_step()
            elif choice == '8':
                self.delete_step()
            elif choice == '9':
                self.show_current_sequence()
            elif choice == '0':
                if self.save_sequence():
                    break
            elif choice == 'q':
                print("\n❌ Отменено")
                break
            else:
                print("⚠️  Неверный выбор")


def main():
    print("\n" + "="*60)
    print("🎯 Sequence Builder - Конструктор последовательностей")
    print("="*60)
    
    # Выбор конфига
    config_input = input("\n📝 Имя конфига (Enter=my_sequences.yaml): ").strip()
    config_path = config_input if config_input else "my_sequences.yaml"
    
    builder = SequenceBuilder(config_path)
    
    while True:
        print("\n" + "="*60)
        print("Главное меню")
        print("="*60)
        print("1. ➕ Создать новую последовательность")
        print("2. ✏️  Редактировать существующую последовательность")
        print("3. 📋 Показать существующие последовательности")
        print("4. 📁 Показать доступные шаблоны")
        print("0. 🚪 Выход")
        print("="*60)
        
        choice = input("Выбор: ").strip()
        
        if choice == '1':
            builder.build_sequence(edit_mode=False)
        elif choice == '2':
            if builder.load_existing_sequence():
                builder.build_sequence(edit_mode=True)
        elif choice == '3':
            builder.list_sequences()
        elif choice == '4':
            builder.list_templates()
        elif choice == '0':
            print("\n👋 До встречи!")
            break
        else:
            print("⚠️  Неверный выбор")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✋ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
