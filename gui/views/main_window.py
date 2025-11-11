"""
Main Window - Главное окно приложения
Основное окно с двухпанельным интерфейсом
"""

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
    QSplitter, QLabel, QFrame, QPushButton, QStatusBar
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon
from pathlib import Path

from .sidebar import Sidebar
from .chat_widget import ChatWidget
from .prompts_widget import PromptsWidget
from .dsl_widget import DSLWidget

class MainWindow(QMainWindow):
    """Главное окно приложения"""
    
    def __init__(self, project_root: Path):
        super().__init__()
        self.project_root = project_root
        
        self.setup_ui()
        self.setup_window()
        
    def setup_window(self):
        """Настройка окна"""
        self.setWindowTitle("🚀 Macro AI Master")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Центрирование окна
        screen = self.screen().availableGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        
        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основной layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Создание сплиттера для разделения панелей
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(splitter)
        
        # Левая панель (Sidebar)
        self.sidebar = Sidebar(self.project_root)
        self.sidebar.setMaximumWidth(300)
        self.sidebar.setMinimumWidth(250)
        splitter.addWidget(self.sidebar)
        
        # Правая панель (Main Content)
        self.content_area = self.create_content_area()
        splitter.addWidget(self.content_area)
        
        # Настройка пропорций сплиттера
        splitter.setSizes([300, 1100])  # 300px для sidebar, остальное для контента
        
        # Подключение сигналов
        self.sidebar.mode_changed.connect(self.on_mode_changed)
        
        # Статус бар
        self.setup_status_bar()
        
    def create_content_area(self) -> QWidget:
        """Создание области контента (правая панель)"""
        
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(10, 10, 10, 10)
        
        # Заголовок области
        self.content_title = QLabel("💬 Чат с AI")
        self.content_title.setFont(QFont("Arial", 16, QFont.Bold))
        self.content_title.setStyleSheet("color: #60A5FA; margin-bottom: 10px;")
        content_layout.addWidget(self.content_title)
        
        # Создаем виджеты для разных режимов
        self.chat_widget = ChatWidget(self.project_root)
        self.prompts_widget = PromptsWidget(self.project_root)
        self.dsl_widget = DSLWidget(self.project_root)
        
        # Сохраняем ссылку на layout для переключения
        self.content_layout = content_layout
        
        # По умолчанию показываем чат
        self.current_widget = self.chat_widget
        content_layout.addWidget(self.current_widget)
        
        return content_widget
        
    def setup_status_bar(self):
        """Настройка статус бара"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Статус готовности
        self.status_label = QLabel("✅ Готов к работе")
        status_bar.addWidget(self.status_label)
        
        # Информация о проекте
        project_info = QLabel(f"📁 {self.project_root.name}")
        status_bar.addPermanentWidget(project_info)
        
    def on_mode_changed(self, mode: str):
        """Обработка смены режима в sidebar"""
        print(f"🔄 Переключение на режим: {mode}")
        
        # Обновление заголовка
        mode_titles = {
            "chat": "💬 Чат с AI",
            "prompts": "📋 Промпты системы",
            "dsl": "📝 DSL Переменные", 
            "architecture": "🏗️ Архитектура шаблонов"
        }
        
        self.content_title.setText(mode_titles.get(mode, "❓ Неизвестный режим"))
        
        # Переключение виджетов контента
        self._switch_content_widget(mode)
        
        # Обновление статуса
        if mode == "chat":
            self.status_label.setText("✅ Режим чата активен")
        elif mode == "prompts":
            self.status_label.setText("📋 Просмотр промптов")
        elif mode == "dsl":
            self.status_label.setText("📝 Управление DSL переменными")
        elif mode == "architecture":
            self.status_label.setText("🏗️ Управление архитектурой")
    
    def _switch_content_widget(self, mode: str):
        """Переключение виджета контента"""
        
        # Удаляем текущий виджет из layout
        if self.current_widget:
            self.content_layout.removeWidget(self.current_widget)
            self.current_widget.hide()
        
        # Выбираем новый виджет
        if mode == "chat":
            self.current_widget = self.chat_widget
        elif mode == "prompts":
            self.current_widget = self.prompts_widget
        elif mode == "dsl":
            self.current_widget = self.dsl_widget
        elif mode == "architecture":
            # TODO: Создать ArchitectureWidget  
            self.current_widget = self.chat_widget  # Временно показываем чат
        else:
            self.current_widget = self.chat_widget
        
        # Добавляем новый виджет в layout
        self.content_layout.addWidget(self.current_widget)
        self.current_widget.show()
            
    def closeEvent(self, event):
        """Обработка закрытия окна"""
        print("👋 Закрытие Macro AI GUI")
        event.accept()
