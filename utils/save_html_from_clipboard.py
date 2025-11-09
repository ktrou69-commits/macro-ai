#!/usr/bin/env python3
"""
save_html_from_clipboard.py
Быстрое сохранение HTML из буфера обмена в файл

Использование:
1. Скопировать HTML (Copy element в F12)
2. Запустить: python3 save_html_from_clipboard.py
3. HTML сохранится в /tmp/element.html
"""

import pyperclip
from pathlib import Path

def main():
    print("📋 Сохранение HTML из буфера обмена")
    print("="*80)
    
    # Получаем HTML из буфера
    try:
        html = pyperclip.paste()
    except Exception as e:
        print(f"❌ Ошибка чтения буфера: {e}")
        print("   Установите: pip install pyperclip")
        return
    
    if not html:
        print("❌ Буфер обмена пуст")
        return
    
    # Сохраняем в файл
    output_file = Path("/tmp/element.html")
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ HTML сохранен: {output_file}")
        print(f"📊 Размер: {len(html)} символов")
        print(f"\n💡 Используйте в инструменте:")
        print(f"   Путь к файлу: {output_file}")
        
    except Exception as e:
        print(f"❌ Ошибка сохранения: {e}")

if __name__ == "__main__":
    main()
