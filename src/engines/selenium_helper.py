#!/usr/bin/env python3
"""
selenium_helper.py
Интерактивный помощник для настройки Selenium шагов
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import os

class SeleniumHelper:
    """Помощник для настройки Selenium"""
    
    def __init__(self):
        self.driver = None
    
    def connect(self):
        """Подключиться к Chrome"""
        try:
            chromedriver_path = "/tmp/chromedriver_temp/chromedriver-mac-arm64/chromedriver"
            
            if not os.path.exists(chromedriver_path):
                print("❌ ChromeDriver не найден!")
                print("💡 Запусти: python3 tests/test_selenium_alt.py")
                return False
            
            options = webdriver.ChromeOptions()
            options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            
            service = Service(chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            
            print("✅ Подключено к Chrome!")
            print(f"   URL: {self.driver.current_url}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка подключения: {e}")
            return False
    
    def test_selector(self, selector: str, show_count: int = 5):
        """Протестировать селектор"""
        if not self.driver:
            print("❌ Не подключен к Chrome")
            return []
        
        try:
            elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
            
            if not elements:
                print(f"❌ Элементы не найдены: {selector}")
                return []
            
            print(f"\n✅ Найдено элементов: {len(elements)}")
            print(f"📋 Первые {min(show_count, len(elements))} элементов:\n")
            
            results = []
            for i, elem in enumerate(elements[:show_count]):
                try:
                    text = elem.text.strip()
                    tag = elem.tag_name
                    data_e2e = elem.get_attribute('data-e2e')
                    
                    print(f"   [{i}] {tag}")
                    if text:
                        print(f"       Текст: {text[:60]}...")
                    if data_e2e:
                        print(f"       data-e2e: {data_e2e}")
                    print()
                    
                    results.append({
                        'index': i,
                        'text': text,
                        'tag': tag,
                        'data_e2e': data_e2e
                    })
                except:
                    pass
            
            return results
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return []
    
    def find_button_in_parent(self, container_selector: str, index: int, button_text: str = "Ответить"):
        """Найти кнопку в родителе контейнера"""
        if not self.driver:
            print("❌ Не подключен к Chrome")
            return None
        
        try:
            containers = self.driver.find_elements(By.CSS_SELECTOR, container_selector)
            
            if not containers:
                print(f"❌ Контейнеры не найдены: {container_selector}")
                return None
            
            if index >= len(containers):
                print(f"❌ Индекс {index} вне диапазона (найдено {len(containers)})")
                return None
            
            container = containers[index]
            parent = container.find_element(By.XPATH, "..")
            
            # Искать кнопку с текстом
            buttons = parent.find_elements(By.XPATH, f".//*[contains(text(), '{button_text}')]")
            
            if not buttons:
                print(f"❌ Кнопка '{button_text}' не найдена в родителе")
                return None
            
            button = buttons[0]
            
            print(f"\n✅ Найдена кнопка в родителе:")
            print(f"   Текст: {button.text}")
            print(f"   data-e2e: {button.get_attribute('data-e2e')}")
            print(f"   class: {button.get_attribute('class')}")
            
            return {
                'selector': button.get_attribute('data-e2e'),
                'text': button.text,
                'tag': button.tag_name
            }
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            return None
    
    def auto_find_selectors(self):
        """Автоматически найти все текстовые элементы на странице"""
        if not self.driver:
            print("❌ Не подключен к Chrome")
            return []
        
        print("\n🔍 Автоматический поиск текстовых элементов...")
        
        # Общие селекторы для разных типов контента
        common_selectors = [
            # Комментарии
            "[data-e2e*='comment']",
            "[class*='comment']",
            ".comment",
            
            # Сообщения
            "[class*='message']",
            ".message",
            "[data-message-id]",
            
            # Посты
            "[class*='post']",
            ".post",
            "article",
            
            # Текстовые блоки
            "[class*='text-content']",
            "[class*='content']",
            "p",
            "span",
        ]
        
        found_selectors = []
        
        for selector in common_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                
                # Фильтруем элементы с текстом
                text_elements = []
                for elem in elements[:10]:  # Проверяем первые 10
                    text = elem.text.strip()
                    if text and len(text) > 10:  # Минимум 10 символов
                        text_elements.append({
                            'text': text[:60],
                            'tag': elem.tag_name,
                            'class': elem.get_attribute('class'),
                            'data_e2e': elem.get_attribute('data-e2e')
                        })
                
                if text_elements:
                    found_selectors.append({
                        'selector': selector,
                        'count': len(elements),
                        'examples': text_elements[:3]
                    })
            except:
                pass
        
        return found_selectors
    
    def interactive_setup(self):
        """Интерактивная настройка Selenium шага"""
        print("\n" + "="*60)
        print("🧠 ИНТЕРАКТИВНАЯ НАСТРОЙКА SELENIUM")
        print("="*60)
        
        # Подключение
        if not self.driver:
            print("\n1️⃣ Подключение к Chrome...")
            if not self.connect():
                return None
        
        # Выбор типа шага
        print("\n2️⃣ Выбери тип шага:")
        print("   1. Извлечь текст (selenium_extract)")
        print("   2. Кликнуть элемент (selenium_click)")
        print("   3. Получить координаты (selenium_get_coordinates)")
        print("   4. 🔍 Автопоиск селекторов (найти все текстовые элементы)")
        
        choice = input("\nВыбор (1-4): ").strip()
        
        if choice == "1":
            return self._setup_extract()
        elif choice == "2":
            return self._setup_click()
        elif choice == "3":
            return self._setup_coordinates()
        elif choice == "4":
            # Автопоиск
            selectors = self.auto_find_selectors()
            
            if not selectors:
                print("❌ Текстовые элементы не найдены")
                return None
            
            print(f"\n✅ Найдено {len(selectors)} типов элементов:\n")
            
            for i, item in enumerate(selectors, 1):
                print(f"{i}. {item['selector']} ({item['count']} элементов)")
                for ex in item['examples']:
                    print(f"   - {ex['text']}...")
                print()
            
            # Выбор селектора
            sel_choice = input(f"Выбери селектор (1-{len(selectors)}): ").strip()
            
            try:
                sel_index = int(sel_choice) - 1
                if 0 <= sel_index < len(selectors):
                    selected = selectors[sel_index]
                    print(f"\n✅ Выбран: {selected['selector']}")
                    
                    # Продолжить настройку с выбранным селектором
                    return self._setup_extract_with_selector(selected['selector'])
                else:
                    print("❌ Неверный выбор")
                    return None
            except:
                print("❌ Неверный ввод")
                return None
        else:
            print("❌ Неверный выбор")
            return None
    
    def _setup_extract_with_selector(self, selector: str):
        """Настройка selenium_extract с готовым селектором"""
        # Тест селектора
        print(f"\n3️⃣ Тестирование селектора: {selector}")
        results = self.test_selector(selector)
        
        if not results:
            return None
        
        # Параметры
        print("\n4️⃣ Настройка параметров:")
        
        start_index = input("   Начальный индекс (0): ").strip() or "0"
        save_to = input("   Сохранить в переменную (extracted_text): ").strip() or "extracted_text"
        skip_empty = input("   Пропускать пустые? (y/n, по умолчанию y): ").strip().lower() != "n"
        
        # Генерация YAML
        step = {
            'action': 'selenium_extract',
            'selector': selector,
            'index': start_index,
            'save_to': save_to,
            'skip_empty': skip_empty,
            'max_attempts': 20,
            'description': f'Извлечь текст из {selector}'
        }
        
        if skip_empty:
            step['save_index_to'] = 'found_index'
        
        print("\n✅ Шаг создан:")
        print(f"   Селектор: {selector}")
        print(f"   Индекс: {start_index}")
        print(f"   Сохранить в: {save_to}")
        print(f"   Пропускать пустые: {skip_empty}")
        
        return step
    
    def _setup_extract(self):
        """Настройка selenium_extract"""
        print("\n" + "="*60)
        print("📝 НАСТРОЙКА ИЗВЛЕЧЕНИЯ ТЕКСТА")
        print("="*60)
        
        # Ввод селектора
        print("\n💡 Примеры селекторов:")
        print("   [data-e2e='comment-level-1']  - контейнеры комментариев")
        print("   .message-text                  - сообщения в чате")
        print("   [class*='post-content']        - контент постов")
        
        selector = input("\nВведи CSS селектор: ").strip()
        
        if not selector:
            print("❌ Селектор не может быть пустым")
            return None
        
        return self._setup_extract_with_selector(selector)
    
    def _setup_click(self):
        """Настройка selenium_click"""
        print("\n" + "="*60)
        print("🖱️  НАСТРОЙКА КЛИКА")
        print("="*60)
        
        # Ввод селектора контейнера
        print("\n💡 Сначала найдем контейнер элемента:")
        container_selector = input("   CSS селектор контейнера: ").strip()
        
        if not container_selector:
            print("❌ Селектор не может быть пустым")
            return None
        
        # Тест
        print(f"\n3️⃣ Тестирование: {container_selector}")
        results = self.test_selector(container_selector, show_count=3)
        
        if not results:
            return None
        
        # Поиск кнопки
        print("\n4️⃣ Поиск кнопки в родителе:")
        button_text = input("   Текст кнопки (Ответить): ").strip() or "Ответить"
        
        button_info = self.find_button_in_parent(container_selector, 0, button_text)
        
        if not button_info:
            print("\n⚠️  Кнопка не найдена автоматически")
            print("💡 Введи селектор кнопки вручную:")
            child_selector = input("   CSS селектор кнопки: ").strip()
        else:
            child_selector = f"span[data-e2e*='{button_info['selector']}']"
            print(f"\n✅ Рекомендуемый селектор: {child_selector}")
            use_recommended = input("   Использовать? (y/n): ").strip().lower() != "n"
            
            if not use_recommended:
                child_selector = input("   CSS селектор кнопки: ").strip()
        
        # Генерация YAML
        step = {
            'action': 'selenium_click',
            'selector': container_selector,
            'index': '{found_index}',
            'parent_selector': '..',
            'child_selector': child_selector,
            'description': f'Кликнуть {button_text}'
        }
        
        print("\n✅ Шаг создан:")
        print(f"   Контейнер: {container_selector}")
        print(f"   Кнопка: {child_selector}")
        
        return step
    
    def _setup_coordinates(self):
        """Настройка selenium_get_coordinates"""
        print("\n" + "="*60)
        print("📍 НАСТРОЙКА ПОЛУЧЕНИЯ КООРДИНАТ")
        print("="*60)
        
        selector = input("\nВведи CSS селектор: ").strip()
        
        if not selector:
            print("❌ Селектор не может быть пустым")
            return None
        
        # Тест
        print(f"\n3️⃣ Тестирование: {selector}")
        results = self.test_selector(selector, show_count=3)
        
        if not results:
            return None
        
        # Параметры
        save_x = input("\n   Сохранить X в переменную (element_x): ").strip() or "element_x"
        save_y = input("   Сохранить Y в переменную (element_y): ").strip() or "element_y"
        
        # Генерация YAML
        step = {
            'action': 'selenium_get_coordinates',
            'selector': selector,
            'index': '{found_index}',
            'save_x': save_x,
            'save_y': save_y,
            'description': f'Получить координаты {selector}'
        }
        
        print("\n✅ Шаг создан:")
        print(f"   Селектор: {selector}")
        print(f"   Координаты: ({save_x}, {save_y})")
        
        return step
    
    def close(self):
        """Закрыть соединение"""
        if self.driver:
            self.driver.quit()
            print("✅ Selenium закрыт")

if __name__ == "__main__":
    # Тест
    helper = SeleniumHelper()
    step = helper.interactive_setup()
    
    if step:
        print("\n" + "="*60)
        print("📋 YAML для конфига:")
        print("="*60)
        import yaml
        print(yaml.dump([step], default_flow_style=False, allow_unicode=True))
    
    helper.close()
