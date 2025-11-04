#!/usr/bin/env python3
"""
TikTok Simple Bot - Легкая версия для MacBook Air
Без OCR, только генерация ответов
"""

import time
import pyautogui
import requests

class SimpleTikTokBot:
    """Упрощенный бот без OCR"""
    
    def __init__(self):
        pyautogui.FAILSAFE = True
        
        # Координаты для TikTok (подбери под свой экран)
        self.reply_button_pos = (200, 500)  # Кнопка "Ответить"
        self.input_field_pos = (200, 550)   # Поле ввода
        
    def generate_reply(self, style='friendly'):
        """Генерация случайного дружелюбного ответа"""
        
        # Готовые шаблоны ответов
        templates = {
            'friendly': [
                "Спасибо! 😊",
                "Рад что понравилось! ❤️",
                "Спасибо за поддержку! 🙏",
                "Очень приятно! 😍",
                "Благодарю! 🔥",
                "Спасибо большое! 💖",
                "Рад стараться! ✨",
                "Ценю ваше мнение! 🌟",
            ],
            'professional': [
                "Благодарю за отзыв!",
                "Спасибо за внимание к контенту.",
                "Ценю вашу поддержку.",
                "Благодарю за интерес!",
            ],
            'funny': [
                "Спасибо! Вы лучшие! 😂",
                "Ого, спасибо! 🤩",
                "Вау, приятно! 🎉",
                "Спасибо! Обнимаю! 🤗",
            ]
        }
        
        import random
        return random.choice(templates.get(style, templates['friendly']))
    
    def generate_reply_ollama(self, prompt="комментарий"):
        """Генерация ответа через Ollama (опционально)"""
        try:
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': 'llama2',
                    'prompt': f'Ответь очень коротко (1-2 слова) на {prompt}',
                    'stream': False
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()['response'].strip()[:50]  # Макс 50 символов
        except:
            pass
        
        # Fallback на шаблон
        return self.generate_reply()
    
    def send_reply(self, reply_text, use_ollama=False):
        """Отправка ответа на комментарий"""
        print(f"\n💬 Отправка: '{reply_text}'")
        
        # 1. Клик на кнопку "Ответить" (или первый комментарий)
        print("🖱️  Клик на комментарий...")
        pyautogui.click(*self.reply_button_pos)
        time.sleep(0.5)
        
        # 2. Клик на поле ввода
        print("🖱️  Клик на поле ввода...")
        pyautogui.click(*self.input_field_pos)
        time.sleep(0.3)
        
        # 3. Ввод текста
        print("⌨️  Ввод текста...")
        pyautogui.write(reply_text, interval=0.05)
        time.sleep(0.3)
        
        # 4. Отправка
        print("📤 Отправка...")
        pyautogui.press('enter')
        
        print("✅ Готово!")
        return True
    
    def run_once(self, style='friendly', use_ollama=False):
        """Один цикл: сгенерировать ответ → отправить"""
        print("\n" + "="*60)
        print("🤖 Запуск Simple TikTok Bot")
        print("="*60)
        
        # Генерация ответа
        if use_ollama:
            print("🧠 Генерация ответа через Ollama...")
            reply = self.generate_reply_ollama()
        else:
            print(f"🎨 Генерация ответа (стиль: {style})...")
            reply = self.generate_reply(style)
        
        # Отправка
        self.send_reply(reply, use_ollama)
        
        return True
    
    def run_loop(self, count=5, delay=10, style='friendly', use_ollama=False):
        """Цикл автоответов"""
        print(f"\n🚀 Запуск цикла: {count} ответов с задержкой {delay}с")
        print(f"🎨 Стиль: {style}")
        print(f"🧠 Ollama: {'Да' if use_ollama else 'Нет (шаблоны)'}")
        print("⚠️  Нажми Ctrl+C для остановки\n")
        
        for i in range(count):
            print(f"\n--- Ответ {i+1}/{count} ---")
            
            try:
                success = self.run_once(style, use_ollama)
                
                if success and i < count - 1:
                    print(f"⏳ Ожидание {delay}с...")
                    time.sleep(delay)
            
            except KeyboardInterrupt:
                print("\n\n⏹️  Остановлено пользователем")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                continue
        
        print("\n✅ Цикл завершен!")


def main():
    """Главная функция"""
    print("\n" + "="*60)
    print("🤖 Simple TikTok Bot - Легкая версия")
    print("="*60)
    print("\n💡 Эта версия НЕ читает комментарии")
    print("   Она просто отправляет дружелюбные ответы\n")
    
    # Создание бота
    bot = SimpleTikTokBot()
    
    # Выбор режима генерации
    print("🧠 Генерация ответов:")
    print("1. Шаблоны (быстро, легко)")
    print("2. Ollama (медленнее, но умнее)")
    
    gen_choice = input("Выбор (1/2): ").strip()
    use_ollama = (gen_choice == '2')
    
    if use_ollama:
        print("\n⚠️  Убедись что Ollama запущен: ollama serve")
    
    # Выбор стиля (только для шаблонов)
    if not use_ollama:
        print("\n🎨 Стиль ответов:")
        print("1. Дружелюбный")
        print("2. Профессиональный")
        print("3. Веселый")
        
        style_choice = input("Выбор (1/2/3): ").strip()
        style_map = {'1': 'friendly', '2': 'professional', '3': 'funny'}
        style = style_map.get(style_choice, 'friendly')
    else:
        style = 'friendly'
    
    # Настройка координат
    print("\n📍 Настройка координат:")
    
    # Попытка загрузить сохраненные координаты
    try:
        with open('tiktok_coordinates.txt', 'r') as f:
            lines = f.readlines()
            coords = {}
            for line in lines:
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=')
                    coords[key.strip()] = int(value.strip())
        
        if 'reply_button_x' in coords:
            bot.reply_button_pos = (coords['reply_button_x'], coords['reply_button_y'])
            bot.input_field_pos = (coords['input_field_x'], coords['input_field_y'])
            print("   ✅ Загружены сохраненные координаты:")
    except:
        print("   ⚠️  Сохраненные координаты не найдены, используются стандартные:")
    
    print(f"   - Кнопка ответа: {bot.reply_button_pos}")
    print(f"   - Поле ввода: {bot.input_field_pos}")
    
    print("\nВыбери действие:")
    print("1. Использовать эти координаты")
    print("2. Определить координаты автоматически (рекомендуется)")
    print("3. Ввести координаты вручную")
    
    coord_choice = input("\nВыбор (1/2/3): ").strip()
    
    if coord_choice == '2':
        print("\n🎯 Запуск инструмента определения координат...")
        print("   Следуй инструкциям в новом окне")
        import subprocess
        subprocess.run(['python3', 'find_coordinates.py'])
        
        # Перезагрузка координат
        try:
            with open('tiktok_coordinates.txt', 'r') as f:
                lines = f.readlines()
                coords = {}
                for line in lines:
                    if '=' in line and not line.startswith('#'):
                        key, value = line.split('=')
                        coords[key.strip()] = int(value.strip())
            
            bot.reply_button_pos = (coords['reply_button_x'], coords['reply_button_y'])
            bot.input_field_pos = (coords['input_field_x'], coords['input_field_y'])
            print("\n✅ Координаты обновлены!")
        except:
            print("\n⚠️  Не удалось загрузить координаты")
    
    elif coord_choice == '3':
        try:
            print("\n📍 Ввод координат вручную:")
            x1 = int(input("X кнопки ответа: "))
            y1 = int(input("Y кнопки ответа: "))
            bot.reply_button_pos = (x1, y1)
            
            x2 = int(input("X поля ввода: "))
            y2 = int(input("Y поля ввода: "))
            bot.input_field_pos = (x2, y2)
            
            print("✅ Координаты обновлены!")
        except:
            print("⚠️  Ошибка ввода, используются стандартные координаты")
    
    # Режим работы
    print("\n⚙️  Режим:")
    print("1. Один ответ (тест)")
    print("2. Цикл ответов")
    
    mode = input("Выбор (1/2): ").strip()
    
    if mode == '1':
        # Задержка для переключения на TikTok
        print("\n⏳ 5 секунд для переключения на TikTok...")
        time.sleep(5)
        
        bot.run_once(style, use_ollama)
    else:
        count = int(input("Количество ответов: ").strip() or "5")
        delay = int(input("Задержка между ответами (сек): ").strip() or "10")
        
        print("\n⏳ 5 секунд для переключения на TikTok...")
        time.sleep(5)
        
        bot.run_loop(count, delay, style, use_ollama)


if __name__ == '__main__':
    main()
