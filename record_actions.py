#!/usr/bin/env python3
"""
record_actions.py
Запись действий пользователя в реальном времени
"""

import time
import sys
from pynput import mouse, keyboard
from pynput.mouse import Button
from pynput.keyboard import Key
import yaml
from pathlib import Path
from datetime import datetime

class ActionRecorder:
    """Записывает действия пользователя"""
    
    def __init__(self):
        self.actions = []
        self.recording = False
        self.start_time = None
        self.last_action_time = None
        
        # Для отслеживания скролла
        self.scroll_buffer = []
        self.scroll_timeout = 0.5  # Группируем скроллы в течение 0.5 сек
        
        # Для отслеживания кликов
        self.last_click_pos = None
        self.last_click_time = None
        self.click_timeout = 0.3  # Двойной клик в течение 0.3 сек
        
    def start_countdown(self, seconds: int = 5):
        """Обратный отсчет перед записью"""
        print("\n" + "="*60)
        print("⏱️  Подготовка к записи")
        print("="*60)
        print(f"\n💡 Переключись на нужное окно/приложение!")
        print(f"💡 Запись начнется через {seconds} секунд...\n")
        
        for i in range(seconds, 0, -1):
            print(f"   {i}...", end='\r')
            time.sleep(1)
        
        print("\n🔴 ЗАПИСЬ НАЧАЛАСЬ!")
        print("="*60)
        print("💡 Выполняй свои действия:")
        print("   • Клики мышью")
        print("   • Скролл")
        print("   • Нажатия клавиш")
        print("   • Ввод текста")
        print("\n⚠️  Нажми ESC для остановки записи")
        print("="*60 + "\n")
    
    def add_wait_if_needed(self, current_time: float):
        """Добавить паузу если прошло время"""
        if self.last_action_time is not None:
            pause = current_time - self.last_action_time
            if pause > 0.5:  # Если пауза больше 0.5 сек
                self.actions.append({
                    'action': 'wait',
                    'duration': round(pause, 1),
                    'description': 'Пауза'
                })
                print(f"⏸️  Пауза: {pause:.1f}с")
    
    def flush_scroll_buffer(self):
        """Сохранить накопленные скроллы"""
        if not self.scroll_buffer:
            return
        
        # Суммируем все скроллы
        total_scroll = sum(self.scroll_buffer)
        
        # Определяем направление и количество
        if total_scroll > 0:
            direction = 'up'
            amount = abs(total_scroll)
        else:
            direction = 'down'
            amount = abs(total_scroll)
        
        # Нормализуем amount (обычно 1 клик = 1-3 единицы)
        amount = max(1, int(amount / 3))
        
        self.actions.append({
            'action': 'scroll',
            'direction': direction,
            'amount': amount,
            'clicks': 1,
            'description': f'Скролл {direction}'
        })
        
        direction_emoji = "⬆️" if direction == 'up' else "⬇️"
        print(f"🖱️  Скролл {direction_emoji} (amount: {amount})")
        
        self.scroll_buffer = []
    
    def on_click(self, x, y, button, pressed):
        """Обработка кликов мыши"""
        if not self.recording:
            return
        
        if pressed:  # Только нажатие, не отпускание
            current_time = time.time()
            
            # Проверяем двойной клик
            is_double_click = False
            if self.last_click_pos and self.last_click_time:
                time_diff = current_time - self.last_click_time
                pos_diff = ((x - self.last_click_pos[0])**2 + (y - self.last_click_pos[1])**2)**0.5
                
                if time_diff < self.click_timeout and pos_diff < 10:
                    is_double_click = True
            
            # Сохраняем скроллы перед кликом
            self.flush_scroll_buffer()
            
            # Добавляем паузу если нужно
            self.add_wait_if_needed(current_time)
            
            if is_double_click:
                # Обновляем последний клик на двойной
                if self.actions and self.actions[-1]['action'] == 'click':
                    self.actions[-1]['clicks'] = 2
                    print(f"🖱️  Двойной клик в ({x}, {y})")
            else:
                # Обычный клик
                self.actions.append({
                    'action': 'click',
                    'position': 'absolute',
                    'x': x,
                    'y': y,
                    'clicks': 1,
                    'description': f'Клик в ({x}, {y})'
                })
                print(f"🖱️  Клик в ({x}, {y})")
            
            self.last_click_pos = (x, y)
            self.last_click_time = current_time
            self.last_action_time = current_time
    
    def on_scroll(self, x, y, dx, dy):
        """Обработка скролла"""
        if not self.recording:
            return
        
        current_time = time.time()
        
        # Добавляем в буфер
        self.scroll_buffer.append(dy)
        
        # Обновляем время последнего действия
        self.last_action_time = current_time
    
    def on_press(self, key):
        """Обработка нажатий клавиш"""
        if not self.recording:
            return
        
        # ESC - остановка записи
        if key == Key.esc:
            print("\n\n⏹️  Остановка записи...")
            self.stop_recording()
            return False  # Останавливаем listener
        
        current_time = time.time()
        
        # Сохраняем скроллы перед нажатием клавиши
        self.flush_scroll_buffer()
        
        # Добавляем паузу если нужно
        self.add_wait_if_needed(current_time)
        
        # Обрабатываем специальные клавиши
        if hasattr(key, 'name'):
            key_name = key.name
            
            # Игнорируем модификаторы (shift, ctrl, cmd)
            if key_name in ['shift', 'shift_r', 'ctrl', 'ctrl_r', 'cmd', 'cmd_r', 'alt', 'alt_r']:
                return
            
            self.actions.append({
                'action': 'key',
                'key': key_name,
                'description': f'Нажатие {key_name}'
            })
            print(f"⌨️  Клавиша: {key_name}")
            
        else:
            # Обычный символ
            try:
                char = key.char
                if char:
                    # Ищем последний action type
                    if self.actions and self.actions[-1]['action'] == 'type':
                        # Добавляем к существующему тексту
                        self.actions[-1]['text'] += char
                        print(f"⌨️  Ввод: '{self.actions[-1]['text']}'", end='\r')
                    else:
                        # Новый ввод текста
                        self.actions.append({
                            'action': 'type',
                            'text': char,
                            'method': 'auto',
                            'description': 'Ввод текста'
                        })
                        print(f"⌨️  Ввод: '{char}'", end='\r')
            except AttributeError:
                pass
        
        self.last_action_time = current_time
    
    def start_recording(self, countdown: int = 5):
        """Начать запись"""
        self.start_countdown(countdown)
        
        self.recording = True
        self.start_time = time.time()
        self.last_action_time = self.start_time
        
        # Создаем listeners
        mouse_listener = mouse.Listener(
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        
        keyboard_listener = keyboard.Listener(
            on_press=self.on_press
        )
        
        # Запускаем
        mouse_listener.start()
        keyboard_listener.start()
        
        # Ждем остановки
        keyboard_listener.join()
        
        # Останавливаем mouse listener
        mouse_listener.stop()
        
        # Сохраняем оставшиеся скроллы
        self.flush_scroll_buffer()
    
    def stop_recording(self):
        """Остановить запись"""
        self.recording = False
        
        total_time = time.time() - self.start_time
        
        print("\n" + "="*60)
        print("✅ Запись завершена!")
        print("="*60)
        print(f"⏱️  Длительность: {total_time:.1f}с")
        print(f"📋 Записано действий: {len(self.actions)}")
        print("="*60)
    
    def save_to_yaml(self, sequence_name: str, config_path: str = "my_sequences.yaml"):
        """Сохранить в YAML"""
        if not self.actions:
            print("\n⚠️  Нет записанных действий")
            return False
        
        # Загружаем существующий конфиг
        config = {'sequences': {}, 'settings': {}}
        if Path(config_path).exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f) or {'sequences': {}, 'settings': {}}
            except Exception as e:
                print(f"⚠️  Ошибка загрузки конфига: {e}")
        
        # Добавляем новую последовательность
        config['sequences'][sequence_name] = {
            'name': f'Записано: {datetime.now().strftime("%Y-%m-%d %H:%M")}',
            'steps': self.actions
        }
        
        # Сохраняем
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
            
            print(f"\n✅ Сохранено в: {config_path}")
            print(f"📝 Имя последовательности: {sequence_name}")
            print(f"\n💡 Запуск:")
            print(f"   python3 macro_sequence.py --config {config_path} --run {sequence_name}")
            return True
        except Exception as e:
            print(f"\n❌ Ошибка сохранения: {e}")
            return False
    
    def show_actions(self):
        """Показать записанные действия"""
        if not self.actions:
            print("\n⚠️  Нет записанных действий")
            return
        
        print("\n" + "="*60)
        print(f"📋 Записанные действия: {len(self.actions)}")
        print("="*60)
        
        for i, action in enumerate(self.actions, 1):
            action_type = action['action'].upper()
            desc = action.get('description', '')
            
            if action_type == 'CLICK':
                x, y = action.get('x', 0), action.get('y', 0)
                clicks = action.get('clicks', 1)
                info = f"({x}, {y}) x{clicks}"
            elif action_type == 'WAIT':
                info = f"{action['duration']}с"
            elif action_type == 'TYPE':
                info = f"'{action['text']}'"
            elif action_type == 'KEY':
                info = action['key']
            elif action_type == 'SCROLL':
                direction = action.get('direction', 'down')
                amount = action.get('amount', 3)
                direction_emoji = "⬆️" if direction == 'up' else "⬇️"
                info = f"{direction_emoji} (amount: {amount})"
            else:
                info = ""
            
            print(f"   {i}. {action_type}: {info}")
            if desc:
                print(f"      └─ {desc}")


def main():
    print("\n" + "="*60)
    print("🎬 Action Recorder - Запись действий")
    print("="*60)
    
    # Параметры
    countdown = input("\n⏱️  Задержка перед записью в сек (Enter=5): ").strip()
    countdown = int(countdown) if countdown.isdigit() else 5
    
    # Создаем recorder
    recorder = ActionRecorder()
    
    try:
        # Начинаем запись
        recorder.start_recording(countdown=countdown)
        
        # Показываем что записали
        recorder.show_actions()
        
        # Сохранение
        save = input("\n💾 Сохранить последовательность? (y/n): ").strip().lower()
        if save == 'y':
            seq_name = input("📝 Имя последовательности: ").strip()
            if not seq_name:
                seq_name = f"recorded_{int(time.time())}"
            
            config_path = input("📁 Путь к конфигу (Enter=my_sequences.yaml): ").strip()
            if not config_path:
                config_path = "my_sequences.yaml"
            
            recorder.save_to_yaml(seq_name, config_path)
        else:
            print("\n❌ Не сохранено")
    
    except KeyboardInterrupt:
        print("\n\n✋ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
