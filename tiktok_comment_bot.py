#!/usr/bin/env python3
"""
TikTok Comment Bot - Автоответы на комментарии
Использует: YOLO (детекция) + OCR (чтение) + LLM (генерация)
"""

import time
import pyautogui
import cv2
import numpy as np
from PIL import Image
from pathlib import Path

# OCR библиотеки
try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False
    print("⚠️  pytesseract не установлен. Установи: pip install pytesseract")

try:
    import easyocr
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False
    print("⚠️  easyocr не установлен. Установи: pip install easyocr")

# LLM библиотеки
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("⚠️  openai не установлен. Установи: pip install openai")

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


class TikTokCommentBot:
    """Бот для автоответов на комментарии в TikTok"""
    
    def __init__(self, ocr_engine='easyocr', llm_provider='local'):
        """
        Args:
            ocr_engine: 'tesseract' или 'easyocr'
            llm_provider: 'openai', 'anthropic', 'local' (ollama)
        """
        self.ocr_engine = ocr_engine
        self.llm_provider = llm_provider
        
        # Инициализация OCR
        if ocr_engine == 'easyocr' and HAS_EASYOCR:
            self.reader = easyocr.Reader(['ru', 'en'])
            print("✅ EasyOCR инициализирован (RU + EN)")
        elif ocr_engine == 'tesseract' and HAS_TESSERACT:
            print("✅ Tesseract выбран")
        else:
            raise ValueError(f"OCR engine '{ocr_engine}' недоступен")
        
        # Инициализация LLM
        if llm_provider == 'openai' and HAS_OPENAI:
            self.llm_client = OpenAI()
            print("✅ OpenAI API инициализирован")
        elif llm_provider == 'anthropic' and HAS_ANTHROPIC:
            self.llm_client = Anthropic()
            print("✅ Anthropic API инициализирован")
        elif llm_provider == 'local':
            print("✅ Локальная LLM (Ollama) будет использована")
            self.llm_client = None
        
        # Координаты для TikTok (примерные)
        self.comment_area = {
            'x': 50,
            'y': 400,
            'width': 400,
            'height': 500
        }
        
        pyautogui.FAILSAFE = True
    
    def capture_comment_area(self):
        """Захват области с комментариями"""
        screenshot = pyautogui.screenshot()
        screenshot = np.array(screenshot)
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
        
        # Вырезаем область комментариев
        x, y = self.comment_area['x'], self.comment_area['y']
        w, h = self.comment_area['width'], self.comment_area['height']
        
        comment_region = screenshot[y:y+h, x:x+w]
        return comment_region
    
    def extract_first_comment(self, image):
        """Извлечение текста первого комментария"""
        if self.ocr_engine == 'easyocr':
            results = self.reader.readtext(image)
            if results:
                # Берем первый результат с наибольшей уверенностью
                results = sorted(results, key=lambda x: x[2], reverse=True)
                text = results[0][1]
                confidence = results[0][2]
                print(f"📝 OCR: '{text}' (confidence: {confidence:.2f})")
                return text
        
        elif self.ocr_engine == 'tesseract':
            # Конвертируем в PIL Image
            pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            text = pytesseract.image_to_string(pil_image, lang='rus+eng')
            text = text.strip()
            print(f"📝 OCR: '{text}'")
            return text
        
        return None
    
    def generate_response(self, comment_text, style='friendly'):
        """
        Генерация ответа на комментарий
        
        Args:
            comment_text: Текст комментария
            style: Стиль ответа ('friendly', 'professional', 'funny')
        """
        if not comment_text:
            return None
        
        # Промпт для генерации
        system_prompt = {
            'friendly': "Ты дружелюбный помощник. Отвечай коротко и позитивно на комментарии в TikTok.",
            'professional': "Ты профессиональный контент-мейкер. Отвечай вежливо и информативно.",
            'funny': "Ты веселый и остроумный. Отвечай с юмором, но не обижай."
        }
        
        prompt = f"Ответь на этот комментарий: '{comment_text}'\n\nОтвет должен быть коротким (1-2 предложения)."
        
        # OpenAI
        if self.llm_provider == 'openai' and HAS_OPENAI:
            response = self.llm_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt[style]},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        
        # Anthropic
        elif self.llm_provider == 'anthropic' and HAS_ANTHROPIC:
            response = self.llm_client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                messages=[
                    {"role": "user", "content": f"{system_prompt[style]}\n\n{prompt}"}
                ]
            )
            return response.content[0].text.strip()
        
        # Локальная LLM (Ollama)
        elif self.llm_provider == 'local':
            import requests
            
            try:
                response = requests.post(
                    'http://localhost:11434/api/generate',
                    json={
                        'model': 'llama2',  # или 'mistral', 'phi'
                        'prompt': f"{system_prompt[style]}\n\n{prompt}",
                        'stream': False
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json()['response'].strip()
            except Exception as e:
                print(f"❌ Ошибка Ollama: {e}")
                return None
        
        return None
    
    def send_reply(self, reply_text):
        """Отправка ответа на комментарий"""
        if not reply_text:
            return False
        
        print(f"💬 Отправка ответа: '{reply_text}'")
        
        # 1. Клик на первый комментарий (открыть ответы)
        # Координаты нужно подобрать для твоего экрана
        comment_x = self.comment_area['x'] + 200
        comment_y = self.comment_area['y'] + 100
        
        pyautogui.click(comment_x, comment_y)
        time.sleep(0.5)
        
        # 2. Клик на поле "Ответить"
        # Обычно появляется под комментарием
        reply_field_y = comment_y + 50
        pyautogui.click(comment_x, reply_field_y)
        time.sleep(0.5)
        
        # 3. Ввод текста
        pyautogui.write(reply_text, interval=0.05)
        time.sleep(0.3)
        
        # 4. Отправка (Enter или клик на кнопку)
        pyautogui.press('enter')
        
        print("✅ Ответ отправлен!")
        return True
    
    def run_once(self, style='friendly'):
        """Один цикл: прочитать комментарий → сгенерировать ответ → отправить"""
        print("\n" + "="*60)
        print("🤖 Запуск бота автоответов")
        print("="*60)
        
        # 1. Захват области комментариев
        print("📸 Захват области комментариев...")
        comment_image = self.capture_comment_area()
        
        # 2. Извлечение текста
        print("🔍 Извлечение текста комментария...")
        comment_text = self.extract_first_comment(comment_image)
        
        if not comment_text:
            print("❌ Комментарий не найден")
            return False
        
        # 3. Генерация ответа
        print(f"🧠 Генерация ответа (стиль: {style})...")
        reply = self.generate_response(comment_text, style)
        
        if not reply:
            print("❌ Не удалось сгенерировать ответ")
            return False
        
        # 4. Отправка
        self.send_reply(reply)
        
        return True
    
    def run_loop(self, count=5, delay=10, style='friendly'):
        """
        Цикл автоответов
        
        Args:
            count: Количество ответов
            delay: Задержка между ответами (сек)
            style: Стиль ответов
        """
        print(f"\n🚀 Запуск цикла: {count} ответов с задержкой {delay}с")
        print(f"🎨 Стиль: {style}")
        print("⚠️  Нажми Ctrl+C для остановки\n")
        
        for i in range(count):
            print(f"\n--- Ответ {i+1}/{count} ---")
            
            try:
                success = self.run_once(style)
                
                if success and i < count - 1:
                    print(f"⏳ Ожидание {delay}с до следующего ответа...")
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
    print("🤖 TikTok Comment Bot - Автоответы на комментарии")
    print("="*60)
    
    # Выбор OCR
    print("\n📖 Выбор OCR движка:")
    print("1. EasyOCR (рекомендуется, поддержка RU)")
    print("2. Tesseract")
    
    ocr_choice = input("Выбор (1/2): ").strip()
    ocr_engine = 'easyocr' if ocr_choice == '1' else 'tesseract'
    
    # Выбор LLM
    print("\n🧠 Выбор LLM:")
    print("1. OpenAI GPT-3.5 (нужен API ключ)")
    print("2. Anthropic Claude (нужен API ключ)")
    print("3. Локальная LLM (Ollama)")
    
    llm_choice = input("Выбор (1/2/3): ").strip()
    llm_map = {'1': 'openai', '2': 'anthropic', '3': 'local'}
    llm_provider = llm_map.get(llm_choice, 'local')
    
    # Создание бота
    try:
        bot = TikTokCommentBot(ocr_engine=ocr_engine, llm_provider=llm_provider)
    except Exception as e:
        print(f"❌ Ошибка инициализации: {e}")
        return
    
    # Выбор стиля
    print("\n🎨 Стиль ответов:")
    print("1. Дружелюбный")
    print("2. Профессиональный")
    print("3. Веселый")
    
    style_choice = input("Выбор (1/2/3): ").strip()
    style_map = {'1': 'friendly', '2': 'professional', '3': 'funny'}
    style = style_map.get(style_choice, 'friendly')
    
    # Режим работы
    print("\n⚙️  Режим:")
    print("1. Один ответ (тест)")
    print("2. Цикл ответов")
    
    mode = input("Выбор (1/2): ").strip()
    
    if mode == '1':
        # Задержка для переключения на TikTok
        print("\n⏳ 5 секунд для переключения на TikTok...")
        time.sleep(5)
        
        bot.run_once(style)
    else:
        count = int(input("Количество ответов: ").strip() or "5")
        delay = int(input("Задержка между ответами (сек): ").strip() or "10")
        
        print("\n⏳ 5 секунд для переключения на TikTok...")
        time.sleep(5)
        
        bot.run_loop(count, delay, style)


if __name__ == '__main__':
    main()
