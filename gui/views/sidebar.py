"""
Sidebar - Левая панель навигации
Содержит навигацию по режимам и статус панель
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QFrame, QButtonGroup, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon
from pathlib import Path

class Sidebar(QWidget):
    """Левая панель с навигацией и статусом"""
    
    # Сигнал для уведомления о смене режима
    mode_changed = Signal(str)
    
    def __init__(self, project_root: Path):
        super().__init__()
        self.project_root = project_root
        self.current_mode = "chat"
        
        self.setup_ui()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Заголовок
        self.create_header(layout)
        
        # Навигация
        self.create_navigation(layout)
        
        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #444444;")
        layout.addWidget(separator)
        
        # Статус панель
        self.create_status_panel(layout)
        
        # Растягивающийся элемент
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
    def create_header(self, layout: QVBoxLayout):
        """Создание заголовка"""
        
        header_label = QLabel("🚀 MACRO AI")
        header_label.setFont(QFont("Arial", 14, QFont.Bold))
        header_label.setStyleSheet("color: #60A5FA; margin-bottom: 5px;")
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header_label)
        
        subtitle_label = QLabel("Автоматизация macOS")
        subtitle_label.setFont(QFont("Arial", 10))
        subtitle_label.setStyleSheet("color: #A0A0A0; margin-bottom: 10px;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle_label)
        
    def create_navigation(self, layout: QVBoxLayout):
        """Создание навигационных кнопок"""
        
        nav_label = QLabel("📁 НАВИГАЦИЯ")
        nav_label.setFont(QFont("Arial", 10, QFont.Bold))
        nav_label.setStyleSheet("color: #E0E0E0; margin-bottom: 5px;")
        layout.addWidget(nav_label)
        
        # Группа кнопок для эксклюзивного выбора
        self.button_group = QButtonGroup(self)
        
        # Кнопки навигации
        nav_buttons = [
            ("chat", "🤖 Генерация", "Основной режим - чат с AI"),
            ("prompts", "📋 Промпты", "Просмотр системных промптов"),
            ("dsl", "📝 DSL", "Управление DSL переменными"),
            ("architecture", "🏗️ Архитектура", "Управление структурой шаблонов")
        ]
        
        for mode, text, tooltip in nav_buttons:
            button = self.create_nav_button(mode, text, tooltip)
            layout.addWidget(button)
            self.button_group.addButton(button)
            
        # Активируем первую кнопку по умолчанию
        self.button_group.buttons()[0].setChecked(True)
        
    def create_nav_button(self, mode: str, text: str, tooltip: str) -> QPushButton:
        """Создание навигационной кнопки"""
        
        button = QPushButton(text)
        button.setCheckable(True)
        button.setToolTip(tooltip)
        button.setMinimumHeight(40)
        
        # Стилизация кнопки
        button.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 8px 12px;
                border: 1px solid #444444;
                border-radius: 6px;
                background-color: #2D2D2D;
                color: #E0E0E0;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3D3D3D;
                border-color: #60A5FA;
            }
            QPushButton:checked {
                background-color: #60A5FA;
                color: #FFFFFF;
                border-color: #60A5FA;
            }
        """)
        
        # Подключение сигнала
        button.clicked.connect(lambda: self.on_nav_button_clicked(mode))
        
        return button
        
    def create_status_panel(self, layout: QVBoxLayout):
        """Создание панели статуса"""
        
        status_label = QLabel("📊 СТАТУС")
        status_label.setFont(QFont("Arial", 10, QFont.Bold))
        status_label.setStyleSheet("color: #E0E0E0; margin-bottom: 5px;")
        layout.addWidget(status_label)
        
        # Статус API
        self.api_status = QLabel("✅ Gemini: OK")
        self.api_status.setStyleSheet("color: #10B981; font-size: 11px;")
        layout.addWidget(self.api_status)
        
        # Количество шаблонов
        self.templates_count = QLabel("📄 Шаблонов: ...")
        self.templates_count.setStyleSheet("color: #A0A0A0; font-size: 11px;")
        layout.addWidget(self.templates_count)
        
        # Количество DSL переменных
        self.dsl_count = QLabel("🎯 DSL переменных: ...")
        self.dsl_count.setStyleSheet("color: #A0A0A0; font-size: 11px;")
        layout.addWidget(self.dsl_count)
        
        # Обновляем статус
        self.update_status()
        
    def on_nav_button_clicked(self, mode: str):
        """Обработка клика по навигационной кнопке"""
        if mode != self.current_mode:
            self.current_mode = mode
            self.mode_changed.emit(mode)
            
    def update_status(self):
        """Обновление статуса панели"""
        try:
            # Проверка API статуса
            from src.utils.api_config import api_config
            
            if api_config.has_gemini():
                model = api_config.gemini_model
                self.api_status.setText(f"✅ Gemini: {model}")
                self.api_status.setStyleSheet("color: #10B981; font-size: 11px;")
            else:
                self.api_status.setText("❌ Gemini: Не настроен")
                self.api_status.setStyleSheet("color: #EF4444; font-size: 11px;")
                
            # Подсчет шаблонов
            templates_dir = self.project_root / "templates"
            if templates_dir.exists():
                png_files = list(templates_dir.rglob("*.png"))
                self.templates_count.setText(f"📄 Шаблонов: {len(png_files)}")
            
            # Подсчет DSL переменных
            dsl_file = self.project_root / "templates" / "DSL_VARIABLES.txt"
            if dsl_file.exists():
                with open(dsl_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Простой подсчет переменных (строки с ${})
                    import re
                    variables = re.findall(r'\$\{[^}]+\}', content)
                    unique_vars = len(set(variables))
                    self.dsl_count.setText(f"🎯 DSL переменных: {unique_vars}")
                    
        except Exception as e:
            print(f"⚠️ Ошибка обновления статуса: {e}")
            self.api_status.setText("❓ Статус неизвестен")
            self.api_status.setStyleSheet("color: #F59E0B; font-size: 11px;")
