#!/usr/bin/env python3
"""
GUI Main Entry Point - Macro AI Master
Главная точка входа для графического интерфейса
"""

import sys
import os
from pathlib import Path

# Добавляем корень проекта в путь для импорта существующих модулей
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Импорты PySide6
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

# Импорты GUI
from views.main_window import MainWindow

def setup_app_style(app: QApplication):
    """Настройка стиля приложения"""
    try:
        import qdarkstyle
        app.setStyleSheet(qdarkstyle.load_stylesheet_pyside6())
        print("✅ Темная тема загружена")
    except ImportError:
        print("⚠️  QDarkStyle не установлен, используется системная тема")
        # Базовая темная тема
        app.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
        """)

def main():
    """Главная функция запуска GUI приложения"""
    
    # Создание приложения
    app = QApplication(sys.argv)
    
    # Настройка приложения
    app.setApplicationName("Macro AI Master")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Macro AI")
    
    # Настройка стиля
    setup_app_style(app)
    
    # Создание главного окна
    try:
        window = MainWindow(project_root)
        window.show()
        
        print("🚀 Macro AI GUI запущен!")
        print(f"📁 Проект: {project_root}")
        
    except Exception as e:
        print(f"❌ Ошибка запуска: {e}")
        return 1
    
    # Запуск цикла событий
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
