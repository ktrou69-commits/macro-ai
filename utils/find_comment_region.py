#!/usr/bin/env python3
"""
Утилита для поиска области комментария
Наведи мышь на комментарий и нажми SPACE
"""

import pyautogui
import time
from pynput import keyboard, mouse

class CommentRegionFinder:
    def __init__(self):
        self.start_pos = None
        self.end_pos = None
        self.current_pos = None
        
    def on_move(self, x, y):
        """Отслеживание позиции мыши"""
        self.current_pos = (x, y)
        
    def on_press(self, key):
        """Обработка нажатий клавиш"""
        try:
            if key == keyboard.Key.space:
                if self.start_pos is None:
                    # Первое нажатие - верхний левый угол
                    self.start_pos = self.current_pos
                    print(f"\n✅ Верхний левый угол: {self.start_pos}")
                    print("📍 Наведи мышь на НИЖНИЙ ПРАВЫЙ угол комментария и нажми SPACE")
                else:
                    # Второе нажатие - нижний правый угол
                    self.end_pos = self.current_pos
                    print(f"✅ Нижний правый угол: {self.end_pos}")
                    
                    # Вычислить регион
                    x = self.start_pos[0]
                    y = self.start_pos[1]
                    width = self.end_pos[0] - self.start_pos[0]
                    height = self.end_pos[1] - self.start_pos[1]
                    
                    print("\n" + "="*50)
                    print("🎯 РЕГИОН КОММЕНТАРИЯ:")
                    print("="*50)
                    print(f"region: [{x}, {y}, {width}, {height}]")
                    print("="*50)
                    print("\n📋 Скопируй эту строку в конфиг:")
                    print(f"region: [{x}, {y}, {width}, {height}]")
                    print("\n✅ Готово! Нажми ESC для выхода")
                    
            elif key == keyboard.Key.esc:
                print("\n👋 Выход...")
                return False
                
        except AttributeError:
            pass
    
    def run(self):
        """Запуск утилиты"""
        print("="*50)
        print("🔍 ПОИСК ОБЛАСТИ КОММЕНТАРИЯ")
        print("="*50)
        print("\n📍 Инструкция:")
        print("1. Открой TikTok с комментариями")
        print("2. Наведи мышь на ВЕРХНИЙ ЛЕВЫЙ угол комментария")
        print("3. Нажми SPACE")
        print("4. Наведи мышь на НИЖНИЙ ПРАВЫЙ угол комментария")
        print("5. Нажми SPACE")
        print("6. Скопируй регион в конфиг")
        print("\n⚠️  Нажми ESC для выхода")
        print("="*50)
        
        # Запустить слушатели
        mouse_listener = mouse.Listener(on_move=self.on_move)
        keyboard_listener = keyboard.Listener(on_press=self.on_press)
        
        mouse_listener.start()
        keyboard_listener.start()
        
        # Ждать завершения
        keyboard_listener.join()
        mouse_listener.stop()

if __name__ == "__main__":
    finder = CommentRegionFinder()
    finder.run()
