#!/usr/bin/env python3
"""
train_yolo.py
Скрипт для обучения YOLO модели на кастомных данных.
Требует размеченный датасет в формате YOLO.
"""

import os
import sys
from pathlib import Path

try:
    from ultralytics import YOLO
except ImportError:
    print("❌ ultralytics не установлена!")
    print("   Установи: pip install ultralytics")
    sys.exit(1)


def train_model(
    data_yaml="data.yaml",
    model="yolov8n.pt",
    epochs=50,
    imgsz=640,
    batch=16,
    device=None
):
    """
    Обучение YOLO модели
    
    Args:
        data_yaml: путь к конфигурации датасета
        model: базовая модель (yolov8n/s/m/l/x)
        epochs: количество эпох
        imgsz: размер изображения
        batch: размер батча
        device: устройство (cpu/mps/cuda)
    """
    
    print("\n" + "="*60)
    print("🧠 Обучение YOLO модели")
    print("="*60)
    
    # Проверка data.yaml
    if not os.path.exists(data_yaml):
        print(f"\n❌ Файл {data_yaml} не найден!")
        print("\nСоздай data.yaml с содержимым:")
        print("""
train: ./data/images/train
val: ./data/images/val
names: ['button']
nc: 1
        """)
        return
    
    print(f"\n📋 Параметры обучения:")
    print(f"   Датасет: {data_yaml}")
    print(f"   Базовая модель: {model}")
    print(f"   Эпох: {epochs}")
    print(f"   Размер изображения: {imgsz}")
    print(f"   Batch size: {batch}")
    print(f"   Устройство: {device or 'auto'}")
    
    # Автоопределение устройства
    if device is None:
        try:
            import platform
            if platform.processor() == 'arm':
                device = 'mps'  # Apple Silicon
            else:
                device = 'cpu'
        except:
            device = 'cpu'
    
    print(f"   Используется: {device}")
    print("="*60)
    
    input("\nНажми Enter для начала обучения...")
    
    try:
        # Загрузка модели
        print("\n🔄 Загрузка базовой модели...")
        yolo = YOLO(model)
        
        # Обучение
        print("\n🚀 Начинаю обучение...\n")
        results = yolo.train(
            data=data_yaml,
            epochs=epochs,
            imgsz=imgsz,
            batch=batch,
            device=device,
            project="runs/detect",
            name="train",
            exist_ok=True,
            verbose=True
        )
        
        print("\n" + "="*60)
        print("✅ Обучение завершено!")
        print("="*60)
        print(f"\n📁 Результаты сохранены в: runs/detect/train/")
        print(f"   Веса модели: runs/detect/train/weights/best.pt")
        print(f"\n💡 Скопируй модель в проект:")
        print(f"   cp runs/detect/train/weights/best.pt models/best_yolo.pt")
        print(f"\n🚀 Запусти макрос с обученной моделью:")
        print(f"   python macro_ai.py --yolo --device {device}")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Ошибка обучения: {e}")
        import traceback
        traceback.print_exc()


def validate_dataset(data_yaml="data.yaml"):
    """Проверка датасета перед обучением"""
    
    print("\n" + "="*60)
    print("🔍 Проверка датасета")
    print("="*60)
    
    if not os.path.exists(data_yaml):
        print(f"\n❌ Файл {data_yaml} не найден!")
        return False
    
    try:
        import yaml
        with open(data_yaml, 'r') as f:
            config = yaml.safe_load(f)
        
        train_path = config.get('train')
        val_path = config.get('val')
        names = config.get('names', [])
        
        print(f"\n📋 Конфигурация:")
        print(f"   Train: {train_path}")
        print(f"   Val: {val_path}")
        print(f"   Классы: {names}")
        
        # Проверка путей
        train_exists = os.path.exists(train_path) if train_path else False
        val_exists = os.path.exists(val_path) if val_path else False
        
        print(f"\n📁 Проверка путей:")
        print(f"   Train: {'✅' if train_exists else '❌'}")
        print(f"   Val: {'✅' if val_exists else '❌'}")
        
        if train_exists:
            train_images = len(list(Path(train_path).glob('*.jpg'))) + \
                          len(list(Path(train_path).glob('*.png')))
            print(f"   Train изображений: {train_images}")
        
        if val_exists:
            val_images = len(list(Path(val_path).glob('*.jpg'))) + \
                        len(list(Path(val_path).glob('*.png')))
            print(f"   Val изображений: {val_images}")
        
        if train_exists and val_exists:
            print("\n✅ Датасет готов к обучению!")
            return True
        else:
            print("\n❌ Датасет не готов. Проверь пути в data.yaml")
            return False
            
    except Exception as e:
        print(f"\n❌ Ошибка проверки: {e}")
        return False


def main():
    """Главное меню"""
    
    print("\n" + "="*60)
    print("🧠 YOLO Training Helper")
    print("="*60)
    print("\nВыбери действие:")
    print("  1. Проверить датасет")
    print("  2. Обучить модель (быстро - 50 эпох)")
    print("  3. Обучить модель (качественно - 100 эпох)")
    print("  4. Кастомные параметры")
    print("  5. Выход")
    print("="*60)
    
    choice = input("\nТвой выбор (1-5): ").strip()
    
    if choice == "1":
        validate_dataset()
        
    elif choice == "2":
        if validate_dataset():
            train_model(epochs=50, batch=16)
            
    elif choice == "3":
        if validate_dataset():
            train_model(epochs=100, batch=16)
            
    elif choice == "4":
        print("\n📋 Кастомные параметры:")
        data_yaml = input("  data.yaml путь [data.yaml]: ").strip() or "data.yaml"
        model = input("  Базовая модель [yolov8n.pt]: ").strip() or "yolov8n.pt"
        epochs = int(input("  Эпох [50]: ").strip() or "50")
        imgsz = int(input("  Размер изображения [640]: ").strip() or "640")
        batch = int(input("  Batch size [16]: ").strip() or "16")
        device = input("  Устройство [auto]: ").strip() or None
        
        train_model(
            data_yaml=data_yaml,
            model=model,
            epochs=epochs,
            imgsz=imgsz,
            batch=batch,
            device=device
        )
        
    elif choice == "5":
        print("\n👋 До встречи!")
        
    else:
        print("\n❌ Неверный выбор")


if __name__ == "__main__":
    main()
