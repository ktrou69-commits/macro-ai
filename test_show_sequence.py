#!/usr/bin/env python3
"""
Тест отображения последовательности с координатами
"""
import yaml
from pathlib import Path

# Загрузка конфига
with open('my_sequences.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# Получение последовательности '1'
sequence = config['sequences']['1']
steps = sequence['steps']

print("\n" + "="*60)
print(f"📋 Текущая последовательность: {len(steps)} шагов")
print("="*60)

for i, step in enumerate(steps, 1):
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

print("\n✅ Тест пройден успешно!")
