#!/usr/bin/env python3
"""
Atlas Runner - Запуск .atlas файлов
Простой интерпретатор для выполнения макросов из .atlas файлов
"""

import sys
import time
import subprocess
from pathlib import Path
import pyautogui
import pyperclip

def parse_atlas_file(file_path: Path) -> list:
    """Парсинг .atlas файла и извлечение команд макроса"""
    
    if not file_path.exists():
        raise FileNotFoundError(f"Файл {file_path} не найден")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Извлекаем секцию с кодом макроса
    lines = content.split('\n')
    commands = []
    in_macro_section = False
    
    for line in lines:
        line = line.strip()
        
        # Начало секции макроса
        if line == "# MACRO CODE" or "**Код макроса:**" in line:
            in_macro_section = True
            continue
        
        # Конец секции макроса (следующая секция с #====)
        if line.startswith("# ============") and in_macro_section and "METADATA" in line:
            break
        
        # Если мы в секции макроса
        if in_macro_section:
            # Пропускаем пустые строки, комментарии и разделители
            if (not line or 
                line.startswith('#') or 
                line.startswith('```') or
                line.startswith('**') or
                line.startswith('✅') or
                line.startswith('Используйте')):
                continue
            
            # Добавляем команду
            commands.append(line)
    
    return commandstesttest

def execute_command(command: str) -> bool:
    """Выполнение одной команды макроса"""
    
    parts = command.split()
    if not parts:
        return True
    
    cmd = parts[0].lower()
    
    try:
        if cmd == "open":
            if len(parts) > 1:
                app_name = parts[1]
                print(f"🚀 Открываю {app_name}")
                # Простая реализация - открытие через spotlight
                pyautogui.hotkey('cmd', 'space')
                time.sleep(0.5)
                pyautogui.write(app_name.replace('App', ''))
                pyautogui.press('enter')
            return True
            
        elif cmd == "wait":
            if len(parts) > 1:
                duration = float(parts[1].replace('s', ''))
                print(f"⏳ Ожидание {duration}с")
                time.sleep(duration)
            return True
            
        elif cmd == "click":
            if len(parts) > 1:
                element = parts[1]
                print(f"👆 Клик по {element}")
                # Простая реализация - клик в центр экрана
                # В реальной версии здесь был бы поиск шаблона
                screen_width, screen_height = pyautogui.size()
                pyautogui.click(screen_width // 2, screen_height // 2)
            return True
            
        elif cmd == "type":
            if len(parts) > 1:
                text = ' '.join(parts[1:]).strip('"\'')
                print(f"⌨️  Ввод: {text}")
                pyautogui.write(text)
            return True
            
        elif cmd == "press":
            if len(parts) > 1:
                key = parts[1]
                print(f"🔘 Нажатие: {key}")
                pyautogui.press(key)
            return True
            
        elif cmd == "repeat":
            print(f"🔄 Команда repeat пока не поддерживается")
            return True
            
        else:
            print(f"⚠️  Неизвестная команда: {command}")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка выполнения команды '{command}': {e}")
        return False

def run_atlas_file(file_path: Path) -> bool:
    """Запуск .atlas файла"""
    
    try:
        print(f"🎯 Запуск макроса: {file_path.name}")
        print("=" * 50)
        
        # Парсим файл
        commands = parse_atlas_file(file_path)
        
        if not commands:
            print("⚠️  В файле не найдены команды для выполнения")
            return False
        
        print(f"📋 Найдено команд: {len(commands)}")
        print()
        
        # Небольшая задержка перед началом
        print("🚀 Начинаю выполнение через 2 секунды...")
        time.sleep(2)
        
        # Выполняем команды
        for i, command in enumerate(commands, 1):
            print(f"[{i}/{len(commands)}] {command}")
            
            success = execute_command(command)
            if not success:
                print(f"❌ Ошибка на команде {i}: {command}")
                return False
            
            # Небольшая пауза между командами
            time.sleep(0.1)
        
        print()
        print("✅ Макрос выполнен успешно!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка запуска макроса: {e}")
        return False

def main():
    """Главная функция"""
    
    if len(sys.argv) != 2:
        print("Использование: python3 atlas_runner.py <путь_к_atlas_файлу>")
        sys.exit(1)
    
    file_path = Path(sys.argv[1])
    
    if not file_path.exists():
        print(f"❌ Файл не найден: {file_path}")
        sys.exit(1)
    
    if not file_path.suffix == '.atlas':
        print(f"❌ Неверное расширение файла. Ожидается .atlas, получен: {file_path.suffix}")
        sys.exit(1)
    
    # Запускаем макрос
    success = run_atlas_file(file_path)
    
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
